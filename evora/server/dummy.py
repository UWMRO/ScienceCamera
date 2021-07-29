from PIL import Image
from numpy import asarray
import base64
from io import BytesIO
from random import randint

# Replacement constants
DRV_SUCCESS = 1
DRV_TEMPERATURE_OFF = 1
DRV_ACQUIRING = 0


# Andor SDK replacement functions with return values
def GetStatus():
    # Magic number means camera is uninitialized
    return 20075


def GetAvailableCameras(status):
    return 1


def GetCameraHandle(cameraIndex, cameraHandle):
    return 1


def Initialize(directory):
    return 1


def GetTemperatureF(temperature):
    return temperature


def GetTemperatureStatus(SensorTemp, TargetTemp, AmbientTemp, CoolerVolts):
    return 1


def GetTemperatureRange(mintemp, maxtemp):
    return maxtemp-mintemp


# Acquisition
def StartAcquisition():
    DRV_ACQUIRING = 1


def AbortAcquisition():
    DRV_ACQUIRING = 0


def GetAcquiredData16(write_var):
    img = 'space.txt'
    if randint(0, 1000) >= 999:
        img = 'space0.txt'

    with open(img) as f:
        data = asarray(Image.open(BytesIO(base64.b64decode(f.read()))))

    # This might not work, passing by reference is weird in Python
    write_var = data
    return DRV_SUCCESS


# These functions do the same thing in this context
GetMostRecentImage16 = GetAcquiredData16

def GetAcquisitionTimings(exposure, accumulate, kinetic):
    return 1

def GetNumberVSSpeeds(speeds):
    return 1

def GetNumberVSAmplitudes(number):
    return 1

def GetVSSpeed(index, speed):
    return 1

def GetFastestRecommendedVSSpeed(index, speeds):
    return 1

def GetNumberHSSpeeds(channel, typ, speeds):
    return 1

def GetHSSpeed(channel, typ, index, speed):
    return 1

def GetDetector(xpixels, ypixels):
    return 1

def GetAcquisitionProgress(acc, series):
    return 1

# Setter functions
def noop(*args):
    # Takes any number of arguments, does nothing
    pass


# Set to noop func instead of defining each to save space
SetCurrentCamera = noop
SetAcquisitionMode = noop
SetTemperature = noop
SetShutter = noop
SetFanMode = noop
CoolerOFF = noop
CoolerON = noop
Shutdown = noop
SetReadMode = noop
SetImage = noop
SetShutter = noop
SetExposureTime = noop
SetKineticCycleTime = noop
SetNumberAccumulations = noop
SetAccumulationCycleTime = noop
SetNumberKinetics = noop
SetTriggerMode = noop
