"""The most basic chat protocol possible.

run me with twistd -n -y camera_reactor.py, and then connect with multiple
telnet clients to port 5502 
"""

from twisted.protocols import basic
import evora_parser2

class CameraReciever(basic.LineReceiver):
    def connectionMade(self):
        print "Got new client!"
        self.factory.clients.append(self)

    def connectionLost(self, reason):
        print "Lost a client!"
        self.factory.clients.remove(self)

    def lineReceived(self, line):
        print "received", repr(line)
	ep = evora_parser2.Parser()	
	ret = ep.parse(str(line))
	if ret != None:
        	for c in self.factory.clients:
        		c.message(str(ret))

    def message(self, message):
        self.transport.write(message + '\n')


from twisted.internet import protocol
from twisted.application import service, internet

factory = protocol.ServerFactory()
factory.protocol = CameraReciever
factory.clients = []

application = service.Application("Evora")
internet.TCPServer(5502, factory).setServiceParent(application)
