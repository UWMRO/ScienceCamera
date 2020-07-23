#!/usr/bin/python3

from FilterWheel import *
from twisted.internet import protocol, reactor, threads
from twisted.protocols import basic

# Port for filterwheel is 5503

class TelescopeServer(basic.LineReceiver):
    def __init__(self):
        'Creates a filterwheel motor.'
        self.fw = FilterWheel()

    def connectionMade(self):
        '''Opens communication with Evora. If more than one line is sent, the callback 
        to start the gui will fail.'''
        self.factory.clients.append(self)

    def connectionLost(self, reason):
        'Disconnects filterwheel motor and removes connection with Evora.'
        self.fw.disconnDev()
        self.factory.clients.remove(self)

    def lineReceived(self, line):
        'Parses a message, and sends a message back to Evora.'
        print("received", line)
        d = threads.deferToThread(self.parse, line)
        d.addCallback(self.sendData)

    def sendData(self, data):
        'Used to send a message to Evora.'
        if data is not None:
            for client in self.factory.clients:
                client.sendLine(str(data))
                
    def parse(self, message = None):
        '''Parses a message and returns a message to be sent back to Evora, which
        expects specific return messages.'''
        message = message.split()
        
        if message[0] == 'home':
    	    return self.fw.home()
        if message[0] == 'move':
    	    return 'moved ' + self.fw.moveFilter(int(message[1]))
        if message[0] == 'getFilter':
            return 'getFilter ' + self.fw.getFilterPos()

class TelescopeClient(protocol.ServerFactory):
    protocol = TelescopeServer
    clients = []
        
if __name__ == "__main__":
    print("You have started the MRO Telescope Server!\n \
          You should now connect a client session to get started.")

    reactor.suggestThreadPoolSize(30)
    reactor.listenTCP(5503, TelescopeClient())
    reactor.run()