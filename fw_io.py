#! /usr/bin/python

"""
fw_io.py

This program is designed to read in data from an arduino.  
Specifically this is program interfaces to the arduino on the
cloud camera.  Functionality includes reading the temperature,
 humidity, and light levels.

TODO:
finish interface

Usage:

Options:


"""

__author__ = ["Joseph Huehnerhoff"]
__license__ = "GPL"
__version__ = "0.1"
__maintainer__ = "Joseph Huehnerhoff"
__email__ = ""
__status__ = "Developement"

import serial
import time

class FWIO():
    def __init__(self):
	self.ser = None
	self.serPort = '/dev/ttyACM0'

    def log(self):
    	"""
    	Check the serial port for data
    	and write any data with a timestamp
    	to the savefile
    	"""
    	data = ser.readline()
    	f = open(savefile, 'a')
    	f.write(str(time.strftime("%H%M%S"))+","+str(data))
    	f.close()

    def openPort(self):
	""" open the serial port for communication with the arduino"""
        self.ser=serial.Serial(self.serPort, 9600, timeout = 2)
        return

    def closePort(self):
	""" close the serial port connection to the arduino"""
        self.ser.close()
        return

    def readSer(self):
	""" Read in the arduino output, parse, and return something useful
	Arguments:
		None
	Returns:
		s (string): parsed serial output
	"""
        s = self.ser.readline().rstrip('\r\n')
        return s

    def getStatus(self):
	"""returns the dome metrology in format humidity,temp,pos
	Arguments:
		None
	Returns:
		

	"""
	self.ser.write('s')
	line = self.readSer()
	l = line.split(',')
	return l

if __name__ == "__main__":
	c = FWIO()
	c.openPort()
	time.sleep(2)
	x = 0	
	for x in range(100):
		print c.getStatus()
	time.sleep(1)
	c.closePort()
