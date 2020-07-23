"""Python OO interface for controlling an Andor Ikon camera."""
import andor
import BaseCam
import numpy as np


class AndorError(BaseCam.CameraError):
    pass

class AndorCam(BaseCam.BaseCam):

    # index on [result[0] - andor.DRV_TEMPERATURE_OFF]
    coolerStatusNames = ('Off', 'NotStabilized', 'Stabilized',
                         'NotReached', 'OutOfRange', 'NotSupported',
                         'WasStableNowDrifting')

    def __init__(self):
        """ Connect to an Andor ikon and start to initialize it. """

        self.camName = 'Andor iKon'
        BaseCam.BaseCam.__init__(self)

        self.IDLE = andor.DRV_IDLE

        # TBD: this is a guess
        self.shutter_time = 5 # in milliseconds
        self.read_time = 0.5

        self.binning = 2

    def connect(self):
        """ (Re-)initialize and already open connection. """

        super(AndorCam,self).doInit()

        self.camHandle = self.safe_call(andor.GetCameraHandle,0)
        self.safe_call(andor.SetCurrentCamera,self.camHandle)
        self.safe_call(andor.Initialize,"/usr/local/etc/andor")
        self.width,self.height = self.safe_call(andor.GetDetector)
        self.ok = True

        self._checkSelf()

        # Turn off LEDs
        # self.write_LedMode(0)

    def safe_call(self,func,*args):
        """
        Call func with args, check return for success, return actual result, if any.
        
        Raises descriptive exception on call failure.
        """
        if self.verbose:
            print 'Calling: {}{}'.format(func.__name__,args)
        result = func(*args)
        # unpack the result: could be a single return value,
        # return value + one thing, or return value + many things.
        if type(result) == list:
            retval = result[0]
            if len(result[1:]) == 1:
                result = result[1]
            else:
                result = result[1:]
        else:
            retval = result
        if retval != andor.DRV_SUCCESS:
            # TBD: convert "result" into something useful, or at least return the
            # TBD: full DRV_* name of it, so it's easier to interpret.
            raise AndorError('Error number {} calling {} with arguments {}'.format(retval,func,args))
        return result

    def _status(self):
        """Get the status of the camera."""
        return self.safe_call(andor.GetStatus)

    def cooler_status(self):
        self._checkSelf()

        self._check_temperature()
        return super(AndorCam,self).cooler_status()

    def set_cooler(self, setpoint):
        if super(AndorCam,self).set_cooler(setpoint) is None:
            return

        # not safe_call: we need the return value
        result = andor.GetTemperatureF()
        if result[0] == andor.DRV_TEMPERATURE_OFF:
            self.safe_call(andor.CoolerON)
        # NOTE: setTemperature wants only an int...
        andor.SetTemperature(int(setpoint))

        return self.cooler_status()

    def set_binning(self, x, y=None):
        pass

    #LCOHACK TBD: should fix this to just set_binning above generically.
    def setBOSSFormat(self, cmd=None, doFinish=False):
        self.binning = 2
    def setFlatFormat(self, cmd=None, doFinish=False):
        self.binning = 1

    def Unbinned(self):
        """Set the default binning for this camera/location."""
        self._checkSelf()

        self.safe_call(andor.SetReadMode,4)
        self.safe_call(andor.SetImage,1,1,1,self.width,1,self.height)

    def _prep_exposure(self):

        if self._status() != self.IDLE:
            raise AndorError('Cannot start exposure: camera not idle.')

        self.safe_call(andor.SetAcquisitionMode, 1)
        self.safe_call(andor.SetExposureTime, self.itime)
        # NOTE: SetImage wants hbin,vbin, then the on-chip image range.
        self.safe_call(andor.SetImage,self.binning,self.binning,1,self.width,1,self.height)

        # Note: Internal trigger mode is the default: no need to set anything for that.

        if self.openShutter:
            mode = 0
        else:
            mode = 2 # permanently closed for darks, etc.
        # Internal shutters are always TTL High, so first param is 1
        self.safe_call(andor.SetShutter,1,mode,int(self.shutter_time),int(self.shutter_time))

    def _start_exposure(self):
        self.safe_call(andor.StartAcquisition)

    def _safe_fetchImage(self,cmd=None):
        """Wrap a call to GetAcquiredData16 in case of bad reads."""
        image = np.zeros((self.width/self.binning) * (self.height/self.binning), dtype='uint16')
        self.safe_call(andor.GetAcquiredData16,image)
        # flip horizontally, to match the image orientation at APO.
        return np.fliplr(image.reshape(self.width/self.binning,self.height/self.binning))

    def _cooler_off(self):
        self.setpoint = 0
        self.safe_call(andor.CoolerOFF)

    def _check_temperature(self):
        # NOTE: apparently this function doesn't actually exist?
        # SensorTemp, TargetTemp, AmbientTemp, CoolerVolts = self.safe_call(andor.GetTemperatureStatus)

        result = andor.GetTemperatureF()
        if result[0] == andor.DRV_ACQUIRING:
            # just update the temperature, don't change the status text
            self.ccdTemp = result[1]
        elif result[0] == andor.DRV_ERROR_ACK:
            self.ok = False
            raise AndorError('Communication error when getting temperature!')
        else:
            self.ccdTemp = result[1]
            self.set_status_text(result[0] - andor.DRV_TEMPERATURE_OFF)

    def _shutdown(self):
        andor.ShutDown()
