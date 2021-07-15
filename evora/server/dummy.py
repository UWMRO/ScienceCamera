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


def GetAvailableCameras():
    return 1


def GetCameraHandle():
    return 1


def Initialize(directory):
    return 1


def GetTemperatureF(temperature):
    return temperature


def GetTemperatureStatus():
    return 1


def GetTemperatureRange(mintemp, maxtemp):
    return maxtemp-mintemp


# Acquisition
def StartAcquisition():
    # May need to set DRV_ACQUIRING=1 later
    pass


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
