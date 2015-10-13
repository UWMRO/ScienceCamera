#! /usr/bin/python

import andor
import numpy as np
import pyfits
import time

class evora(object):

    def __init__(self):
	self.num = 0

    def startup(self):
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
	return txt

    def shutdown(self):
	self.warmup()
	res = self.getTemp()
	while res[1] < int(0):
		time.sleep(5)
		res = self.getTemp()
		print 'waiting: %s' % str(res[1])
	print 'closing down camera connection'
        andor.ShutDown()
	return "1"
    
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


if __name__ == "__main__":
    e = evora()
    e.startup()
    e.get_cooler()
