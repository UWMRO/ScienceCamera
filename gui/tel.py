import getpass
import sys
import telnetlib
import time

HOST = "localhost"

tn = telnetlib.Telnet(HOST,5502)
time.sleep(10)
tn.write("status\n")
time.sleep(10)
"""time.sleep(2)
tn.write("temp\n")
time.sleep(2)
tn.write("setTEC\n")
time.sleep(2)
for i in range (0,300):
        tn.write("expose flat 1 10 2 1\r\n")
	print 'exposing'
        time.sleep(10)
tn.write("shutdown\r\n")

tn.write("exit\n")"""
print tn.read_all()
telnet.sock.close()
