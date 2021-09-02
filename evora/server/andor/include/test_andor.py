"""
Use like this:

import test_actor
test_actor.connect()
test_actor.expose(num,time)
# when you're done:
test_actor.shutdown()
# check that the temperature is ~0 C or above.
test_actor.cooler()
test_actor.andor.ShutDown()
"""
from __future__ import print_function
import andor
import numpy as np
import pyfits

num = 0

def connect():
    print(andor.GetAvailableCameras())
    camHandle = andor.GetCameraHandle(0)
    print(camHandle)
    print('set camera:', andor.SetCurrentCamera(camHandle[1]))
    print('Init:', andor.Initialize("/usr/local/etc/andor"))

    #time.sleep(2)

    print('Status:', andor.GetStatus())

    print('SetAcquisitionMode:', andor.SetAcquisitionMode(1));

    print('SetShutter:', andor.SetShutter(1,0,50,50));

def get_cooler():
    # index on [result[0] - andor.DRV_TEMPERATURE_OFF]
    coolerStatusNames = ('Off', 'NotStabilized', 'Stabilized',
                         'NotReached', 'OutOfRange', 'NotSupported',
                         'WasStableNowDrifting')

    result = andor.GetTemperatureF()
    print(coolerStatusNames[result[0] - andor.DRV_TEMPERATURE_OFF], result[1])
    return result[0]
    result = andor.GetTemperatureStatus()
    print(result)

def cooler(setPoint=None):

    result = get_cooler()

    if setPoint is not None:
        if result == andor.DRV_TEMPERATURE_OFF:
            andor.CoolerON()
        andor.SetTemperature(setPoint)
        get_cooler()

def expose(expnum=None, itime=2, bin=1):

    global num
    if expnum is None:
        num += 1
        expnum = num
    else:
        
        num = expnum

    retval,width,height = andor.GetDetector()
    print('GetDetector:', retval,width,height)
    # print 'SetImage:', andor.SetImage(1,1,1,width,1,height)
    print('SetReadMode:', andor.SetReadMode(4))
    print('SetImage:', andor.SetImage(bin,bin,1,width,1,height))
    print('GetDetector (again):', andor.GetDetector())
    
    andor.SetShutter(1,0,5,5)

    print('SetExposureTime:', andor.SetExposureTime(itime))
    print('StartAcquisition:', andor.StartAcquisition())

    status = andor.GetStatus()
    print(status)
    while(status[1]==andor.DRV_ACQUIRING):
        status = andor.GetStatus()
        # print status

    data = np.zeros(width/bin*height/bin, dtype='uint16')
    print(data.shape)
    result = andor.GetAcquiredData16(data)
    print(result, 'success={}'.format(result == 20002))
    data=data.reshape(width/bin,height/bin)
    print(data.shape,data.dtype)
    hdu = pyfits.PrimaryHDU(data,do_not_scale_image_data=True,uint=True)
    filename = '/data/tests4/image{}_{:0.2f}s.fits'.format(expnum,itime)
    hdu.writeto(filename,clobber=True)
    print("wrote: {}".format(filename))

def shutdown():
    andor.CoolerOFF()
