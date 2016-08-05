#!/home/mro/Ureka/variants/common/bin/python
"""
Add_headers is a python program that adds all sorts of useful information to the FITS headers of images taken at MRO. If you have logfiles produced by the GTCC, add_headers will read them and save pointing information to the headers.

Add_headers continuously looks for new images in the directory specified by -s. For each one, it:

* Searches for the right GTCC log, and if it finds one,
** writes RA, DEC, EPOCH, ST, HA, ZD to header, and
** calculates AIRMASS and JD (through iraf setairmass and setjd).
* Saves the image into the current directory on geezil
* Displays it in ds9.
* Asks you  the object's name and writes that information into the header

Oliver Fraser

Versions
0.5  initial version (OJF)
0.8  fixed bug in findlogfile, I assumed (incorrectly) that I'd get logfiles in
     order. (OJF)
0.9  Converted from pyfits to iraf.hedit and shutil.copy.
     We found that pyfits will change the data type in the data section of the
     image from Int32 to Float -- probably because Andor doesn't write out perfectly
     standard FITS files. This conversion seemed to lose some data, so instead we'll
     use IRAF. In the IRAF specific stuff 'Stdout=True' is to stop hedit from
     writing stuff to the screen. (OJF)
0.91 Display image, *then* ask for information (OJF)
0.92 Converted back to pyfits (for speed and easy maintenance).
     Minor UI changes. (OJF)
1.0  Dropped filter slide keyword, added airmass and specifying the source via -s.
     Updated documentation a lot (OJF)
1.1  Updated directory paths for Geezil install, and commented out the airmass.
     Updated documentation. (OJF)
2.0  Removed accessing the filter info from gtcc since it the filter is no longer
     ran from there. Added a manual input for the filter. Created a night log with
     image: time, name, type, ra, dec, exptime, filter, airmass(or sec(z)). Use
     iraf to set airmass and jd header keywords (Jean McKeever)
3.6  Can now read and process files produced by by both Spyder and Kia, 
     removed night log, replaced FitsIO with astropy.io.fits, and now use
     os.path.basename. (Amelia Brown & Oliver Fraser)
3.7  updated how we set header values, supress warnings from astropy, bug fixes
4.0  modify/strip out code to work w/ Evora.
"""

from optparse import OptionParser
import glob # for getting files that match a pattern
import time
import numpy
#import pyfits # for dealing with fits files
import astropy.utils.exceptions
import astropy.io.fits as pyfits
import readline
import sys
import os.path
from pyraf import iraf
import warnings

__version__ = "4.1"

defaults = {'source_dir': '/home/mro/data/raw',
            'new_source_dir': False,
            'destination_dir': '.',
            'logfile_dir': '/mnt/gtcc',
            'ask_for_object_name': False,
            'sleep': 1,
            'ds9': False,
            'once': False,
            'quiet': False,
            'DEBUG': False
            }

def ChooseLogfile( LogfileList, ObsTime, options ):
    """
    Choose the right logfile for the time of the observation,
    The logfiles are named according to their creation date, but they don't
    necessarilly come though in order. We'll return the name of the last
    one made before the exposure.
    """
    nlogs = len(LogfileList)
    ObsTime = time.mktime(ObsTime) # convert to float representation
    besttime = -ObsTime # set a start time way in the past
    bestindex = 0
    for i in range(nlogs):
        # make a time from the logfile name
        LogfileTime = time.mktime(
            time.strptime(                     
              os.path.basename( LogfileList[i] )
              +' UTC', "%Y-%m-%dT%H:%M:%S %Z" # this is the format
            )
          )
        # what's the delta between this and the observation
        delTime = LogfileTime - ObsTime
        if options.DEBUG:
            print LogfileList[i], delTime, besttime
        # choose the largest negative delLogfileTime as the right logfile
        # that is, the closest negative number to zero
        if delTime > besttime and delTime < 0:
            besttime = delTime
            bestindex = i
    # whew! finally got the logfile we want
    return LogfileList[bestindex]


