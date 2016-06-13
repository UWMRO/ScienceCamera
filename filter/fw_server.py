#!/usr/bin/python2

from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import sys

from twisted.protocols import basic
from twisted.internet import protocol, reactor, threads

# For filter controls
from FilterMotor import FilterMotor
import Queue
import thread
import threading


# port for filterwheel is 5503


class FilterWheelServer(basic.LineReceiver):
    def connectionMade(self):
        """
        If you send more than one line then the callback to start the gui will completely fail.
        """
        self.factory.clients.append(self)
        #self.sendMessage("Welcome to the Evora Server")
        #self.sendMessage("Starting camera")
        fw = FWParser(self)
        command = fw.parse("status") 
        self.sendMessage(str(command)) # activate the callback to give full control to the camera.

    def connectionLost(self, reason):
        #self.sendLine("Connection Lost")
        #if len(self.factory.clients) is 1:
        #    ep = EvoraParser()
        #    command = ep.parse("shutdown")
            #self.sendMessage(command)        
        self.factory.clients.remove(self)

    def lineReceived(self, line):
        print("received", line)
        fw = FilterWheelParser(self)
        d = threads.deferToThread(fw.parse, line)
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

## Evora Parser commands sent here from server where it envokes the camera commands.
class FilterWheelParser(object):
    def __init__(self, protocol):
        self.fw = FilterWheel()
        self.protocol = protocol

    def parse(self, input=None):
        print(input)
        input = input.split()
        if input[0] == 'connect':
            return self.fw.connDev()
        if input[0] == 'disconnect':
            return self.fw.disconnDev()
        if input[0] == 'status':        
            return self.fw.status()
        if input[0] == 'test':
	    return 'test routine'
 

if __name__ == "__main__":
    #ep = Evora()
    #ep.startup()
    reactor.suggestThreadPoolSize(30)
    reactor.listenTCP(5503, EvoraClient())
    reactor.run()

