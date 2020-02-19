#!/usr/bin/env python

import serial
from Phidget22.Phidget import *
from Phidget22.Devices.Stepper import *

class FilterWheel:
    def __init__(self):
        'Sets up internal variables and initializes the stepper and serial port.'
        self._VELOCITY_LIMIT = 5000
        self._filterPos = None
        self._hallData = None
        
        self.stepper = Stepper()
        self.stepper.openWaitForAttachment(10000)

        self.stepper.setControlMode(StepperControlMode.CONTROL_MODE_RUN)
        self.stepper.setAcceleration(20000)
        self.stepper.setCurrentLimit(0.9)

        self.SerialPort = serial.Serial(self.SerialPortAddress, 9600, timeout = 2)
        self.SerialPortAddress = '/dev/ttyACM0'
        
        print("Filterwheel connection successful.")

    def disconnDev(self):
        'Disconnects the stepper and serial port.'
        self.stepper.setVelocityLimit(0)
        self.stepper.setEngaged(False)
        self.stepper.close()
        self.SerialPort.close()
        print("Disconnect successful")
        return

    def getHallData(self, index):
        '''Gets the Hall sensor data and returns the sensor value at the index.
        Indices 0 and 1 store if a magnet is detected (0 returned) or not (1).'''
        self.SerialPort.write('s')
        self._hallData = self.SerialPort.readline().rstrip('\r\n').split(',')
        return int(self._hallData[index])
    
    def getFilterPos(self):
        'Returns the position of the filterwheel, an integer between 0 and 5.'
        return str(self._filterPos)
    
    def home(self):
        'Homes the filter wheel to position 0.'
        self.stepper.setEngaged(True)
        self.stepper.setVelocityLimit(self._VELOCITY_LIMIT)
        
        while self.getHallData(0) != 0 or self.getHallData(1) != 0:
            pass
            
        self._filterPos = 0
        
        self.stepper.setVelocityLimit(0)
        self.stepper.setEngaged(False)
        
        print("Homed")
        return 'home 1'
        
    def moveFilter(self, num):
        'Moves the filter to the specified position, an integer between 0 and 5.'
        self.stepper.setEngaged(True)
        self.stepper.setVelocityLimit(self._VELOCITY_LIMIT)
        
        if self._filterPos == None:
            print("Not homed, homing first.")
            self.home()
        
        if num >= self._filterPos:
            swaps = abs(num - self._filterPos)
        else:
            swaps = 6 - self._filterPos + num
            
        while swaps != 0:
            while self.getHallData(0) == 0:
                pass
                
            while self.getHallData(0) != 0:
                pass
            swaps -= 1
        
        self._filterPos = num
        
        self.stepper.setVelocityLimit(0)
        self.stepper.setEngaged(False)
        
        print("At filter position %d." % num)
        return 'True'