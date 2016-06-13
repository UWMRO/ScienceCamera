#!/usr/bin/python2

from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import sys
import andor
import numpy as np
from astropy.io import fits
import time
import Queue
import thread
import threading
import AddLinearSpacer as als


from twisted.protocols import basic
from twisted.internet import protocol, reactor, threads

# For filter controls
#from FilterMotor import filtermotor

# port for evora is 5502

# Global Variables
acquired = None
t = None
isAborted = None  # tracks globally when the abort has been called.  Every call to the parser
                  # is an new instance


class EvoraServer(basic.LineReceiver):
    def connectionMade(self):
        """
        If you send more than one line then the callback to start the gui will completely fail.
        """
        self.factory.clients.append(self)
        #self.sendMessage("Welcome to the Evora Server")
        #self.sendMessage("Starting camera")
        ep = EvoraParser(self)
        command = ep.parse("status") 
        self.sendMessage(str(command)) # activate the callback to give full control to the camera.

    def connectionLost(self, reason):
        #self.sendLine("Connection Lost")
        #if len(self.factory.clients) is 1:
        #    ep = EvoraParser()
        #    command = ep.parse("shutdown")
            #self.sendMessage(command)        
        self.factory.clients.remove(self)

    def lineReceived(self, line):
        print("received", line)
        ep = EvoraParser(self)
        d = threads.deferToThread(ep.parse, line)
        d.addCallback(self.sendData)

    def sendData(self, data):
        if data is not None:
            self.sendMessage(str(data))

    def sendMessage(self, message):
        for client in self.factory.clients:
            client.sendLine(message)


class EvoraClient(protocol.ServerFactory):
    protocol = EvoraServer
    clients = []

## Evora Parser commands sent here from server where it envokes the camera commands.
class EvoraParser(object):
    def __init__(self, protocol):
        self.e = Evora()
        self.protocol = protocol

    def parse(self, input=None):
        print(input)
        input = input.split()
        if input[0] == 'connect':
            return self.e.startup()
        if input[0] == 'temp':
            return self.e.getTemp()
        if input[0] == 'setTEC':
            return self.e.setTEC(input[1])
        if input[0] == 'getTEC':
            return self.e.getTEC()
        if input[0] == 'warmup':
            return self.e.warmup()
        if input[0] == 'shutdown':
            return self.e.shutdown()
        if input[0] == "status":
            return self.e.getStatus()
        if input[0] == "timings":
            return self.e.getTimings()
        if input[0] == "vertStats":
            return self.e.verticalSpeedStats(int(input[1]))
        if input[0] == 'filterConnect':
            pass
        if input[0] == 'filterSlew':
            # pos can be a number 1-6
            pos = input[1]
            pass
        if input[0] == 'filterHome':
            # simply slews the filter to home
            pass
        if input[0] == "abort":
            return self.e.abort()
        if input[0] == 'expose':
            # command expose flat 1 10 2
            # get the type of exposure (i.e. bias, flat, object)
            imType = input[1]
            print(imType)
            # exposure attributes
            expnum = int(input[2])
            itime = float(input[3])  # why int?
            binning = int(input[4])
            return self.e.expose(imType, expnum, itime, binning)
        if input[0] == 'real':
            # command real flat 1 10 2
            imType = input[1]
            print(imType)
            # exposure attributes
            expnum = int(input[2])  # don't need this
            itime = float(input[3])
            binning = int(input[4])
            return self.e.realTimeExposure(self.protocol, imType, itime, binning)
        if input[0] == 'series':
            # series bias 1 10 2
            imType = input[1]
            print(imType)
            # exposure attributes
            expnum = int(input[2])
            itime = float(input[3])
            binning = int(input[4])
            return self.e.kseriesExposure(self.protocol, imType, itime, numexp=expnum, binning=binning)
        """
        if input[0] == 'realTest':
            #exposureSetting = int(input[1])
            imType = input[1]
            print(imType)
            # exposure attributes
            expnum = int(input[2]) # don't need this
            itime = float(input[3])
            binning = int(input[4])
            return self.e.realTimeExposure_test(self.protocol, imType, itime, binning)

        # This is a deprecated function for series exposure.  It utilizes run till abort, e.g. real time, and will
        # self abort when a counter has reached the user specified number of exposures.
        if input[0] == 'series_tillAbort':
            #exposureSetting = int(input[1])
            imType = input[1]
            print(imType)
            # exposure attributes
            expnum = int(input[2])
            itime = float(input[3])
            binning = int(input[4])
            return self.e.seriesExposure(self.protocol, imType, itime, expnum, binning)
        """


