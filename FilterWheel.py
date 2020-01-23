#!/usr/bin/env python

import serial
from Phidget22.Phidget import *
from Phidget22.Devices.Stepper import *

class FilterMotor:
    def __init__(self, motorProtocol):
        'Sets up a dictionary and motor protocol and initializes the stepper and serial port.'
        self.dict = {"acceleration": 20000, "velocityLimit": 5000, "ampLimit": 0.9, "filterPos": None, "hallData": None, "homed": False}
        self.motorProtocol = motorProtocol
        
        self.stepper = Stepper()
        self.stepper.openWaitForAttachment(10000)
        
        self.stepper.setControlMode(StepperControlMode.CONTROL_MODE_RUN)
        self.stepper.setAcceleration(self.dict['acceleration'])
        self.stepper.setCurrentLimit(self.dict['ampLimit'])

        self.SerialPort = serial.Serial(self.SerialPortAddress, 9600, timeout = 2)
        self.SerialPortAddress = '/dev/ttyACM0'

    def disconnDev(self):
        'Disconnects the stepper and serial port.'
        self.stepper.setVelocityLimit(0)
        self.setEngaged(False)
        self.stepper.close()
        self.SerialPort.close()
        print("Disconnect successful")
        return

    def getHallData(self, index):
        '''Gets the Hall sensor data and returns the sensor value at the index.
        Indices 0 and 1 store if a magnet is detected (0 returned) or not (1).'''
        self.SerialPort.write('s')
        self.dict['hallData'] = self.SerialPort.readline().rstrip('\r\n').split(',')
        return int(self.dict['hallData'][index])
    
    def home(self):
        'Homes the filter wheel to position 0.'
        self.stepper.setEngaged(True)
        self.stepper.setVelocityLimit(self.dict['velocity'])
        
        print("Homing...")
        
        while self.getHallData(0) != 0 or self.getHallData(1) != 0:
            pass
            
        self.dict['homed'] = True
        self.dict['filterPos'] = 0
        
        self.stepper.setVelocityLimit(0)
        self.stepper.setEngaged(False)
        
        return 'home 1' # Returning a boolean has issues coming out client side
        
    def moveFilter(self, num):
        'Moves the filter to the specified position, an integer between 0 and 5.'
        self.stepper.setEngaged(True)
        self.stepper.setVelocityLimit(self.dict['velocity'])
        
        if self.dict['homed'] == False:
            print("Not homed, homing first.")
            self.home()
            
        print("Moving to filter position %d" % num)
            
        if num - self.dict['filterPos'] < 0: 
            self.stepper.setVelocityLimit(-self.dict['velocity'])
                
        swaps = abs(num - self.dict['filterPos'])
        while swaps != 0:
            while self.getHallData(0) == 0:
                pass
                
            while self.getHallData(0) != 0:
                pass
            swaps -= 1
        
        self.dict['filterPos'] = num
        
        self.stepper.setVelocityLimit(0)
        self.stepper.setEngaged(False)
        
        return True