def ParseLogfile(LogfileName, ObsTime, options):
    """
    Find the line in the logfile closest in time to the observation,
    parse it, and return it.
    Logfile format is:

    UTDate&Time RA Dec Epoch LST Hour-angle Zenith-angle fslide:position

    We treat everything as a string.
    """
    if options.DEBUG:
        print "opening logfile",LogfileName
    Log = open(LogfileName)
    # now we need to find the smallest time increment between
    # Obstime and the time recorded on each line of the logfile
    # we'll read each line in, then compare
    data = Log.readline().split() 
    Time = time.strptime(data[0]+' UTC', "%Y-%m-%dT%H:%M:%S %Z")
    delTime = abs( time.mktime(Time) - time.mktime(ObsTime) )
    # move through and compare each line of the logfile
    if options.DEBUG:
        print time.asctime(Time), delTime
    for newline in Log:    
        newdata = newline.split()
        newTime = time.strptime( newdata[0]+' UTC', "%Y-%m-%dT%H:%M:%S %Z" )
        newdelTime = abs( time.mktime(newTime) - time.mktime(ObsTime) )
        # this newdelTime should be smaller than delTime
        # since we should be moving closer to the right line.
        # if it's not, then we've gone too far
        if options.DEBUG:
            print time.asctime(newTime), newdelTime
        if newdelTime > delTime:
            if options.DEBUG:
                print "that last one is *too* far"
            break
        delTime = newdelTime
        data = newdata
    #filter = data[7].rsplit(':',1)[1] # pull out just the filter number
    return data[1], data[2], data[3], data[4], data[5], data[6]#, filter


usage = """%prog [options] source_dir\n  source_dir is a subdirectory of ~/data/raw on Loki. To override this behavior use the -s command line option. The wiki has more documentation, examples, and hints."""

parser = OptionParser(usage=usage, version="%prog "+__version__)
parser.add_option("-s", "--source", dest = "new_source_dir",
                  default = defaults['new_source_dir'],
                  help = "Source of raw images--overrides any command line argument"
                  )
parser.add_option("-d", "--destination", dest = "destination_dir",
                  default = defaults['destination_dir'],
                  help = "Destination for saving images, defaults to '"+defaults['destination_dir']+"'"
                  )
parser.add_option("-l", "--logs", dest = "logfile_dir",
                  default = defaults['logfile_dir'],
                  help = "Location of logfiles, defaults to '"+defaults['logfile_dir']+"'."
                  )
parser.add_option("--ask_for_object_name", action = "store_true", dest = "ask_for_object_name",
                  default = defaults['ask_for_object_name'],
                  help = "Ask for the object name."
                  )
parser.add_option("--sleep", dest = "sleep",
                 default = defaults['sleep'],
                 help = "Time to wait between checking for new files, defaults to "+str(defaults['sleep'])+" second."
                 )
parser.add_option("--ds9", action = "store_true",
                 default = defaults['ds9'],
                 help = "Automatically display images in ds9."
                 )
parser.add_option("--once", action = "store_true",
                  default = defaults['once'],
                  help = "Just run once, don't keep checking for new files."
                  )
parser.add_option("-q", "--quiet", action = "store_true",
                  default = defaults['quiet'],
		  help = "Suppress printing extra information to the screen."
                  )
parser.add_option("--DEBUG", action = "store_true",
                  default = defaults['DEBUG'],
                  help = "Print out extra information that'll help you debug."
                  )
options, args = parser.parse_args()

# setup some convenience variables
ds9 = options.ds9
verbose = not options.quiet
if options.ask_for_object_name:
    verbose = True
imtype = 'bias'
object_name = ''
filter='g'
iraf.noao.astutil(_doprint=0)
Spyder = False
warnings.filterwarnings('ignore', category=astropy.utils.exceptions.AstropyUserWarning)

# choose the source dir
source_dir = defaults['source_dir']
if len(args) > 0:
    data_dir=args[0]
    source_dir = source_dir + '/' + data_dir
if options.new_source_dir: # override anything on the command line
    source_dir = options.new_source_dir
if not os.path.exists(source_dir):
    print "Error:", source_dir, "doesn't exist!"
    print "Aborting..."
    sys.exit(1)

# here we go!    
if verbose:
    print "Ready to grab files from", source_dir
