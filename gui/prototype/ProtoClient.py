from twisted.internet.protocol import Factory
from twisted.internet import reactor
from protoServer import ProtoServer


class ProtoClient(Factory):
	"""
	Inherit Factory to be able to give commands
	"""

	def __init__(self):
		self.x = "Stuff"

	def buildProtocol(self, addr):
		return ProtoServer()

if __name__=="__main__":
	reactor.listenTCP(5502, ProtoClient())
	reactor.run()
