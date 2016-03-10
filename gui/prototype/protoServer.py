import numpy as np
from twisted.protocols import basic
from twisted.internet import protocol, reactor

import ProtoParser

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
		PP = ProtoParser.ProtoParser()
		command = PP.parse(line)
		if command != None:
			self.sendMessage(command)

	def sendMessage(self, message):
		for client in self.factory.clients:
			client.sendLine(message)







class ProtoClient(protocol.ServerFactory):
	"""
	Inherit Factory to be able to give commands
	"""

	protocol = ProtoServer
	clients = []



if __name__=="__main__":
	reactor.listenTCP(5502, ProtoClient())
	reactor.run()
