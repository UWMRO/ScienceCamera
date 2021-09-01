from PIL import Image
from numpy import asarray
import base64
from io import BytesIO
from random import randint

# Replacement constants
DRV_SUCCESS = 1
DRV_TEMPERATURE_OFF = 20034
DRV_TEMPERATURE_STABILIZED = 20036
DRV_ACQUIRING = 0

"""
SWIG notes
SWIG seems to change the API from the docs in two major ways
1. Unsigned int functions actually return [status, return_val] e.g. [DRV_SUCCESS, 35]
2. Pointer arguments are simply omitted e.g. int SomeFunction(long* input) -> def SomeFunction()...
"""

# Andor SDK replacement functions with return values
def GetStatus():
    # Magic number means camera is uninitialized
    return [20075, 0]


def GetAvailableCameras():
    return 1


def GetCameraHandle(cameraIndex):
    return [DRV_SUCCESS, 1]


def Initialize(directory):
    return 1


def GetTemperatureF():
    return [DRV_SUCCESS, 32]


def GetTemperatureStatus():
    return [DRV_SUCCESS, 1]


def GetTemperatureRange(mintemp, maxtemp):
    return [maxtemp-mintemp, mintemp, maxtemp]


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
