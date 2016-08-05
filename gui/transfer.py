#! /user/bin/python
from __future__ import division  # this handles truncation 10/3. ==> 10/3
from __future__ import print_function
from __future__ import absolute_import # where it looks in the path for modules

"""
transfer.py
Upload Tool using Paramiko
"""

__author__ = "Joseph Huehnerhoff"
__copyright__ = "NA"
__credits__ = [""]
__license__ = "GPL"
__version__ = "0.1"
__maintainer__ = "NA"
__email__ = "NA"
__status__ = "Developement"

import paramiko
import time
import os

class transfer(object):
	def __init__(self):
		self.parm = self.retrieveParm()
		self.ssh = None
		self.ftp = None

	def openConnection(self, server = None, user = None):
		self.ssh = paramiko.SSHClient()
		self.ssh.set_missing_host_key_policy(
    		paramiko.AutoAddPolicy())
		self.ssh.connect(self.parm['server'], username=self.parm['user'])
		self.ftp = self.ssh.open_sftp()

	def uploadFile(self, f_in):
		#add changdir to public_html
		self.ftp.put(os.path.join(os.getcwd(), f_in), os.path.join(self.parm['server_dir'], f_in))
		return

	def closeConnection(self):
		self.ftp.close()
		self.ssh.close()
		return

	def retrieveParm(self, f_loc = None):
		dict = {}
		f_in = open(os.path.join(os.getcwd(), 'transfer.init'),'r')
		for line in f_in:
			l = line.split()
			dict[l[0]] = l[1]
		f_in.close()
		return dict

if __name__ == "__main__":
	t = transfer()
	t.openConnection()
	t.uploadFile('make')
	t.closeConnection()
