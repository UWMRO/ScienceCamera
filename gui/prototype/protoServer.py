import numpy as np
from twisted.protocols import basic
from twisted.internet import protocol, reactor

#import ProtoParser

# port for evora is 5502

class ProtoServer(basic.LineReceiver):

	def connectionMade(self):
		self.sendLine("Welcome to the Evora Server")
		self.factory.clients.append(self)

	def connectionLost(self, reason):
		self.sendLine("Connection Lost")
		self.factory.clients.remove(self)


	def lineReceived(self, line):
		print "received", line
		PP = ProtoParser()
		command = PP.parse(line)
		if command != None:
			self.sendMessage(command)

	def sendMessage(self, message):
		for client in self.factory.clients:
			client.sendLine(message)




class ProtoClient(protocol.ServerFactory):
	protocol = ProtoServer
	clients = []


class ProtoParser():
	def __init__(self):
		print "Entered the parser"

	def parse(self, command = None):
		#print command
		command = command.split() # split the evora command by white space.
		if command[0] == "expose":
			return "Exposing with name " + command[1] + " for " + command[2] + " seconds with " + command[3] + " binning, " + command[4] + " exposure type, and " + command[5] + " image type."
		if command[0] == "temperature":
			return "Changing temperature to " + command[1] + " C"

if __name__=="__main__":
	reactor.listenTCP(5502, ProtoClient())
	reactor.run()