class Evora(object):

    def __init__(self):
        self.num = 0

    def getStatus(self):
        # if the first status[0] is 20075 then the camera is not initialized yet and
        # one needs to run the startup methodg.
        status = andor.GetStatus()
        return "status " + str(status[0]) + "," + str(status[1])

    def startup(self):
	"""
        20002 is the magic number.  Any different number and it didn't work.
        """
        print(andor.GetAvailableCameras())
        camHandle = andor.GetCameraHandle(0)
        print(camHandle)
        print('set camera:', andor.SetCurrentCamera(camHandle[1]))

        init = andor.Initialize("/usr/local/etc/andor")

        print('Init:', init)

        state = andor.GetStatus()

        print('Status:', state)

        print('SetAcquisitionMode:', andor.SetAcquisitionMode(1))

        print('SetShutter:', andor.SetShutter(1,0,50,50))

        # make sure cooling is off when it first starts
        print('SetTemperature:', andor.SetTemperature(0))
        print('SetFan', andor.SetFanMode(0))
        print('SetCooler', andor.CoolerOFF())

        return "connect " + str(init)

    def getTEC(self):
        # index on [result[0] - andor.DRV_TEMPERATURE_OFF]
        coolerStatusNames = ('Off', 'NotStabilized', 'Stabilized',
                             'NotReached', 'OutOfRange', 'NotSupported',
                             'WasStableNowDrifting')

        # 20037 is NotReached
        # 20035 is NotStabalized
        # 20036 is Stabalized
        # 20034 is Off

        result = andor.GetTemperatureF()
        res = coolerStatusNames[result[0] - andor.DRV_TEMPERATURE_OFF]
        print(coolerStatusNames[result[0] - andor.DRV_TEMPERATURE_OFF], result[1])
        return_res = "getTEC " + str(result[0]) + "," + str(result[1])
        return return_res

    def setTEC(self, setPoint=None):
        result = self.getTEC().split(" ")[1].split(",")
        result = [int(result[0]), float(result[1])]
        print(result)

        print(setPoint)

        if setPoint is not None:
            if result[0] == andor.DRV_TEMPERATURE_OFF:
                andor.CoolerON()
            print(andor.SetTemperature(int(setPoint)))
            self.getTEC()
        return "setTEC " + str(setPoint)

    def warmup(self):
	"""
        Pre: Used to warmup camera.
        Post: Sets the temperature to 0 and turns the fan to 0 then turns the cooler off and
        returns 1 that everything worked.
        """
        setTemp = andor.SetTemperature(0)
        setFan = andor.SetFanMode(0)
        setCooler = andor.CoolerOFF()

        results = 1
        if(setFan != andor.DRV_SUCCESS or setCooler != andor.DRV_SUCCESS):
            results = 0
        return "warmup " + str(results)

    def getTemp(self):
        # 20037 is NotReached
        # 20035 is NotStabalized
        # 20036 is Stabalized
        # 20034 is Off
        result = andor.GetTemperatureStatus()
        mode = andor.GetTemperatureF()
        txt = "" + str(mode[0])
        print(result)
        for e in result:
            txt = txt+","+str(e)
        return "temp " + txt

    def shutdown(self):
        self.warmup()
        res = self.getTemp()
        while res[1] < int(0):
            time.sleep(5)
            res = self.getTemp()
            print('waiting: %s' % str(res[1]))
        print('closing down camera connection')
        andor.ShutDown()
        return "shutdown 1"

    def filterConnect(self):
        # check the status of the filter and connect as needed
        # return which filter is in position
        pass

    def filterSlew(self, pos):
        """
        Takes in a position from 1 to 6 and slews to that filter position.
        """
        pass

    def filterHome(self):
        """
        Slews to the home position of the filter wheel.  Returns which filter position this is.
        """
        pass

    def getTimings(self):
        #retval, width, height = andor.GetDetector()
        #print retval, width, height
        expTime, accTime, kTime = andor.GetAcquisitionTimings()
        print(expTime, accTime, kTime)

        return "timings"

    def verticalSpeedStats(self, index):
        print("GetNumberVSSpeeds:", andor.GetNumberVSSpeeds())
        print("GetNumberVSAmplitudes:", andor.GetNumberVSAmplitudes())
        print("GetVSSpeed:", andor.GetVSSpeed(index))
        print("GetFastestRecommendedVSSpeed:", andor.GetFastestRecommendedVSSpeed())

    def writeData(self):
        """
        This will write all the necessary exposure files headers.
        """
        pass

    def abort(self):
        """
        This will abort the exposure and throw it out.
        """
        global isAborted
        isAborted = True
        self.isAbort = True
        print("Aborted:", andor.AbortAcquisition())
        return 'abort 1'

    # Likely not a possibility.
    def stop(self):
        """
        This will stop the exposure but read out where it stopped at, if possible.
        """
        pass

    def expose(self, imType=None, expnum=None, itime=2, binning=1):

        if expnum is None:
            self.num += 1
            expnum = self.num
        else:
            self.num = expnum

        if imType is None: # if the image type is not specified it defaults to object
            imType = "object"

        retval, width, height = andor.GetDetector()
        print('GetDetector:', retval,width,height)
        # print 'SetImage:', andor.SetImage(1,1,1,width,1,height)
        print('SetReadMode:', andor.SetReadMode(4))
        print('SetAcquisitionMode:', andor.SetAcquisitionMode(1))
        print('SetImage:', andor.SetImage(binning,binning,1,width,1,height))
        print('GetDetector (again):', andor.GetDetector())

        if(imType == "bias"):
            andor.SetShutter(1,2,0,0) # TLL mode high, shutter mode Permanently Closed, 0 millisec open/close
            print('SetExposureTime:', andor.SetExposureTime(0))
        else:
            if(imType in ['flat', 'object']):
                andor.SetShutter(1,0,5,5)
            else:
                andor.SetShutter(1,2,0,0)
            print('SetExposureTime:', andor.SetExposureTime(itime)) # TLL mode high, shutter mode Fully Auto, 5 millisec open/close


        #expTime, accTime, kTime = ctypes.c_float(), ctypes.c_float(), ctypes.c_float()
        #expTime, accTime, kTime = andor.GetAcquisitionTimings()
        print("Adjusted Exposure Time:", andor.GetAcquisitionTimings())
        # set VSSpeeds
        print("SetVSSpeed:", andor.SetVSSpeed(3))
        print('StartAcquisition:', andor.StartAcquisition())

        status = andor.GetStatus()
        print(status)
        while status[1] == andor.DRV_ACQUIRING:
            status = andor.GetStatus()
            #print("Progress:", andor.GetAcquisitionProgress())
            
        print(status)

        """
        acquired = andor.WaitForAcquisition()
        print "Result of waiting:", acquired
        """

        data = np.zeros(width//binning*height//binning, dtype='uint16')
        print(data.shape)
        result = andor.GetAcquiredData16(data)

        success = None
        if(result == 20002):
            success = 1 # for true
        else:
            success = 0 # for false

        print(result, 'success={}'.format(result == 20002))
        filename = None
        if success == 1:
            data=data.reshape(width//binning,height//binning)
            print(data.shape,data.dtype)
            hdu = fits.PrimaryHDU(data,do_not_scale_image_data=True,uint=True)
            #filename = time.strftime('/data/forTCC/image_%Y%m%d_%H%M%S.fits')
            filename = als.getImagePath()
            hdu.writeto(filename,clobber=True)
            print("wrote: {}".format(filename))
        #queue.put("expose " + filename)
        return "expose " + str(success) + ","+str(filename) + "," + str(itime)

    def realTimeExposure(self, protocol, imType, itime, binning=1): 
        """
        This will start and exposure, likely the run till abort setting, and keep reading out images for the specified time.
        """
        #global acquired
        retval,width,height = andor.GetDetector()
        print('GetDetector:', retval,width,height)

        print("SetAcquisitionMode:", andor.SetAcquisitionMode(5))
        print('SetReadMode:', andor.SetReadMode(4))

        print('SetImage:', andor.SetImage(binning,binning,1,width,1,height))
        print('GetDetector (again):', andor.GetDetector())

        print('SetExposureTime:', andor.SetExposureTime(itime))
        print('SetKineticTime:', andor.SetKineticCycleTime(0))


        if(imType == "bias"):
            andor.SetShutter(1,2,0,0) # TLL mode high, shutter mode Permanently Closed, 0 millisec open/close
            print('SetExposureTime:', andor.SetExposureTime(0))
        else:
            if(imType in ['flat', 'object']):
                andor.SetShutter(1,0,5,5)
            else:
                andor.SetShutter(1,2,0,0)
            print('SetExposureTime:', andor.SetExposureTime(itime)) # TLL mode high, shutter mode Fully Auto, 5 millisec open/close
            
        data = np.zeros(width//binning*height//binning, dtype='uint16')
        print('StartAcquisition:', andor.StartAcquisition())

        
        status = andor.GetStatus()
        print(status)
        workingImNum = 1
        while(status[1]==andor.DRV_ACQUIRING):
           
            progress = andor.GetAcquisitionProgress()
            currImNum = progress[2] # won't update until an acquisition is done
            status = andor.GetStatus()

            if(status[1] == andor.DRV_ACQUIRING and currImNum == workingImNum):
                print("Progress:", andor.GetAcquisitionProgress())
                results = andor.GetMostRecentImage16(data) # store image data
                print(results, 'success={}'.format(results == 20002)) # print if the results were successful
                
                if(results == andor.DRV_SUCCESS): # if the array filled store successfully
                    data=data.reshape(width//binning,height//binning) # reshape into image
                    print(data.shape,data.dtype)
                    hdu = fits.PrimaryHDU(data,do_not_scale_image_data=True,uint=True)
                    #filename = time.strftime('/tmp/image_%Y%m%d_%H%M%S.fits') 
                    filename = als.getImagePath()
                    hdu.writeto(filename,clobber=True)
                    print("wrote: {}".format(filename))
                    data = np.zeros(width//binning*height//binning, dtype='uint16')

                    protocol.sendData("realSent " + filename)
                    workingImNum += 1

        return "real 1" # exits with 1 for success
        
    def seriesExposure(self, protocol, imType, itime, numexp=1, binning=1):
        global isAborted
        isAborted = False
        """
        This will start and exposure, likely the run till abort setting, and keep reading out images for the specified time.
        """
        retval,width,height = andor.GetDetector()
        print('GetDetector:', retval,width,height)

        print("SetAcquisitionMode:", andor.SetAcquisitionMode(5))
        print('SetReadMode:', andor.SetReadMode(4))

        print('SetImage:', andor.SetImage(binning,binning,1,width,1,height))
        print('GetDetector (again):', andor.GetDetector())

        print('SetExposureTime:', andor.SetExposureTime(itime))
        print('SetKineticTime:', andor.SetKineticCycleTime(0))

        if(imType == "bias"):
            itime = 0
            andor.SetShutter(1,2,0,0) # TLL mode high, shutter mode Permanently Closed, 0 millisec open/close
            print('SetExposureTime:', andor.SetExposureTime(0))
        else:
            andor.SetShutter(1,0,5,5)
            print('SetExposureTime:', andor.SetExposureTime(itime)) # TLL mode high, shutter mode Fully Auto, 5 millisec open/close

        data = np.zeros(width/binning*height/binning, dtype='uint16') # reserve room for image

        print('StartAcquisition:', andor.StartAcquisition())

        status = andor.GetStatus()

        print(status)
        counter = 1
        
        while(status[1]==andor.DRV_ACQUIRING and counter <= numexp):
            status = andor.GetStatus()
            
            progress = andor.GetAcquisitionProgress()
            status = andor.GetStatus()

            if(status[1] == andor.DRV_ACQUIRING and progress[2] == counter):
                results = andor.GetMostRecentImage16(data) # store image data
                print(results, 'success={}'.format(results == 20002)) # print if the results were successful
                
                if(results == andor.DRV_SUCCESS): # if the array filled store successfully
                    data=data.reshape(width/binning,height/binning) # reshape into image
                    print(data.shape,data.dtype)

                    hdu = fits.PrimaryHDU(data,do_not_scale_image_data=True,uint=True)
                    #filename = time.strftime('/data/forTCC/image_%Y%m%d_%H%M%S.fits') 
                    filename = als.getImagePath()
                    hdu.writeto(filename,clobber=True)

                    print("wrote: {}".format(filename))
                    
                    protocol.sendData("seriesSent"+str(counter)+" "+str(counter)+","+itime+","+filename)

                counter += 1
        print("Aborting", andor.AbortAcquisition())
        return "series 1,"+str(counter) # exits with 1 for success


    def kseriesExposure(self, protocol, imType, itime, numexp=1, binning=1, numAccum=1, accumCycleTime=0, kCycleTime=0):
        """
        This will start and exposure, likely the run till abort setting, and keep reading out images for the specified time.
        """
        global isAborted
        isAborted = False
        retval,width,height = andor.GetDetector()
        print('GetDetector:', retval,width,height)

        print("SetAcquisitionMode:", andor.SetAcquisitionMode(3))
        print('SetReadMode:', andor.SetReadMode(4))

        print('SetImage:', andor.SetImage(binning,binning,1,width,1,height))
        print('GetDetector (again):', andor.GetDetector())

        if(imType == "bias"):
            itime = 0
            andor.SetShutter(1,2,0,0) # TLL mode high, shutter mode Permanently Closed, 0 millisec open/close
            print('SetExposureTime:', andor.SetExposureTime(0))
        else:
            if(imType in ['flat', 'object']):
                andor.SetShutter(1,0,5,5)
            else:
                andor.SetShutter(1,2,0,0)
            print('SetExposureTime:', andor.SetExposureTime(itime)) # TLL mode high, shutter mode Fully Auto, 5 millisec open/close

        print("SetNumberOfAccumulations:", andor.SetNumberAccumulations(numAccum)) # number of exposures to be combined
        print("SetAccumulationTime:", andor.SetAccumulationCycleTime(accumCycleTime))
        print("SetNumberOfKinetics:", andor.SetNumberKinetics(numexp)) # this is the number of exposures the user wants
        print('SetKineticTime:', andor.SetKineticCycleTime(accumCycleTime))
        print("SetTriggerMode:", andor.SetTriggerMode(0))

        print("Timings:", andor.GetAcquisitionTimings())

        print('StartAcquisition:', andor.StartAcquisition())

        status = andor.GetStatus()
        print(status)

        imageAcquired = False

        counter = 1
        while(status[1] == andor.DRV_ACQUIRING):
            status = andor.GetStatus()    
            progress = andor.GetAcquisitionProgress()

            runtime = 0
            if(progress[2] == counter or (not isAborted and progress[2] == 0 and imageAcquired)):
                runtime -= time.clock()
                data = np.zeros(width//binning*height//binning, dtype='uint16') # reserve room for image
                results = andor.GetMostRecentImage16(data) # store image data
                print(results, 'success={}'.format(results == 20002)) # print if the results were successful
                
                print('image number:', progress[2])

                if(results == andor.DRV_SUCCESS): # if the array filled store successfully
                    data=data.reshape(width//binning,height//binning) # reshape into image
                    print(data.shape,data.dtype)

                    hdu = fits.PrimaryHDU(data,do_not_scale_image_data=True,uint=True)
                    filename = time.strftime('/data/forTCC/image_%Y%m%d_%H%M%S.fits') 
                    hdu.writeto(filename,clobber=True)

                    print("wrote: {}".format(filename))
                    
                    protocol.sendData("seriesSent"+str(counter)+" "+str(counter)+","+str(itime)+","+filename)
                    
                    if(counter == numexp):
                        print("entered abort")
                        isAborted = True
                        
    
                    imageAcquired = True
                    counter += 1
                runtime += time.clock()
                print("Took %f seconds to write."%runtime)
            #print(andor.GetStatus())
        return "series 1,"+str(counter) # exits with 1 for success


if __name__ == "__main__":
    #ep = Evora()
    #ep.startup()
    reactor.suggestThreadPoolSize(30)
    reactor.listenTCP(5502, EvoraClient())
    reactor.run()

