#!/usr/bin/env python

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
import serial
import numpy as np


class FilterMotor(object):
	def __init__(self):
                self.motorProtocol = None
		self.stepper = None

                # code brought in my OJF
                self.SerialPort = None
                self.SerialPortAddress = '/dev/ttyACM0'
                
		self.dict = {"velocity":None, "amp":None, "acceleration":None, "currentPos":None, "power":None, "hall":None, "commandedPos":None, "filterDelta":6860, "ID":None, "home":False, "filterPos":None, "filterCount":None, "moving":False}

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

		self.setParm(20000,5000,0.9)

                # code brought in by OJF
                self.SerialPort=serial.Serial(self.SerialPortAddress, 9600, timeout = 2)

		time.sleep(2)
		print "Stepper Driver Connected"
		self.status()
		return 1

	def disconnDev(self):
		time.sleep(1)
		self.motorPower(False)
		self.stepper.closePhidget()
		print "Stepper Driver Disconnected"
                # line added by OJF
                self.SerialPort.close()
		return

	def motorPower(self, val = False):
		self.stepper.setEngaged(0,val)
		if val == False:
			self.dict['moving'] = False
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
                
                # request Hall effect sensor from Arduino
                self.SerialPort.write('s')
                self.dict['hall'] = self.SerialPort.readline().rstrip('\r\n').split(',')

		self.dict['filterPos'] = int(self.dict['currentPos'])/int(self.dict['filterDelta'])
		return self.dict

	def setPos(self, pos = None):
		self.stepper.setCurrentPosition(0, int(pos))	
		return

	def moveMotor(self, pos = None):
		self.dict['moving'] = True
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
		self.dict['moving'] = True
		delta = int(self.dict['filterDelta'])
		print "Moving to filter position %d" % num
		tpos = num*delta
		self.moveMotor(tpos)
		while tpos != self.dict['currentPos']:
			self.status()
			print 'moving', self.dict['currentPos']
			time.sleep(1)
		if tpos == self.dict['currentPos']:
			self.status()
			if int(self.dict['hall'][0]) == 0:
				print 'move complete', self.dict
				self.motorPower(False)
				print self.status()
				return True
			if int(self.dict['hall'][0]) == 1:
				print 'move incomplete, intiate find', self.dict
				results = self.findPos()
				self.motorStop()
				print self.status()
                                if(results == True):
                                        return True  # Adjustment successful
                                else:
                                        return False  # Adjustment failed


	def findPos(self):
                self.motorProtocol.sendData("findPos 1")  # Sends to server that it is addjusting filter position
		startPos = self.dict['currentPos']
		for x in range(0,200,25):
			newPos = x + startPos
			self.moveMotor(newPos)
			time.sleep(1)
			self.status()
			if int(self.dict['hall'][0]) == 0:
				print 'positive position found', self.dict
				self.setPos(int(startPos))
				return True  # Successfully found filter position
			
		for x in range(0,200,25):
                        newPos = x - startPos
                        self.moveMotor(newPos)
                        time.sleep(1)
                        self.status()
                        if int(self.dict['hall'][0]) == 0:
                                print 'negative position found', self.dict
				self.setPos(int(startPos))
                                return True  # Successfully found filter position
		self.motorStop()
                return False  # For when even findPos fails


        def getFilterPosition(self):
                """
                Note: Evora Gui cannot handle a dictionary that is returned in string 
                      format so instead of calling status and getting filter position
                      from there this is called instead.
                Pre:  Takes in nothing.
                Post: Returns the filter position as an integer between 0 and 5 that will
                      be parsed.
                """
                filter = int(self.dict['currentPos'])/int(self.dict['filterDelta'])
                return "getFilter " + str(filter) 

	def motorStop(self):
		self.motorPower(False)
		self.dict['moving'] = False
		return

	def home(self): 
                """
                Return 1 for True and 0 for False
                """
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
							print 'first pass', self.status()
							previousPos = self.dict['currentPos']
						if  self.dict['currentPos'] - previousPos >  3000:
							pastHome = pastHome + 1
							print 'second pass', self.status()
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
			print "==>FAILED TO HOME!!!!!"
			return "home 0"  # returning a boolean has some issues when coming out client side
		self.motorPower(False)
		self.dict['filterCount'] = 0
		print "==> HOME SUCCESSFUL"
		return "home 1"  # returning a boolean has some issues when coming out client side

if __name__ == "__main__":
	p = FilterMotor()
	p.connDev()
	time.sleep(.5)
	print p.home()
	time.sleep(.5)
	p.disconnDev()

