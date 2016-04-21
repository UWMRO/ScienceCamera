#!/usr/bin/python


import andor
import numpy as np
import pyfits
import time

from twisted.protocols import basic
from twisted.internet import protocol, reactor

#import ProtoParser

# port for evora is 5502

class EvoraServer(basic.LineReceiver):
    def connectionMade(self):
        """
        If you send more than one line then the callback to start the gui completely will fail.
        """
        self.factory.clients.append(self)
        #self.sendMessage("Welcome to the Evora Server")
        if len(self.factory.clients) is 1:
            #self.sendMessage("Starting camera")
            ep = EvoraParser()
            command = ep.parse("connect")
            self.sendMessage("startup 1") # activate the callback to give full control to the camera.
        else:
            self.sendMessage("startup 1") # for when there is more than one client open

    def connectionLost(self, reason):
        #self.sendLine("Connection Lost")
        if len(self.factory.clients) is 1:
            ep = EvoraParser()
            command = ep.parse("shutdown")
            #self.sendMessage(command)
        
        self.factory.clients.remove(self)            

    def lineReceived(self, line):
        print "received", line
        ep = EvoraParser()
        command = ep.parse(line)
        if command != None:
            self.sendMessage(str(command))
           
    def sendMessage(self, message):
        for client in self.factory.clients:
            client.sendLine(message)


class EvoraClient(protocol.ServerFactory):
    protocol = EvoraServer
    clients = []

## Evora Parser commands sent here from server where it envokes the camera commands.
class EvoraParser(object):
    def __init__(self):
        self.e = Evora()

    def parse(self, input = None):
        print input
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
            print "entered shutdown"
            return self.e.shutdown()
        if input[0] == 'expose':
            # expose flat 1 10 2
            type = input[1]
            expnum = int(input[2])
            itime = int(input[3]) # why int?
            bin = int(input[4])
            return self.e.expose(expnum, itime, bin)


class Evora(object):

    def __init__(self):
        self.num = 0

    def startup(self):
	"""
	20002 is the magic number.  Any different number and it didn't work.
	"""
        print andor.GetAvailableCameras()
        camHandle = andor.GetCameraHandle(0)
        print camHandle
        print 'set camera:', andor.SetCurrentCamera(camHandle[1])
	
	init = andor.Initialize("/usr/local/etc/andor")	

        print 'Init:', init

	state = andor.GetStatus()        

        print 'Status:', state
        
        print 'SetAcquisitionMode:', andor.SetAcquisitionMode(1);
        
        print 'SetShutter:', andor.SetShutter(1,0,50,50);
	
	return str(init)

    def getTEC(self):
        # index on [result[0] - andor.DRV_TEMPERATURE_OFF]
        coolerStatusNames = ('Off', 'NotStabilized', 'Stabilized',
                         'NotReached', 'OutOfRange', 'NotSupported',
                         'WasStableNowDrifting')

        result = andor.GetTemperatureF()
	res = coolerStatusNames[result[0] - andor.DRV_TEMPERATURE_OFF]
        print coolerStatusNames[result[0] - andor.DRV_TEMPERATURE_OFF], result[1]
        return result

    def setTEC(self,setPoint=None):

        result = self.getTEC()

	print setPoint

        if setPoint is not None:
            if result[0] == andor.DRV_TEMPERATURE_OFF:
                andor.CoolerON()
            print andor.SetTemperature(int(setPoint))
            self.getTEC()
	return str(setPoint)

    def warmup(self):
	"""
	Pre: Used to warmup camera.
	Post: Sets the temperature to 0 and turns the fan to 0 then turns the cooler off and 
	returns 1 that everything worked.
	"""
        andor.SetTemperature(0)
	andor.SetFanMode(0)
	andor.CoolerOFF()
	return "1"

    def getTemp(self):
	result = andor.GetTemperatureStatus()
	txt = ""
	print result
	for e in result:
		txt = txt+","+str(e)
        return "temp " + txt

    def shutdown(self):
	self.warmup()
	res = self.getTemp()
	while res[1] < int(0):
		time.sleep(5)
		res = self.getTemp()
		print 'waiting: %s' % str(res[1])
	print 'closing down camera connection'
        andor.ShutDown()
        return "shutdown 1"
    
    def expose(self,expnum=None, itime=2, bin=1):

        if expnum is None:
            self.num += 1
            expnum = self.num
        else:
        
            self.num = expnum

        retval,width,height = andor.GetDetector()
        print 'GetDetector:', retval,width,height
        # print 'SetImage:', andor.SetImage(1,1,1,width,1,height)
        print 'SetReadMode:', andor.SetReadMode(4)
        print 'SetImage:', andor.SetImage(bin,bin,1,width,1,height)
        print 'GetDetector (again):', andor.GetDetector()
    
        andor.SetShutter(1,0,5,5)

        print 'SetExposureTime:', andor.SetExposureTime(itime)
        print 'StartAcquisition:', andor.StartAcquisition()

        status = andor.GetStatus()
        print status
        while(status[1]==andor.DRV_ACQUIRING):
            status = andor.GetStatus()
            # print status

        data = np.zeros(width/bin*height/bin, dtype='uint16')
        print data.shape
        result = andor.GetAcquiredData16(data)
        print result, 'success={}'.format(result == 20002)
        data=data.reshape(width/bin,height/bin)
        print data.shape,data.dtype
        hdu = pyfits.PrimaryHDU(data,do_not_scale_image_data=True,uint=True)
	filename = time.strftime('/data/forTCC/image_%Y%m%d_%H%M%S.fits')
        hdu.writeto(filename,clobber=True)
        print "wrote: {}".format(filename)
	return "1"

	def abort(self):
		"""
		This will abort the exposure and throw it out.
		"""
		pass
	
	def stop(self):
		"""
		This will stop the exposure but read out where it stopped at, if possible.
		"""
		pass


if __name__=="__main__":
    #ep = Evora()
    #ep.startup()
    reactor.listenTCP(5502, EvoraClient())
    reactor.run()

