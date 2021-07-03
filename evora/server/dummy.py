# Replacement constants
DRV_SUCCESS = 1
DRV_TEMPERATURE_OFF = 1
DRV_ACQUIRING = 0


# Andor SDK replacement functions
def GetStatus():
    # Means camera is uninitialized
    return 20075


def GetAvailableCameras():
    return 1


def GetCameraHandle():
    return 1


def SetCurrentCamera():
    pass


def Initialize(directory):
    return 1


def SetAcquisitionMode(mode):
    pass


def SetShutter(typ, mode, closingtime, openingtime):
    pass


def SetTemperature(temperature):
    pass


def SetFanMode(mode):
    pass


def CoolerOFF():
    pass


def GetTemperatureF(temperature):
    return temperature


def CoolerON():
    pass


def GetTemperatureStatus():
    return 1


def GetTemperatureRange(mintemp, maxtemp):
    return maxtemp-mintemp


def ShutDown():
    pass


# Acquisition
def StartAcquisition():
    # May need to set DRV_ACQUIRING=1 later
    pass


def AbortAcquisition():
    DRV_ACQUIRING = 0
