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


class FilterMotor(object):
	def __init__(self):
		"""Add docs to all functions"""
		self.stepper = None
		self.fw = fw_io.FWIO()

	def DisplayDeviceInfo(self):
		#==> rename to getDeviceInfo
    		print("|- %8s -|- %30s -|- %10d -|- %8d -|" % (self.stepper.isAttached(), self.stepper.getDeviceName(), self.stepper.getSerialNum(), self.stepper.getDeviceVersion()))
    		print("Number of Motors: %i" % (self.stepper.getMotorCount()))

	def connDev(self):
		"""connect to device and open serial connection to arduino"""
		self.stepper = Stepper()
                self.stepper.openPhidget()
                self.stepper.waitForAttach(10000)

		self.param(20000,6000,0.75)

		self.fw.openPort()

	def disconnDev(self):
		time.sleep(1)
		self.motorpower(False)
		self.stepper.closePhidget()

	def motorpower(self, val = False):
		self.stepper.setEngaged(0,val)

		self.param(0,20000,6000,0.75)
		self.motorpower(True)

	def setParm(self, acc, vel, cur):
		self.stepper.setAcceleration(0, acc) 
	    	self.stepper.setVelocityLimit(0, vel)
		if cur>1.4:				
			print "Cannot set current above 1.5. Current set to 0.5"
			return
 
	def status(self):
		dict = {"velocity":None, "amp":None, "acceleration":None, "position":None, "power":None, "hall":None}
		dict['power'] = self.stepper.getEngaged(0)
		dict['position'] = self.stepper.getCurrentPosition(0)
		dict['acceleration'] =self.stepper.getAcceleration(0)
		dict['velocity'] = self.stepper.getVelocityLimit(0)
		dict['amp'] = self.stepper.getCurrentLimit(0)
		dict['hall'] = FWIO.status()
		return dict

	def setPos(self, pos = None):
		self.stepper.setCurrentPosition(0, pos)	

	def moveMotor(self, pos = None):
		self.stepper.setTargetPosition(0, int(pos))

	def nudge(self, mov):
		x = self.stepper.getCurrentPosition(0) + mov 
		self.movemotor(x)
		time.sleep(0.5)
		print "New Position:", self.stepper.getCurrentPosition(0)

	def test3(self):
		x = 0
		while x != 1:
			continue
		print "hi" 

	def filterselect(self, num = None):
		print "Moving to filter position %d" % num
		if int(num)<= 6 and int(num)>=0:
			self.movemotor(int(num)*7050)
			tpos = num*7050
			while self.getCurrentPosition() != tpos:
				continue
			while switch == false:
				self.movemotor(tpos+1000)
				if switch == True:
					self.motorstop()
					self.setCurrentPosition(0,tpos)
				else: 
					self.movemotor(tpos-1000)
					if switch == True:
						self.motorstop()
						self.setCurrentPosition(0,tpos)
			
		elif int(num)>6:
			print "Not Valid Filter Number"
		elif int(num)<0:
			print "Not Valid Filter Number"

	def test(self, x): #test for drifting
		n=0		
		while n<x:
			n+=1
			print n
			self.filterselect(6)
			time.sleep(8)
			self.filterselect(0)
			time.sleep(8)	

	def motorstop(self):
		self.stepper.setAcceleration(0,200000)
		self.stepper.setVelocityLimit(0,0)
		time.sleep(0.2)
		y = self.stepper.getCurrentPosition(0)
		self.stepper.setCurrentPosition(0,y)
		self.stepper.setVelocityLimit(0,self.gvel)
		self.stepper.setAcceleration(0,self.gacc)

	def findhome(self, switch): #'switch' placeholder for actual returned boolean value of switches
		self.stepper.setVelocityLimit(0, 4000)
		while switch == False:
			self.stepper.setTargetPosition(0, 99999)
		print self.stepper.getCurrentPosition(0)
		self.stepper.setVelocityLimit(0,0)
		self.stepper.setAcceleration(0,200000)
		time.sleep(0.2)
		y = self.stepper.getCurrentPosition(0)
		self.stepper.setCurrentPosition(0,y)
		self.stepper.setVelocityLimit(0,self.gvel)
		self.stepper.setAcceleration(0,self.gacc)
		print self.stepper.getCurrentPosition(0)
		self.stepper.setCurrentPosition(0,0)

	def test2(self): #test code for findhome. rotates until it reaches 999999 steps or when enter is pressed.
		i = 0
		while True:
    			os.system('cls' if os.name == 'nt' else 'clear')
    			if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        			line = raw_input()
        			break
			self.stepper.setTargetPosition(0, 999999)
			print self.stepper.getCurrentPosition(0)
		print self.stepper.getCurrentPosition(0)
		self.stepper.setVelocityLimit(0,0)
		self.stepper.setAcceleration(0,200000)
		time.sleep(0.2)
		y = self.stepper.getCurrentPosition(0)
		self.stepper.setCurrentPosition(0,y)
		self.stepper.setVelocityLimit(0,self.gvel)
		self.stepper.setAcceleration(0,self.gacc)
		print self.stepper.getCurrentPosition(0)
		self.stepper.setCurrentPosition(0,0)

if __name__ == "__main__":
	p = FilterMotor()
	p.connDev()
	p.status()
	time.sleep(1)
	p.disconnDev()

