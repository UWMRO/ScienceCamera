import os
import datetime
import numpy as np
from astropy.io import fits
import MyLogger

logger = MyLogger.myLogger("fits_utils.py", "client")


def getdata(path):
    """
    This function will open a FITS file, return the data as a 2x2 numpy array
    """
    return fits.getdata(path)


def calcstats(data):
    """
    This function calculates the standard statistics of a FITS image of min,
    max, mean, and median. A list of these stats is returned so that these
    stats can then be displayed at the bottom of the image GUI window.
    """
    stats_list = []
    stats_list.append(min(data.flat))
    stats_list.append(max(data.flat))
    stats_list.append(np.mean(data.flat))
    stats_list.append(np.median(data.flat))
    return stats_list


def check_for_file(path):
    """
    Pre: User specifies a path to a file.
    Post: This method returns true if the file exists
    """
    boolean = os.path.isfile(path)
    return boolean


def get_image_path(type):
    """
    Pre: No inputs.
    Post: Returns the file path /data/forTCC/ plus an image name with a time
    stamp with accuracy of milliseconds.
    """
    saveDirectory = "/home/mro/storage/evora_data/"
    time = datetime.today()
    fileName = time.strftime("image_%Y%m%d_%H%M%S_%f.fits")
    if(type == 'real'):
        return "/home/mro/storage/evora_data/tmp/" + fileName
    else:
        return saveDirectory + fileName


def check_image_counter(name):
    """
    Note: This method is only ever entered if there actually is a name as well
    as there will never be a .fits at the end.
    Pre: Takes in an image name as a string and sees if the standard iterator
    is on the end of the image name.
    Post: Returns a boolean of whether the standard iterator is on the end of
    the image name.  That standard format follows like *_XXX.fits where XXX
    goes from 001 an up.
    """
    if "_" in name:
        name.split("_")
        if (name[-1]).isdigit():
            return True
        else:
            return False
    else:
        return False


def iterate_image_counter(name):
    """
    Note: This method is only invoked if the current image name has been
    checked to have a counter.
    Pre: Takes in an image name with a counter.
    Post: Gets the counter and iterates it, and then is used to change
    self.currentImage to have an iterated count string in the standard format.
    """
    temp = name.split('_')
    count = int(temp[-1])
    logger.debug(str(count))
    count += 1
    if(count < 10):
        temp[-1] = "00" + str(count)
    elif(count < 100):
        temp[-1] = "0" + str(count)
    else:
        temp[-1] = str(count)
    name = "_".join(temp[:])
    logger.debug("Iterated to: " + name)
    return name