while ( True==True ):
    """ We need to figure out which files are in the source dir that 
    aren't in the destination dir. To do this we'll start by reading
    in all the filenames that are pertinent."""
    # a list of *fit files already in the destination directory
    DestFileList = glob.glob(options.destination_dir+'/*.fit*')
    # extract just the names of those files (for comparison purposes)
    DestFileNames = [ os.path.basename(file) for file in DestFileList ]
    # all the logfiles
    LogfileList = glob.glob(options.logfile_dir+'/????-??-??T??:??:??')
    # a list of *.fit files in the source directory
    SourceFileList = glob.glob(source_dir+'/*.[fF][iI][tT]*')
    if options.DEBUG:
        print "Source files in", source_dir, ":", SourceFileList
        print "Dest files in", options.destination_dir, ":", DestFileNames 
        print "Log files in", options.logfile_dir, ":", LogfileList
	      
    for file in SourceFileList:
        # Grab just the name of the file (for comparison purposes)
        FileName = os.path.basename( file )
        if "FIT" in FileName:
            FileName = FileName.replace("FIT", "fit")
        # if it already exists in the destination, skip it
        if FileName in DestFileNames:
            continue
        print FileName
        ## Read the file and get the date
        try:
            ImageData, ImageHdr = pyfits.getdata(file, 0, header=True, ignore_missing_end=True)
        except: # the file isn't complete, skip it!
            #Image.close()
            if options.DEBUG:
                print "Skipping truncated file:", FileName
            continue
        try:
            if ImageHdr['HEAD']=="DV434":
		Spyder = True
            if options.DEBUG:
		print "recognized", FileName, "is from Spyder."
            DateObs = ImageHdr['date'] # DateObs is a string representing the UT time
	except:
            Spyder = False
            if options.DEBUG:
		print FileName, "is not from Spyder."
            DateObs = ImageHdr['DATE-OBS'] # DateObs is a string representing the UT time
        # convert DateObs to a python struct_time
        ObsTime = time.strptime(DateObs+' UTC', "%Y-%m-%dT%H:%M:%S %Z")
        if options.DEBUG:
            print FileName, "was taken on", time.asctime(ObsTime), time.mktime(ObsTime)
        if Spyder == True:
            ## Write the extra headers out to the new file
            ImageHdr['DATE-OBS'] = (DateObs, "Time at start of exposure")
       	    ImageHdr['UT'] = (time.strftime("%H:%M:%S",ObsTime), "UT time at start of exposure")
            
        ## Check for logfiles and write headers if we can
        if len(LogfileList) == 0:
        	print "No logfiles found."
        else:
            try:
                LogfileName = ChooseLogfile(LogfileList, ObsTime, options)
                ra, dec, epoch, lst, ha, za = ParseLogfile(LogfileName, ObsTime, options)
            except Exception, error:
                if options.DEBUG:
                    print "Oops -- messed up reading the logfile. Please rerun with '--DEBUG --once' and send the output to Oliver."
                    print error
            else:   # only executed if we found a logfile
                ImageHdr['RA'] = (ra, "Right Ascension")
                ImageHdr['DEC'] = (dec, "Declination")
                ImageHdr['EPOCH'] = (epoch, "Epoch for RA and Dec (years)")
                ImageHdr['ST'] = (lst, "local sidereal time (hours)")
                ImageHdr['HA'] = (ha, "Hour Angle")
                ImageHdr['ZD'] = (za, "Zenith Angle")
                #ImageHdr['AIRMASS'] = (1./numpy.cosine(float(za)), "secant(Z)")
        newfile = options.destination_dir+"/"+FileName
        try:
            #pyfits.writeto(newfile, ImageData, ImageHdr, output_verify = "silentfix")
            pyfits.writeto(newfile, ImageData, ImageHdr, output_verify = "ignore")
        except IOError, error:
            print "Error: Can't save output file:", error
            print "Aborting..."
            sys.exit(1)

        ## Set air mass and jd
        iraf.noao.astutil.setairmass (options.destination_dir+'/'+FileName, observatory=")_.observatory", intype="beginning", outtype="effective", ra="ra", dec="dec", equinox="epoch", st="st", ut="ut", date="date-obs", exposure="exposure", airmass="airmass", utmiddle="utmiddle", scale=750., show='yes', update='yes', override='yes')
        iraf.noao.astutil.setjd (options.destination_dir+'/'+FileName, observatory=")_.observatory", date="date-obs", time="ut", exposure="exposure", ra="ra", dec="dec", epoch="epoch", jd="jd", hjd="hjd", ljd="ljd", utdate='yes', uttime='yes', listonly='no')
        
        ## Display the image
        if ds9:
            iraf.display(newfile,zscale=True)
        if Spyder:
            # add imtype 
            Image = pyfits.open(newfile, mode='update')
            ImageHdr = Image[0].header
            tmp = raw_input( "image type (obj:bias:flat) [%s]: " % (imtype,) )
            # a null input means use the last entered value
            if tmp != '':
                # use the first letter to make sure it's one of these three choices:
                if tmp[0].lower() == 'o':
                    imtype = 'object'
                elif tmp[0].lower() == 'b':
                    imtype = 'bias'
                elif tmp[0].lower() == 'f':
                    imtype = 'flat'
            ImageHdr['IMAGETYP'] = imtype
            tmp = raw_input("filter name [%s]: " % (filter,) )
            # a null input means use the last entered value
            if tmp != '':
                filter = tmp
            ImageHdr['FILTER'] = filter
            Image.flush() # save changes
        if options.ask_for_object_name:
            Image = pyfits.open(newfile, mode='update')
            ImageHdr = Image[0].header
            tmp = raw_input("object name [%s]: " % (object_name,) )
            # a null input means use the last entered value
            if tmp != '':
                object_name = tmp
            ImageHdr['OBJECT'] = object_name
            Image.flush() # save these changes too!

        print '\n\n\n'           
            
    if options.once:
        break
    time.sleep(options.sleep)
