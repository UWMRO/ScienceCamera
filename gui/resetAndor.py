import subprocess
from subprocess import check_output
import os
import re

class resetAndor(object):

	def __init__(self):
		self.cwd = os.getcwd()
		self.bus = 0 #bus number
        	self.device = 0 #device number
        	self.foundStr = '' #parsed line with Andor ino
	
	#run lsusb in terminal, parse output and pull out bus and device numberes
	#for Andor, save globally
	def getInfo(self):
		devices = check_output('lsusb')
		devices = devices.split('\n')
		for usb in devices:
			if re.search('Andor',usb):
				self.foundStr = usb
		self.foundStr = self.foundStr.split(' ')
		self.bus = self.foundStr[1]
		self.device = self.foundStr[3]
	
	#use found Andor bus and device numbers to run usbreset and reset Andor
	def restart(self):
		resetString = ' /dev/bus/usb/' + str(self.bus) + '/' + str(self.device).strip(':')
		command = os.getcwd() + '/usbreset' + resetString
		os.system(command)

if __name__ == "__main__":
	g = resetAndor()
	g.getInfo()
	g.restart()
	print 'Andor has been reset.'
