
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.


"""
An example client. Run simpleserv.py first before running this.
"""
from __future__ import print_function
import time
from twisted.internet import reactor, protocol
#import twisted.protocols.basic import LineReceiver

# a client protocol

class EchoClient(protocol.Protocol):
    """Once connected, send a message, then print the result."""
    
    def connectionMade(self):
	self.transport.write("shutdown\r\n")
	self.transport.write('temp\r\n')

    def dataReceived(self, data):
        "As soon as any data is received, write it back."
        print("Server said:", data)
	"""if data == "":
        	self.transport.write('status')
        	self.transport.write('temp')
        	self.transport.write("setTEC\r\n")
        	for i in range (0,300):
                	self.transport.write("expose\r\n")
                	time.sleep(10)
        	self.transport.write("shutdown\r\n")"""
	

    def connectionLost(self, reason):
        print("connection lost")

class EchoFactory(protocol.ClientFactory):
    protocol = EchoClient

    def clientConnectionFailed(self, connector, reason):
        print("Connection failed - goodbye!")
        reactor.stop()
    
    def clientConnectionLost(self, connector, reason):
        print("Connection lost - goodbye!")
        reactor.stop()


# this connects the protocol to a server running on port 5502
def main():
    f = EchoFactory()
    reactor.connectTCP("localhost", 5502, f)
    reactor.run()

# this only runs if the module was *not* imported
if __name__ == '__main__':
    main()

