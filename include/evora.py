#! /usr/bin/python

import andor

class evora(object):

    def startup():
        print andor.GetAvailableCameras()
        camHandle = andor.GetCameraHandle(0)
        print camHandle
        print 'set camera:', andor.SetCurrentCamera(camHandle[1])
        print 'Init:', andor.Initialize("/usr/local/etc/andor")
        
        #time.sleep(2)
        
        print 'Status:', andor.GetStatus()
        
        print 'SetAcquisitionMode:', andor.SetAcquisitionMode(1);
        
        print 'SetShutter:', andor.SetShutter(1,0,50,50);

    def get_cooler():
        # index on [result[0] - andor.DRV_TEMPERATURE_OFF]
        coolerStatusNames = ('Off', 'NotStabilized', 'Stabilized',
                         'NotReached', 'OutOfRange', 'NotSupported',
                         'WasStableNowDrifting')

        result = andor.GetTemperatureF()
        print coolerStatusNames[result[0] - andor.DRV_TEMPERATURE_OFF], result[1]
        return result[0]
        print '2'
        result = andor.GetTemperatureStatus()
        print result


    def cooler(setPoint=None):

        result = get_cooler()

        if setPoint is not None:
            if result == andor.DRV_TEMPERATURE_OFF:
                andor.CoolerON()
            andor.SetTemperature(setPoint)
            get_cooler()

    def warmup():
        pass

    def shutdown():
        pass



if __name__ == "__main__":
    e = evora()
    e.startup()
    e.get_cooler()
