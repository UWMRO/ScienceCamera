#!/usr/bin/env python2
from __future__ import print_function, division, absolute_import

from twisted.internet import defer, protocol, reactor, threads
from twisted.protocols import basic
from twisted.python import log

# FTP Client Things
from twisted.protocols.ftp import FTPFactory
from twisted.protocols.ftp import FTPFileListProtocol
from twisted.protocols.ftp import FTPClient

# GUI element imports
import AddLinearSpacer as als


#Global variables
ftp = None

class FileServer(basic.LineReceiver):
    """
    This is the Evora camera server code using Twisted's convienience object of basic.LineReceiver.
    When a line is recieved from the client it is sent to the parser to execute the camera commands
    and the resulting data is sent back to the client.  This a threaded server so that long
    running functions in the parser don't hang the whole server.
    """
    
    def connectionMade(self):
        """
        If you send more than one line then the callback to start the gui will completely fail.
        """
        self.factory.clients.append(self)
        self.sendMessage("Welcome to the file server") # activate the callback to give full control to the camera.

    def connectionLost(self, reason):
        """
        Adds connecting client to the list of existing clients.
        """
        self.factory.clients.remove(self)

    def lineReceived(self, line):
        """
        Called when server recieves a line. Runs the line through the parser and then
        sends the resulting data off.
        """
        print("received " + line)
        parser = Parser(self)
        results = parser.parse(line)
        self.sendData(results)

    def sendData(self, data):
        """
        Decorator method to self.sendMessage(...) so that it
        sends the resulting data to every connected client.
        """
        if data is not None:
            self.sendMessage(str(data))

    def sendMessage(self, message):
        """
        Sends message to every connect client.
        """
        for client in self.factory.clients:
            client.sendLine(message)

class FileServerClient(protocol.ServerFactory):
    """
    This makes up the twistedPython factory that defines the protocol and stores
    a list of the clients connect.
    """
    def __init__(self):
        self.protocol = FileServer
        self.clients = []

#    def buildProtocol(self, addr):
#        self.protocol = FileServer()
#        return self.protocol

    def clientConnectionLost(self, transport, reason):
        print("Connection to File server lost normally:", reason)

    def clientConnectionFailed(self, transport, reason):
        print("Connection failed:", reason)


class Parser(object):
    """
    This object parses incoming data lines from the client and executes the respective hardware
    driver code.
    """
    
    def __init__(self, protocol):
        """
        Trickles down the protocol for potential usage as well as defines an instance of Evora (the object
        that holds the driver code).
        """
        self.protocol = protocol

    def parse(self, input=None):
        """
        Receive an input and splitps it up and based on the first argument will execute the right method 
        (e.g. input=connect will run the Evora startup routine).
        """
        global ftp
        input = input.split()
        if input[0] == 'get':
            """
            Retrieve file.
            >>> get fileName saveDirectory saveName
            """
            serverImageName = input[1]
            savePath = input[2]
            saveName = input[3]
            #type = input[4]
            print(serverImageName, savePath, saveName)
            d = ftp.retrieveFile(serverImageName, als.FileBuffer(savePath, saveName), offset=0)
            d.addCallback(self.transferDone, file=savePath+saveName)
            d.addErrback(self.transferFail)
            return "Attempting to start transfer"

        if input[0] == 'test':

            ftp.pwd().addCallback(self.done)

    def done(self, msg):
        print(msg)
    def transferDone(self, msg, file):
        self.protocol.sendData("get %s" % file)

    def transferFail(self, msg):
        pass
        

class FileClient(FTPClient, object):

    def __init__(self, factory, username, password, passive):
        super(FileClient, self).__init__(username=username, password=password, passive=passive)
        # Set to not be passive ftp protocol, ie 1.
        self.factory = factory

    def connectionMade(self):
        global ftp
        ftp = self
        # Pass the protocol to the gui when connection is made to FTP Sever
        #self.factory.protocol = self
        # Main wx.Frame
        
        print("CONNECTION MADE")
        
        
class FileClientFactory(protocol.ClientFactory):
    def __init__(self):
        self.protocol = None
        #self.protocol = None
        #self.protocol = self.buildProtocol('localhost')

    def buildProtocol(self, addr):
        # The username and passwd are meaningless but needed
        user = 'anonymous'
        passwd = 'mro@uw.edu' # again this is meaningless
        self.protocol = FileClient(self, username=user, password=passwd, passive=1)
        return self.protocol
    
    def clientConnectionLost(self, transport, reason):
        print("Connection to FTP server lost normally:", reason)

    def clientConnectionFailed(self, transport, reason):
        print("Connection failed:", reason)


if __name__ == "__main__": 
    ftpFactory = FileClientFactory()

    fileServerFactory = FileServerClient()
    
    
    reactor.connectTCP(als.HEIMDALL_IP, als.FTP_TRANSFER_PORT, ftpFactory)     
    reactor.listenTCP(als.FTP_GET_PORT, fileServerFactory)

    reactor.run()

    
