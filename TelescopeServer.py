#!/usr/bin/python3

from twisted.protocols import basic
from twisted.internet import protocol, reactor, threads

from FilterWheel import *

# Port for filterwheel is 5503

class FilterWheelServer(basic.LineReceiver):
    def __init__(self):
        self.f = FilterMotor(self) #Argument of self passes protocol to FilterMotor.py
        self.fw = FilterWheelParser(self, self.f)

    def connectionMade(self):
        """
        If you send more than one line then the callback to start the gui will completely fail.
        """
        self.factory.clients.append(self)

    def connectionLost(self, reason):
        self.factory.clients.remove(self)
        self.f.disconnDev()

    def lineReceived(self, line):
        print("received", line)
        d = threads.deferToThread(self.fw.parse, line)
        d.addCallback(self.sendData)

    def sendData(self, data):
        if data is not None:
            self.sendMessage(str(data))

    def sendMessage(self, message):
        for client in self.factory.clients:
            client.sendLine(message)

class FilterWheelClient(protocol.ServerFactory):
    protocol = FilterWheelServer
    clients = []

class FilterWheelParser():
    def __init__(self, protocol, f):
        self.f = f
        self.protocol = protocol

    def parse(self, userInput = None):
        userInput = userInput.split()
        
        if input[0] == 'disconnect':
            return self.f.disconnDev()
        elif input[0] == 'status':
            return self.f.dict
        elif input[0] == 'move':
    	    return 'moved ' + str(self.f.moveFilter(int(userInput[1])))
        elif input[0] == 'home':
    	    return self.f.home()
        else:
            return "There's no command for that input!"

if __name__ == "__main__":
    #ep = Evora()
    #ep.startup()
    print("You have started the MRO Telescope Server!\n \
          You should now connect a client session to get started.")

    reactor.suggestThreadPoolSize(30)
    reactor.listenTCP(5503, FilterWheelClient())
    reactor.run()