#!/usr/bin/env python

#Basic imports
import sys
import time
from ctypes import *

from Phidgets.Devices.Stepper import Stepper
from Phidgets.Events.Events import (AttachEventArgs, CurrentChangeEventArgs,
                                    DetachEventArgs, ErrorEventArgs,
                                    InputChangeEventArgs,
                                    StepperPositionChangeEventArgs,
                                    VelocityChangeEventArgs)
from Phidgets.Phidget import PhidgetLogLevel
#Phidget specific imports
from Phidgets.PhidgetException import PhidgetErrorCodes, PhidgetException

"""
Haydon Kerk Bipolar Stepper start parameters
A = Red/White
B = Red
C = Green/White
D = Green

Vel Limit = 22321
Accel = 262144
Current Limit = 0.31
"""

class PhidgetMotorController(object):
	def __init__(self):
		self.stepper = Stepper()
		self.stepper.openPhidget()
		print('attaching stepper dev ...')
		self.stepper.waitForAttach(10000)
		self.DisplayDeviceInfo
		

	def DisplayDeviceInfo(self):
    		print("|- %8s -|- %30s -|- %10d -|- %8d -|" % (self.stepper.isAttached(), self.stepper.getDeviceName(), self.stepper.getSerialNum(), self.stepper.getDeviceVersion()))
    		print("Number of Motors: %i" % (self.stepper.getMotorCount()))

	def disconnDev(self):
#		print "Setting to Home Position"
#		self.stepper.setTargetPosition(0, 0)
#		time.sleep(4)
#		print "Shutting Down"
		self.motorPower(False)
#		print "Goodbye"
		self.stepper.closePhidget()

	def setupParm(self):
		self.stepper.setAcceleration(0, 30000)
	    	self.stepper.setVelocityLimit(0, 8000)
    		self.stepper.setCurrentLimit(0, 1.0)
		self.stepper.setCurrentPosition(0,0)

	def moveMotor(self, pos = None):
		self.stepper.setTargetPosition(0, int(pos))
		while self.stepper.getCurrentPosition(0) != int(pos) :
			print self.stepper.getCurrentPosition(0)
			time.sleep(.1)

	def motorPower(self, val = False):
		self.stepper.setEngaged(0,val)

	def filterselect(self, num = None):
		print "Moving to filter position %d" % num
		if int(num)<= 6 and int(num)>=1:
			self.stepper.setTargetPosition(0, int(num)*6958)
		elif int(num)>6:
			print "Not Valid Filter Number"
		elif int(num)<1:
			print "Not Valid Filter Number"

#	def findhome(self):
#		while x = False
#			self.stepper.setTargetPosition(0, 9999999)
#		

if __name__ == "__main__":
	p = PhidgetMotorController()
	p.setupParm()
	p.motorPower(True)
	time.sleep(1)
	p.moveMotor(30000)
	time.sleep(1)
	p.moveMotor(0)
	p.disconnDev()

