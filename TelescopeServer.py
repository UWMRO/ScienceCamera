#!/usr/bin/python3

from twisted.protocols import basic
from twisted.internet import protocol, reactor, threads

from FilterWheel import *

# Port for filterwheel is 5503

class TelescopeServer(basic.LineReceiver):
    def __init__(self):
        self.fw = FilterWheel(self) #Argument of self passes protocol to FilterWheel.py
        self.tp = TelescopeParser(self, self.fw)

    def connectionMade(self):
        """
        If you send more than one line then the callback to start the gui will completely fail.
        """
        self.factory.clients.append(self)

    def connectionLost(self, reason):
        self.factory.clients.remove(self)
        self.fw.disconnDev()

    def lineReceived(self, line):
        print("received", line)
        d = threads.deferToThread(self.tp.parse, line)
        d.addCallback(self.sendData)

    def sendData(self, data):
        if data is not None:
            self.sendMessage(str(data))

    def sendMessage(self, message):
        for client in self.factory.clients:
            client.sendLine(message)

class TelescopeClient(protocol.ServerFactory):
    protocol = TelescopeServer
    clients = []

class TelescopeParser():
    def __init__(self, protocol, fw):
        self.fw = fw
        self.protocol = protocol

    def parse(self, userInput = None):
        userInput = userInput.split()
        
        if input[0] == 'disconnect':
            return self.fw.disconnDev()
        elif input[0] == 'status':
            return self.fw.dict
        elif input[0] == 'move':
    	    return 'moved ' + str(self.fw.moveFilter(int(userInput[1])))
        elif input[0] == 'home':
    	    return self.fw.home()
        else:
            return "There's no command for that input!"

if __name__ == "__main__":
    #ep = Evora()
    #ep.startup()
    print("You have started the MRO Telescope Server!\n \
          You should now connect a client session to get started.")

    reactor.suggestThreadPoolSize(30)
    reactor.listenTCP(5503, TelescopeClient())
    reactor.run()