#!/usr/bin/python2

from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import sys

from twisted.protocols import basic
from twisted.internet import protocol, reactor, threads

# For filter controls
from FilterMotor import *
import Queue
import thread
import threading


# port for filterwheel is 5503


class FilterWheelServer(basic.LineReceiver):
    def __init__(self):
	self.f = FilterMotor()
	self.fw = FilterWheelParser(self, self.f)
	self.f.connDev()

        # Pass protocol to FilterMotor.py
        self.f.motorProtocol = self


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

class FilterWheelParser(object):
    def __init__(self, protocol, f):
        #self.f = FilterMotor()
	self.f = f
        self.protocol = protocol


    def parse(self, input=None):
        print(input)
        input = input.split()
        if input[0] == 'disconnect':
            return self.f.disconnDev()
        if input[0] == 'status':
            return self.f.status()
        if input[0] == 'getFilter':
            return self.f.getFilterPosition()
	if input[0] == 'power':
	    return self.f.motorPower(bool(input[1]))
	if input[0] == 'move':
	    return "moved " + str(self.f.moveFilter(int(input[1])))
	if input[0] == 'home':
	    return self.f.home()
        if input[0] == 'test':
	    return 'test routine'
 

if __name__ == "__main__":
    #ep = Evora()
    #ep.startup()
    print ("You have just started the MRO Telescope Server\n"\
                "This product is currently under first year beta testing\n" \
                "Please Report any bugs to:\n" \
                "jlozo@uw.edu\n" \
                "jwhueh@uw.edu \n" \
                "Thank you and enjoy your science! \n\n"
		"You should now connect a client session to get started.")

    reactor.suggestThreadPoolSize(30)
    reactor.listenTCP(5503, FilterWheelClient())
    reactor.run()

