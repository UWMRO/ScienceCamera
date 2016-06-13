#!/usr/bin/env python

#==>add usage docstring
"""
#install for raspberrypi
#libusb via aptget
#phidgetlib from phidget website
#pip install phidgets


"""

import time
import os
from Phidgets.PhidgetException import PhidgetErrorCodes, PhidgetException
from Phidgets.Events.Events import AttachEventArgs, DetachEventArgs, ErrorEventArgs, InputChangeEventArgs, CurrentChangeEventArgs, StepperPositionChangeEventArgs, VelocityChangeEventArgs
from Phidgets.Devices.Stepper import Stepper
from Phidgets.Phidget import PhidgetLogLevel
import fw_io
import numpy as np


class FilterMotor(object):
	def __init__(self):
		"""Add docs to all functions"""
		self.stepper = None
		self.fw = fw_io.FWIO()
		self.dict = {"velocity":None, "amp":None, "acceleration":None, "currentPos":None, "power":None, "hall":None, "commandedPos":None, "filterDelta":6860, "ID":None, "home":False, "filterPos":None}

	def DisplayDeviceInfo(self):
		#==> rename to getDeviceInfo
    		print("|- %8s -|- %30s -|- %10d -|- %8d -|" % (self.stepper.isAttached(), self.stepper.getDeviceName(), self.stepper.getSerialNum(), self.stepper.getDeviceVersion()))
    		print("Number of Motors: %i" % (self.stepper.getMotorCount()))
		return

	def connDev(self):
		"""connect to device and open serial connection to arduino"""
		self.stepper = Stepper()
                self.stepper.openPhidget()
                self.stepper.waitForAttach(10000)

		self.setParm(20000,5000,0.8)

		self.fw.openPort()
		time.sleep(2)
		print "Stepper Driver Connected"
		self.status()
		return 1

	def disconnDev(self):
		time.sleep(1)
		self.motorPower(False)
		self.stepper.closePhidget()
		print "Stepper Driver Disconnected"
		return

	def motorPower(self, val = False):
		self.stepper.setEngaged(0,val)
		return

	def setParm(self, acc, vel, cur):
		self.stepper.setAcceleration(0, acc) 
	    	self.stepper.setVelocityLimit(0, vel)
		self.stepper.setCurrentLimit(0,cur)
		if cur>1.4:				
			print "Cannot set current above 1.5. Current set to 0.5"
			return
		return
 
	def status(self):
		self.dict['power'] = self.stepper.getEngaged(0)
		self.dict['currentPos'] = int(self.stepper.getCurrentPosition(0))
		self.dict['acceleration'] =self.stepper.getAcceleration(0)
		self.dict['velocity'] = self.stepper.getVelocityLimit(0)
		self.dict['amp'] = self.stepper.getCurrentLimit(0)
		self.dict['hall'] = self.fw.getStatus()
		self.dict['filterPos'] = int(self.dict['currentPos'])/int(self.dict['filterDelta'])
		return self.dict

	def setPos(self, pos = None):
		self.stepper.setCurrentPosition(0, int(pos))	
		return

	def moveMotor(self, pos = None):
		self.motorPower(True)
		self.stepper.setTargetPosition(0, int(pos))
		self.dict["commandedPos"] = pos
		return

	def nudge(self, mov):
		x = self.stepper.getCurrentPosition(0) + mov 
		self.movemotor(x)
		time.sleep(0.5)
		print "New Position:", self.stepper.getCurrentPosition(0)
		return

	def test3(self):
		x = 0
		while x != 1:
			continue
		print "hi" 

	def moveFilter(self, num = None):
		delta = int(self.dict['filterDelta'])
		print "Moving to filter position %d" % num
		tpos = num*delta
		self.moveMotor(tpos)			
		return

	def motorStop(self):
		self.motorPower(False)
		return

	def home(self): 
		crossArr = [0]
		pastHome = 0
		previousPos = 0
		try:
			print "starting home sequence"
			self.setPos(0)
			self.moveMotor(100000)
			time.sleep(.2)
			self.status()
			while int(self.dict['currentPos']) < int(self.dict['commandedPos']):
				self.status()
				if self.dict['hall'][0] == '0':
					if self.dict['hall'][0] == '0' and self.dict['hall'][1] == '0':
						if pastHome == 0: 
							pastHome = pastHome + 1
							print 'first home', self.status()
							previousPos = self.dict['currentPos']
						if  self.dict['currentPos'] - previousPos >  3000:
							pastHome = pastHome + 1
							print 'second home', self.status()
						if pastHome == 2:
							self.motorStop()
							self.setPos(int(100))
							time.sleep(2)
							print self.status()
							break
		
					if self.dict['currentPos'] - previousPos >  3000:
						#print self.dict['position'] - previousPos
						crossArr.append(self.dict['currentPos'] - previousPos)
						#print self.status(), crossArr
						previousPos = self.dict['currentPos']
				if self.dict['currentPos'] == self.dict['commandedPos']:
                                	raise Exception

			del crossArr[0]
			del crossArr[0]
			self.dict['filterDelta'] = int(np.mean(crossArr))
			print "homed", self.status()
			self.moveMotor(0)
			time.sleep(1)
			self.dict["home"] = True
		except:
			self.dict["home"] = False
			self.motorPower(False)
			return False
		self.motorPower(False)
		return True

if __name__ == "__main__":
	p = FilterMotor()
	p.connDev()
	time.sleep(.5)
	print p.home()
	time.sleep(.5)
	p.disconnDev()

