import subprocess
from subprocess import check_output
import os
import re

class resetAndor(object):

	def __init__(self):
		self.cwd = os.getcwd()
		self.bus = 0
        	self.device = 0
        	self.cwd = ''
        	self.foundStr = ''
	
	def getInfo(self):
		devices = check_output('lsusb')
		print devices
		devices = devices.split('\n')
		print devices
		for usb in devices:
			if re.search('Andor',usb):
				self.foundStr = usb
		self.foundStr = self.foundStr.split(' ')
		self.bus = self.foundStr[1]
		self.device = self.foundStr[3]

	def restart(self):
		resetString = ' /dev/bus/usb/' + str(self.bus) + '/' + str(self.device).strip(':')
		command = os.getcwd() + '/usbreset' + resetString
		print command
		print os.path.join(os.getcwd(),'usbreset') + resetString
		#subprocess.Popen(['sudo',os.path.join(os.getcwd(),'usbreset'),resetString])
		os.system(command)
if __name__ == "__main__":
	g = resetAndor()
	g.getInfo()
	g.restart()
	print 'Andor has been reset.'
