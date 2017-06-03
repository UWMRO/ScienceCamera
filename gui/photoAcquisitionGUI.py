#!/usr/bin/env python2
from __future__ import absolute_import, division, print_function

import os
import Queue
import signal
import subprocess
import sys
import thread
import threading
import webbrowser

import wx
import matplotlib
matplotlib.use("WXAgg")
import matplotlib.pyplot as plt
import numpy as np

from astropy.io import fits
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2Wx as Toolbar
from scipy import stats

# always goes after wxreactor install

from twisted.internet import wxreactor
wxreactor.install()
from twisted.internet import defer, protocol, reactor, threads
from twisted.protocols import basic
from twisted.python import log

# FTP Client Things
from twisted.protocols.ftp import FTPFactory
from twisted.protocols.ftp import FTPFileListProtocol
from twisted.protocols.ftp import FTPClient

# GUI element imports
import acquisitionClasses as ac
import AddLinearSpacer as als
import controlClasses as cc
import EnhancedStatusBar
import logClasses as lc
import MyLogger
import scriptingClasses as sc

"""
# Comment on documentation:
# When reading the doc strings if "Pre:" is present then this stands for "precondition", or the conditions in order to invoke something.
# Oppositely, "Post:" stands for "postcondition" and states what is returned by the method.
"""

__author__ = "Tristan J. Hillis"


## Global Variables
app = None  # reference to Evora app
port_dict = {}  # dictionary storing different connections that may be open.
ftpClientProc = None
logger = MyLogger.myLogger("photoAcquisitionGUI.py", "client")

## Getting to parents (i.e. different classes)
# Three parents will get to the Evora class and out of the notebook


# Frame class.
class Evora(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, None, -1, "Evora Acquisition GUI", size=(600, 450))

        # width and height in pixels
        self.width = 600
        self.height = 450
        
        self.protocol = None # client protocol
        self.ftp = None
        self.connection = None
        self.connected = False  # keeps track of whether the gui is connect to camera
        self.active_threads = {}  # dict of the active threads
        self.imageOpen = False # keep track of whether the image window is open
        self.window = None # holds the image window
        self.logFunction = None

        panel = wx.Panel(self)
        notebook = wx.Notebook(panel)

        notebook.parent = self # to reach variables in Evora() from the notebooks

        # define the each tab
        page1 = TakeImage(notebook)
        #page2 = OtherParams(notebook)
        page2 = Scripting(notebook)
        page3 = Log(notebook)

        # add each tab to the notebook
        notebook.AddPage(page1, "Imaging")
        #notebook.AddPage(page2, "Controls")
        notebook.AddPage(page2, "Scripting")
        notebook.AddPage(page3, "Log")

        # make instances of the tabs to access variables within them
        self.takeImage = notebook.GetPage(0) # Gives access to TakeImage class
        #self.otherParams = notebook.GetPage(1)
        self.scripting = notebook.GetPage(1) # Gives access to Scripting class
        self.log = notebook.GetPage(2) # Gives access to Log class

        # Widgets

        #
        self.binning = "2" # starts in 2x2 binning
        self.readoutIndex = 3  # default readout speed is 3 or 0.5 MHz

        ## Menu
        self.menuBar = wx.MenuBar()

        ## Sub menus
        filterSub = wx.Menu()
        filterSub.Append(1110, "&Connect", "Connect to the filter")
        filterSub.Append(1112, "&Disconnect", "Disconnect from filter")
        filterSub.Append(1111, "&Refresh", "Refresh filter list")
        filterSub.Enable(1112, False)

        binningSub = wx.Menu()
        binningSub.Append(1120, "1x1", "Set CCD readout binning", kind=wx.ITEM_RADIO)
        binningSub.Append(1121, "2x2", "Set CCD readout binning", kind=wx.ITEM_RADIO)
        binningSub.Check(id=1121, check=True)

        cameraSub = wx.Menu()
        #cameraSub.Append(1133, "&Startup", "Start the camera")
        cameraSub.Append(1130, "&Connect", "Connect to camera")
        cameraSub.Append(1131, "&Disconnect", "Disconnect the camera")
        cameraSub.Append(1132, "&Shutdown", "Shutdown and disconnect from camera")
        cameraSub.Enable(1131, False)
        cameraSub.Enable(1132, False)

        readoutSub = wx.Menu()
        readoutSub.Append(1140, "0.05 MHz", "6 seconds", kind=wx.ITEM_RADIO)
        readoutSub.Append(1141, "1.0 MHz", "X seconds", kind=wx.ITEM_RADIO)
        readoutSub.Append(1142, "3.0 MHz", "X seconds", kind=wx.ITEM_RADIO)
        readoutSub.Append(1143, "5.0 MHz", "X seconds", kind=wx.ITEM_RADIO)

        # create main menus
        fileMenu = wx.Menu()
        #fileMenu.AppendMenu(1001, "&Filter", filterSub)
        fileMenu.AppendMenu(1002, "&Binning", binningSub)
        fileMenu.AppendMenu(1004, "&Readout", readoutSub)
        #fileMenu.AppendMenu(1003, "&Camera", cameraSub)
        fileMenu.Append(1000, "&Exit", "Quit from Evora")

        viewMenu = wx.Menu()
        viewMenu.Append(1200, "&Image", "Open Image Window")

        helpMenu = wx.Menu()
        helpMenu.Append(1300, "&Help")

        # add to menu bar
        self.menuBar.Append(fileMenu, "&File")
        self.menuBar.Append(cameraSub, "&Camera")
        self.menuBar.Append(filterSub, "F&ilter")
        self.menuBar.Append(viewMenu, "&View")
        self.menuBar.Append(helpMenu, "&Help")
        # instantiate menubar
        self.SetMenuBar(self.menuBar)

        ## Status Bar:  include temperature, binning type, gauge for exposure
        self.stats = EnhancedStatusBar.EnhancedStatusBar(self)
        self.stats.SetSize((23,-1))
        self.stats.SetFieldsCount(4)
        #self.stats.SetStatusWidths([int(self.width*(1/10)),int(self.width*(2/10)),int(self.width*(5/10)),int(self.width*(5/10)),int(self.width*(5/10))])
        self.SetStatusBar(self.stats)
        self.stats.SetStatusText("Current Temp:  ... C", 0)

        self.stats.SetStatusText("  Exp:", 1)
        self.stats.SetStatusText("   Binning Type: 2x2", 2)
        self.stats.SetStatusText("Filter: offline", 3)
        self.expGauge = wx.Gauge(self.stats, id=1, range=100, size=(100, -1))
        self.stats.AddWidget(self.expGauge, pos=1, horizontalalignment=EnhancedStatusBar.ESB_ALIGN_RIGHT)
        
        # size panels
        sizer = wx.BoxSizer()
        sizer.Add(notebook, 1, wx.EXPAND)

        ## Bindings
        self.Bind(wx.EVT_MENU, self.openImage, id=1200)
        self.Bind(wx.EVT_MENU, self.onClose, id=1000)
        self.Bind(wx.EVT_MENU, self.onHelp, id=1300)
        self.Bind(wx.EVT_MENU, self.onRefresh, id=1111)
        self.Bind(wx.EVT_MENU, self.on1x1, id=1120)
        self.Bind(wx.EVT_MENU, self.on2x2, id=1121)
        self.Bind(wx.EVT_MENU, self.onReadTimeSelect, id=1140)
        self.Bind(wx.EVT_MENU, self.onReadTimeSelect, id=1141)
        self.Bind(wx.EVT_MENU, self.onReadTimeSelect, id=1142)
        self.Bind(wx.EVT_MENU, self.onReadTimeSelect, id=1143)
        self.Bind(wx.EVT_MENU, self.onConnect, id=1130)
        self.Bind(wx.EVT_MENU, self.onDisconnect, id=1131)
        self.Bind(wx.EVT_MENU, self.onShutdown, id=1132)

        self.Bind(wx.EVT_MENU, self.onFilterConnect, id=1110)
        self.Bind(wx.EVT_MENU, self.onRefresh, id=1111)
        self.Bind(wx.EVT_MENU, self.onFilterDisconnect, id=1112)
        self.Bind(wx.EVT_MENU, self.onHelp, id=1300)
        #self.Bind(wx.EVT_MENU, self.onStartup, id=1133)
        self.Bind(wx.EVT_CLOSE, self.onClose)

        #wx.EVT_CLOSE(self, lambda evt: reactor.stop())

        self.disableButtons("evora", True)

        # Add and set icon
        ico = wx.Icon("evora_logo_circ.ico", wx.BITMAP_TYPE_ICO)
        self.SetIcon(ico)

        panel.SetSizer(sizer)
        panel.Layout()
  
    ## Keep an eye on memory (i.e. make sure it doesn't increase the more images are ploted).  This could cause memory usage to increase
    ## with newly loaded images when using the evora camera.
    def openImage(self, event):
        """
        This opens up the image window when selected in the drop down menu.
        """
        self.window = ImageWindow(self)
        self.window.Show()
        self.imageOpen = True
        logger.info("Opening image window.")

    def onClose(self, event):
        """
        When the exit is selected in the Evora File menu then it will ask if you are sure and subsequently close the
        GUI down.
        """
        dialog = wx.MessageDialog(None, "Close Evora GUI?", "Closing Evora", wx.OK | wx.CANCEL|wx.ICON_QUESTION)
        answer = dialog.ShowModal()
        dialog.Destroy()
        
        if answer == wx.ID_OK:
            logger.info("Closing down Evora GUI")
            self.quit()

        else:
            logger.info("Quit called but not closing.")
    
    def quit(self):
        """
        Helper method that handles properly closing the GUI.
        """
        if self.connected:
            logger.info("killing E. server connection in quit method")
            self.connection.disconnect()
        
        filterInstance = self.takeImage.filterInstance
        if(filterInstance.filterConnection):
            logger.info("killing F. server connection")
            port_dict.pop('5503').disconnect()

        # Kill transfer client
        os.killpg(os.getpgid(ftpClientProc.pid), signal.SIGTERM)
            
        if(self.imageOpen):
            logger.info("destroying image frame")
            self.imageOpen = False
            self.window.panel.closeFig()
            self.window.Destroy()
        
        self.Destroy()
        reactor.callFromThread(reactor.stop)  # Important to call like this else GUI hangs when trying to destroy it.
        logger.info("reactor stopped, finished quitting")

    def onHelp(self, event):
        """
        Pre: Press the "Help" menu option.
        Post: Opens up the Evora documentation section of the MRO website.
        """
        logger.info("opening web browser for help")
        webbrowser.open("https://sites.google.com/a/uw.edu/mro/documentation/evora")
        
    def onRefresh(self, event):
        """
        This will simply refresh the filter list so that the menu gets displayed correctly.  
        This is should only be used when the file "filter.txt" has been edited.
        """
        self.takeImage.filterInstance.refreshList()

    def on1x1(self, event):
        """
        Activates when 1x1 is selected in the binning menu under file.
        """
        logger.debug("setting binning type to 1x1")
        self.binning = "1"
        self.stats.SetStatusText("Binning Type: 1x1", 2)

    def on2x2(self, event):
        """
        Activates when 2x2 is selected in the binning menu under file.
        """
        logger.debug("setting binning type to 2x2")
        self.binning = "2"
        self.stats.SetStatusText("Binning Type: 2x2", 2)
        
    def onReadTimeSelect(self, event):
        id = event.GetId()
        if id == 1140:
            self.readoutIndex = 3
        if id == 1141:
            self.readoutIndex = 2
        if id == 1142:
            self.readoutIndex = 1
        if id == 1143:
            self.readoutIndex = 0
        logger.debug("setting readout index to index " + str(self.readoutIndex))

    def onConnect(self, event):
        """
        When connect is selected under the Camera menu this will set twisted to connect to port 5502
        """
        global port_dict, ftpClientProc
        logger.info("Connect command pressed")
        #reactor.run()
        #self.connection = reactor.connectTCP("localhost", 5502, EvoraClient(app.frame1))
        # add filter connection
        self.connection = port_dict[str(als.CAMERA_PORT)] = reactor.connectTCP(als.HEIMDALL_IP, als.CAMERA_PORT, EvoraClient(app.frame1))
        #port_dict[str(als.FTP_TRANSFER_PORT)] = reactor.connectTCP(als.HEIMDALL_IP, als.FTP_TRANSFER_PORT, FileClientFactory(app.frame1))
        port_dict[str(als.FTP_GET_PORT)] = reactor.connectTCP('localhost', als.FTP_GET_PORT, TransferClient(app.frame1))
        ftpClientProc = subprocess.Popen("./transferImages.py", shell=True, preexec_fn=os.setsid)
        

    def onConnectCallback(self, msg):
        """
        When a connection is made successfully the server sends a status which goes throught this.
        If the camera status is uninitialized then it runs the startup routine else it sets the state
        of the GUI to connect..
        """
        #msg = args[0]
        #thread = args[1]

        logger.debug(msg + " Startup callback entered")
        self.connected = True

        # get the number of clients
        status = int(msg.split(",")[0])

        self.logFunction = self.logMain
        logString = als.getLogString('status ' + str(status), 'post')
        self.logMethod(self.logFunction, logString)

        logger.debug("status from connect callback: " + str(status))

        if(status == 20075):  # camera is uninitialized
            d = self.protocol.sendCommand("connect")
            d.addCallback(self.callStartup)
            
        elif(status == 20002):  # if camera is already initialized then start server like regular
            # start temperature thread
            t = threading.Thread(target=self.takeImage.tempInstance.watchTemp, args=(), name="temp thread")
            self.takeImage.tempInstance.isConnected = True # setups infinite loop in watchTemp method
            t.daemon = True
            
            # Enable disconnect and shutdown and disable connect menu items
            self.enableConnections(False, True, True)
            self.disableButtons("connect", False)

            t.start()
            self.active_threads["temp"] = t
            
        else: # camera drivers are broken needs reinstall?
            pass

    def callStartup(self, msg):
        """
        When connect is sent to the server and is done this will set the state of the GUI.
        """
        self.logFunction = self.logMain
        logString = als.getLogString('connect ' + msg, 'post')
        self.logMethod(self.logFunction, logString)

        result = int(msg)

        self.connected = True # boolean to tell if connected to server
        self.enableConnections(False, True, True) # grey and un-grey camera menu options
        self.disableButtons("connect", False) # enable gui functionality
        self.takeImage.tempInstance.isConnected = True # setups infinite loop in watchTemp method
        t = threading.Thread(target=self.takeImage.tempInstance.watchTemp, args=(), name="temp thread")
        t.daemon = True
        t.start()
        self.active_threads["temp"] = t

        logger.info("Started up from callStartup method")
    
    def onDisconnect(self, event):
        """
        Called when disconnect is chosen from the Camera menu.
        """
        logger.info("Disconnect command pressed")
        self.takeImage.tempInstance.isConnected = False # closes infinite loop in watchTemp method

        # Update temperature bitmap in status bar.
        bitmap = wx.StaticBitmap(self.stats, -1, size=(90, 17))
        self.stats.AddWidget(bitmap, pos=0, horizontalalignment=EnhancedStatusBar.ESB_ALIGN_RIGHT)
        self.stats.SetStatusText("      Temp:  ... C", 0)
        
        self.joinThreads("temp", demonized=True)
        self.connection.disconnect() # this is the acutal disconnection from the server'
        ftp = port_dict['5505']
        ftp.disconnect()
        
        self.connected = False
        self.enableConnections(True, False, False)
        self.disableButtons('disconnect', True)

        self.takeImage.tempInstance.current_mode = None

    def onShutdown(self, event):
        """
        Runs when camera shutdown command is pressed in the Camera menu.  Checks to see if the camera temp is 
        above zero.  If so it warns the user.  If the option to shutdown is reached then tells the camera
        to start the shutdown routine.
        """
        if self.protocol is not None:
            temp = self.takeImage.tempInstance.currTemp
            
            if temp < 0:
                dialog = wx.MessageDialog(None, "Temperature is below 0 are you sure you want to shutdown the camera.", "", \
                                          wx.OK | wx.CANCEL | wx.ICON_QUESTION)

                answer = dialog.ShowModal()
                dialog.Destroy()
                if(answer == wx.ID_OK):
                    logger.info("Shutting down camera")
                    d = self.protocol.sendCommand("shutdown")
                    d.addCallback(self.callShutdown)
                    self.disableButtons('shutdown', True)
                    
            else:
                d = self.protocol.sendCommand("shutdown")
                d.addCallback(self.callShutdown)
                self.disableButtons('shutdown', True)

    def callShutdown(self, msg):
        """
        When the camera sends it has shutdown successfully then this runs and locks down the GUI.
        """
        self.logFunction = self.logMain
        logString = als.getLogString("shutdown " + msg, 'post')
        self.logMethod(self.logFunction, logString)
        
        self.takeImage.tempInstance.isConnected = False

        bitmap = wx.StaticBitmap(self.stats, -1, size=(90, 17))
        self.stats.AddWidget(bitmap, pos=0, horizontalalignment=EnhancedStatusBar.ESB_ALIGN_RIGHT)
        self.stats.SetStatusText("Current Temp:            ... C", 0)

        self.joinThreads("temp", demonized=False)
        self.connection.disconnect()
        self.connected = False
        self.enableConnections(True, False, False)

    def enableConnections(self, con, discon, shut):
        """
        This is used to enable the Connect, Disconnect, and Shutdown menu options in Camera fast. 
        """
        # get camera menu
        cameraSub = self.menuBar.GetMenu(1)
        
        cameraSub.Enable(1130, con)
        cameraSub.Enable(1131, discon)
        cameraSub.Enable(1132, shut)

    def disableButtons(self, method, boolean):
        """
        Used to lock down GUI or not.
        """
        # Diable GUI functionality (expose, stop, cool, warmup, rotate to)
        boolean = not boolean
        self.takeImage.exposureInstance.expButton.Enable(boolean)
        
        self.takeImage.tempInstance.tempButton.Enable(boolean)
        if method != 'connect':
            self.takeImage.tempInstance.stopCool.Enable(boolean)


    def onFilterConnect(self, event):
        """
        When 'Connect' is pressed in the filter sub-menu of file this will run the initialization process for the filter.
        The server will will start the filter motor and then use the connect function
        """        
        # send command on filter setup
        logger.info("Connect pressed in Filter menu")
        port_dict[str(als.FILTER_PORT)] = reactor.connectTCP(als.FILTER_PI_IP, als.FILTER_PORT, FilterClient(app.frame1))

        # lock the connect button up and unlock the disconnect
        filterSub = self.menuBar.GetMenu(2)  # second index

        # change the status of Filter menu options
        filterSub.Enable(1110, False)
        filterSub.Enable(1112, True)

        # Turn on buttons in filter section of the Image tab.
        self.takeImage.filterInstance.filterButton.Enable(True)
        self.takeImage.filterInstance.homeButton.Enable(True)

    def onFilterDisconnect(self, event):
        """
        Run when filter disconnect option is selected.  Closes connection and locks down filter options.
        """
        logger.info("Disconnect pressed in filter menu")
        connection = port_dict['5503']
        connection.disconnect()
        
        # lock the connect button up and unlock the disconnect
        filterSub = self.menuBar.GetMenu(2)
        filterSub.Enable(1110, True)
        filterSub.Enable(1112, False)
        self.takeImage.filterInstance.filterButton.Enable(False)
        self.takeImage.filterInstance.homeButton.Enable(False)

    def logMain(self, logmsg):
        """
        Note: This is used to log activity within the most top level class.
        Pre: Pass in string that will be logged to only the log tab.
        """
        logger.info("logging from exposure class")
        logInstance = self.log.logInstance
        wx.CallAfter(logInstance.threadSafeLogStatus, logmsg)

    def logMethod(self, logfunc, logmsg):
        """
        Pre: Before an exposure is set the correct log function to call is set to self.logFunction.
        For example, setting self.logFunction to self.logScript will log on the scripting status
        and the log tab versus self.logExposure.  Also passed in is the logmsg that you want to 
        print.
        Post: This method will run the logfunc to print the log message to the correct status
        boxes; it returns nothing.
        """
        logger.info("entered logMethod")
        logfunc(logmsg)

    def joinThreads(self, threadKey, demonized=False):
        t = self.active_threads.pop(threadKey)
        if demonized:
            t.join(0)
        else:
            t.join(0)
        logger.debug("Thread with key "+ str(threadKey) + " is shutdown")

        
class ImageWindow(wx.Frame):

    """
    Controls the image display window.
    """
    def __init__(self, parent):
        """
        Initializes window elements.
        """
        wx.Frame.__init__(self, parent, -1, "Image Window", size=(650,550))

        #self.image = 'example.fit'  # for debugging
        self.parent = parent
        self.currSliderValue = 60
        self.currMap = 'gray'
        logger.debug("current slider value " + str(self.currSliderValue))

        ## Main sizers
        self.topSizer = wx.BoxSizer(wx.VERTICAL)
        self.sideSizer = wx.BoxSizer(wx.HORIZONTAL)

        ## Minor Sizers
        self.sliderSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.panel = DrawImage(self)
        self.parent.imageOpen = True

        #self.data = self.panel.getData(self.image)  # for debugging

        ### Put in matplotlib imshow window
        #self.panel.plotImage(self.data, 6.0, 'gray')  # for debugging
        self.devSlider = wx.Slider(self, id=-1, value=60, minValue=1, maxValue=200, size=(250,-1),\
                         style=wx.SL_HORIZONTAL)
        self.invert = wx.CheckBox(self, id=-1, label="Invert")
        self.invert.SetValue(False)
        self.text = wx.StaticText(self, label='Contrast:')

        self.stats = self.CreateStatusBar(4)
        self.stats.SetStatusStyles([1,1,1,1])
        self.stats.SetStatusText("Min: %.0f"%(self.panel.min), 0)
        self.stats.SetStatusText("Max: %.0f"%(self.panel.max), 1)
        self.stats.SetStatusText("Mean: %.1f"%(self.panel.mean), 2)
        self.stats.SetStatusText("Median: %.0f"%(self.panel.median), 3)

        self.menuBar = wx.MenuBar()

        self.fileMenu = wx.Menu()
        self.fileMenu.Append(1500, "&Open", "Open fits image")

        self.menuBar.Append(self.fileMenu, "&File")
        self.SetMenuBar(self.menuBar)

        ##  Adjust sub sizers
        self.sliderSizer.Add(self.text, flag=wx.ALIGN_CENTER)
        als.AddLinearSpacer(self.sliderSizer, 10)
        self.sliderSizer.Add(self.devSlider, flag=wx.ALIGN_CENTER)
        als.AddLinearSpacer(self.sliderSizer, 20)
        self.sliderSizer.Add(self.invert, flag=wx.ALIGN_CENTER)

        ## Adjust major sizers
        self.topSizer.Add(self.panel, proportion=1, flag=wx.EXPAND)
        self.topSizer.Add(self.sliderSizer, flag=wx.ALIGN_CENTER)

        ### Binds
        self.devSlider.Bind(wx.EVT_SCROLL, self.onSlide)
        self.invert.Bind(wx.EVT_CHECKBOX, self.onInvert)
        self.Bind(wx.EVT_MENU, self.onOpen, id=1500)
        self.Bind(wx.EVT_CLOSE, self.onClose)

        # Set Icon
        ico = wx.Icon("evora_logo_circ.ico", wx.BITMAP_TYPE_ICO)
        self.SetIcon(ico)

        self.SetSizer(self.topSizer)
        self.Fit()

    def onSlide(self, event):
        """
        When the user uses the contrast slider this will adjust the limits of the image based on the median average deviation.
        """
        self.currSliderValue = event.GetPosition()
        value = float(event.GetPosition()) / 10.0
        lower = self.panel.median - value * self.panel.mad
        upper = self.panel.median + value * self.panel.mad
        self.panel.updateLims(lower, upper)
        self.panel.refresh()

    def onClose(self, event):
        """
        Runs when user closes the image window.  Closes window safely.
        """
        logger.info("entered close")
        self.parent.imageOpen = False
        self.panel.closeFig()
        self.Destroy()

    def onOpen(self, event):
        """
        Opens when user selects to load an image.  Allows user to select a load a saved fits/fit image.
        """
        logger.info("Trying to open image")
        openFileDialog = wx.FileDialog(self, "Open Image File", "", "", "Image (*.fits;*.fit)|*.fits.*;*.fits;*.fit", wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        
        if openFileDialog.ShowModal() == wx.ID_CANCEL:
            return
        
        fileName = openFileDialog.GetFilename()
        fileName = fileName.split(".")
        
        if fileName[-1] in ["fits", "fit"]:
            data = als.getData(openFileDialog.GetPath())
            stats_list = als.calcStats(data)
            self.parent.takeImage.exposureInstance.safePlot(data, stats_list)

    def onInvert(self, event):
        """
        Called when invert check box is clicked.  Inverts the gray scale on the displayed fits image.
        """
        value = event.IsChecked()
        if value is True:
            logger.info("Inverting image gray scale")
            self.panel.updateCmap("gray_r")
            self.panel.refresh()
            self.currMap = 'gray_r'
        if value is False:
            logger.info("Changing image to regular gray scale")
            self.panel.updateCmap('gray')
            self.panel.refresh()
            self.currMap = 'gray'

    def resetWidgets(self):
        """
        DEPRECATED: When plotting new image, uses the current position to set the scale.
        Used to reset the slider to the default state.
        """
        # Set slider to 60
        self.devSlider.SetValue(60)
        self.invert.SetValue(False)


class DrawImage(wx.Panel):
    """
    Used to draw a plot onto the Matplotlib figure that is embedded in a wxPython frame.
    """
    def __init__(self, parent):
        """
        Initializes embedded matplotlib figure.
        """
        wx.Panel.__init__(self, parent)

        self.parent = parent

        # Create figure, plot space, and canvas for drawing fit image
        self.figure, self.axes = plt.subplots(1)
        self.figure.frameon = False
        self.axes.get_yaxis().set_visible(False)
        self.axes.get_xaxis().set_visible(False)
        self.axes.invert_xaxis()
        self.canvas = FigureCanvas(self, -1, self.figure)
        
        # If one wants to add the toolbar uncomment
        #self.toolbar = Toolbar(self.canvas)
        #self.toolbar.Realize()

        self.min = 0
        self.max = 0
        self.mean = 0
        self.median = 0
        self.mad = 0
        
        # set sizers
        self.vertSizer = wx.BoxSizer(wx.VERTICAL)
        #self.horzSizer = wx.BoxSizer(wx.HORIZONTAL)

        # add to sizers
        self.vertSizer.Add(self.canvas, proportion=1, flag=wx.LEFT | wx.TOP | wx.GROW)
        #self.vertSizer.Add(self.toolbar, proportion=0, flag= wx.EXPAND)

        self.SetSizer(self.vertSizer)
        self.Fit()

    def plotImage(self, data, scale, cmap):
        """
        Should call updatePassedStats first before calling this. Creates new plot to be drawn.
        """
        self.mad = np.median(np.abs(data.ravel()-self.median))  # median absolute deviation
        deviation = scale * self.mad
        self.upper = self.median + deviation
        self.lower = self.median - deviation

        data = np.fliplr(data)
        self.plot = self.axes.imshow(data, vmin=self.lower, vmax=self.upper, origin='lower')
        #self.axes.invert_xaxis()
        
        self.plot.set_clim(vmin=self.lower, vmax=self.upper)
        self.plot.set_cmap(cmap)
        self.figure.tight_layout()
    
    def refresh(self):
        """
        Draws image onto figure.  Call after using plotImage.
        """
        self.canvas.draw()
        self.canvas.Refresh()
    
    def clear(self):
        """
        Clear the current figure to be redrawn.
        """
        self.axes.clear()

    # Replaced with similar method in AddLinearSpacer
    def getData(self, image):
        """
        Get fits data.
        """
        return fits.getdata(image)

    def updateScreenStats(self):
        """
        Updates the stats on the status bar.
        """
        self.parent.stats.SetStatusText("Min: %.0f"%(self.min), 0)
        self.parent.stats.SetStatusText("Max: %.0f"%(self.max), 1)
        self.parent.stats.SetStatusText("Mean: %.1f"%(self.mean), 2)
        #self.parent.stats.SetStatusText("Mode: %.0f"%(self.mode), 3)
        self.parent.stats.SetStatusText("Median: %.0f"%(self.median), 3)


    def updatePassedStats(self, stats_list):  # list needs to be [min, max, mean, median]
        """
        Updates the global stats from passed in stat list.
        """
        self.min = stats_list[0]
        self.max = stats_list[1]
        self.mean = stats_list[2]
        self.median = stats_list[3]

    def updateStats(self, data):
        """
        # Deprecated for a similar method in AddLinearSpacer.py
        """
        self.min = np.min(data.flat)
        self.max = np.max(data.flat)
        self.mean = np.mean(data.flat)
        self.median = np.median(data.flat)

    def updateLims(self, min, max):
        """
        Update the figure contrast
        """
        self.plot.set_clim(vmin=min, vmax=max)

    def updateCmap(self, cmap):
        """
        Update the color map of the figure to the passed in one.
        """
        self.plot.set_cmap(cmap)

    def closeFig(self):
        """
        Close figure when called.  Usually used when closing entire GUI.
        """
        plt.close('all')

        
class TakeImage(wx.Panel): ## first tab; with photo imaging
    """
    Embeds all the imaging functionality widgets into the imaging tab.
    """
    def __init__(self, parent):
        """
        Initialize imaging tab.
        """
        wx.Panel.__init__(self, parent)

        # Things to add: add updating text for temperature in bottom left of GUI
        self.parent = parent

        # Set sizers so I have horizontal and vertical control
        self.topbox = wx.BoxSizer(wx.VERTICAL)
        #self.hbox = wx.BoxSizer(wx.HORIZONTAL)

        ### Sub sizer
        self.expTempSizer = wx.BoxSizer(wx.VERTICAL)
        self.controlHorz = wx.BoxSizer(wx.HORIZONTAL)

        self.filterInstance = ac.FilterControl(self)
        self.tempInstance = ac.TempControl(self)
        self.exposureInstance = ac.Exposure(self)
        self.typeInstance = ac.TypeSelection(self)

        ## place sub sizers
        self.expTempSizer.Add(self.exposureInstance, flag=wx.ALIGN_CENTER)
        als.AddLinearSpacer(self.expTempSizer, 8)
        self.expTempSizer.Add(self.tempInstance, flag=wx.ALIGN_CENTER)

        self.controlHorz.Add(self.expTempSizer, flag=wx.ALIGN_CENTER)
        als.AddLinearSpacer(self.controlHorz, 50)
        self.controlHorz.Add(self.filterInstance, flag=wx.ALIGN_CENTER)

        ### place main Sizer
        als.AddLinearSpacer(self.topbox, 20)
        self.topbox.Add(self.typeInstance, flag=wx.ALIGN_CENTER)
        als.AddLinearSpacer(self.topbox, 20)
        self.topbox.Add(self.controlHorz, flag=wx.ALIGN_CENTER)

        # comes last
        self.SetSizer(self.topbox)
        self.topbox.Fit(self)


class Log(wx.Panel): # Code for each widget is in logClasses.py
    """
    Handles the logging tab elements.
    """
    def __init__(self, parent):
        """
        Place widgets in logging tab.
        """
        wx.Panel.__init__(self, parent)

        ## Main Sizers
        self.vertSizer = wx.BoxSizer(wx.VERTICAL)
        self.horzSizer = wx.BoxSizer(wx.HORIZONTAL)

        # sub sizers
        self.logInstance = lc.logBox(self)

        # adjust sub sizers

        # adjust main sizers
        als.AddLinearSpacer(self.vertSizer, 20)
        self.vertSizer.Add(self.logInstance, proportion=1, flag=wx.ALIGN_CENTER|wx.EXPAND)

        self.SetSizer(self.vertSizer)
        self.vertSizer.Fit(self)

class Scripting(wx.Panel): # Code for widgets is in scriptingClasses.py
    """
    Handles the Logging tab.
    """
    def __init__(self,parent):
        """
        Places widgets.
        """
        wx.Panel.__init__(self, parent)

        self.parent = parent

        ## Main Sizers
        self.vertSizer = wx.BoxSizer(wx.VERTICAL)
        self.horzSizer = wx.BoxSizer(wx.HORIZONTAL)

        ## Subsizers (none)

        # adjust subsizers
        self.scriptStatus = sc.ScriptStatus(self)
        self.scriptCommands = sc.ScriptCommands(self)

        # adjust main sizers
        als.AddLinearSpacer(self.horzSizer, 15)
        self.horzSizer.Add(self.scriptStatus, flag=wx.ALIGN_CENTER)

        als.AddLinearSpacer(self.vertSizer, 15)
        self.vertSizer.Add(self.scriptCommands, flag=wx.ALIGN_CENTER)
        als.AddLinearSpacer(self.vertSizer, 15)
        self.vertSizer.Add(self.horzSizer, flag=wx.ALIGN_CENTER)

        self.SetSizer(self.vertSizer)
        self.vertSizer.Fit(self)

### Classes for twisted
class EvoraForwarder(basic.LineReceiver):
    """
    Sends and receives data from Evora server.
    """
    def __init__(self):
        self.output = None
        self._deferreds = {}

    def dataReceived(self, data):
        """
        Handles incoming data and starts the proper call back chain based on the key received from the server.
        """
        logger.debug("Receieved from E. server: " + data)
        
        # Get GUI instance
        gui = self.factory.gui
            
        # Initialize ports.
        gui.protocol = self
        gui.takeImage.exposureInstance.protocol = self
        gui.takeImage.tempInstance.protocol = self
        gui.takeImage.filterInstance.protocol = self
        gui.scripting.scriptCommands.protocol = self

        # With a multi-threaded server one is not guarenteed to receive one line at a time.
        # This code take into account receiving multiple lines.
        sep_data = data.rsplit() # split for multiple lines
        size = len(sep_data) # size of sep_data will always be even (key followed by data pair)
        for i in range(0, size, 2):
            singular_sep_data = [sep_data[i], sep_data[i+1]]

            if singular_sep_data[0] in self._deferreds:
                self._deferreds.pop(singular_sep_data[0]).callback(singular_sep_data[1])
        
    def sendCommand(self, data):
        """
        Wrapper method for sending lines to the Evora server.
        """
        logger.debug("Sent to E. server: " + data)
        self.sendLine(data)
        d = self._deferreds[data.split(" ")[0]] = defer.Deferred()
        return d

    def connectionMade(self):
        """
        Executes when twisted connects to server.
        """
        
        self.output = self.factory.gui.log.logInstance.logBox
        logger.info("Connection made to E. server on port 5502")
        
        ## Add a callback that will open up the rest of the gui when the camera is done setting up
        gui = self.factory.gui # get gui for adding the callback method
        d = defer.Deferred()
        d.addCallback(gui.onConnectCallback)
        self._deferreds["status"] = d

    def addDeferred(self, string):
        """
        This is used for creating deferred objects when expecting to receive data.
        """
        d = self._deferreds[string] = defer.Deferred()
        return d

    def removeDeferred(self, string):
        """
        Used to get rid of any trailing deferred obejcts (e.g. realSent after an abort)
        """
        if(string in self._deferreds):
            self._deferreds.pop(string)

    def connectionLost(self, reason):
        """
        Executes when connection is lost to Evora server.
        """
        ## Add a "callback" that will close down the gui functionality when camera connection is closed.
        #gui = self.factory.gui
        #gui.onDisconnectCallback()
        pass



class EvoraClient(protocol.ClientFactory):
    """
    Makes a client instance for the the user running the GUI.
    """
    def __init__(self, gui):
        self.gui = gui
        self.protocol = EvoraForwarder
        self.filterWatchThread = None

    def clientConnectionLost(self, transport, reason):
        """
        Called when client connection is lost normally.
        """
        exposureInstance = self.gui.takeImage.exposureInstance
        exposureInstance.logFunction = exposureInstance.logExposure
        logString = als.getLogString("connectLost 1", 'post')
        exposureInstance.log(exposureInstance.logFunction, logString)

        logger.info("connection to E. server lost normally on port 5502")

    def clientConnectionFailed(self, transport, reason):
        """
        Called when client connection is lost unexpectedly.
        """
        exposureInstance = self.gui.takeImage.exposureInstance
        exposureInstance.logFunction = exposureInstance.logExposure
        logString = als.getLogString("connectFailed 1", 'post')
        exposureInstance.log(exposureInstance.logFunction, logString)

        logger.warning("connection to E. server failed on port 5502")

class FilterForwarder(basic.LineReceiver):
    """
    Handles outgoing/incoming data with filter server.
    """
    def __init__(self):
        self.output = None
        self._deferreds = {}
        self.gui = None

    def dataReceived(self, data):
        """
        Handles incoming data and executes the appropriate twisted callback method.
        """
        logger.debug("Receieved from filter (5503): " + data)        
            
        self.gui.takeImage.filterInstance.protocol2 = self
        
        # if there is more than one line that was received 
        sep_data = data.rsplit()  # split for multiple lines
        size = len(sep_data) # size of sep_data will always be even (key followed by data pair)
        for i in range(0, size, 2):
            singular_sep_data = [sep_data[i], sep_data[i+1]]

            # run singular_sep_data command one at a time
            if singular_sep_data[0] in self._deferreds:
                self._deferreds.pop(singular_sep_data[0]).callback(singular_sep_data[1])
        
    def sendCommand(self, data):
        logger.debug("Sending to filter: " +  str(data))
        self.sendLine(data)
        d = None
        if(data.split(" ")[0] == "move"):
            d = self._deferreds["moved"] = defer.Deferred()
        else:
            d = self._deferreds[data.split(" ")[0]] = defer.Deferred()
        return d

    def connectionMade(self):
        """
        Executes when conncetion is made to filter.
        """
        ## Add a callback that will open up the rest of the gui when the camera is done setting up
        #gui = self.factory.gui # get gui for adding the callback method
        #d = defer.Deferred()
        #d.addCallback(gui.onConnectCallback)
        #self._deferreds["status"] = d
        
        self.gui = self.factory.gui
        self.gui.takeImage.filterInstance.protocol2 = self
        self.gui.takeImage.filterInstance.statusBar = self.gui.stats

        logger.info("connection made to filter")

        filterInstance = self.gui.takeImage.filterInstance

        filterInstance.filterConnection = True
        #self.filterWatchThread = threading.Thread(target=filterInstance.filterWatch, args=())
        #self.filterWatchThread.daemon = True

        filterInstance.logFunction = filterInstance.logFilter
        logString = als.getLogString('filter connect', 'pre')
        filterInstance.log(filterInstance.logFunction, logString)

        logString = als.getLogString('filter getFilter', 'pre')
        filterInstance.log(filterInstance.logFunction, logString)

        d = self.sendCommand('getFilter')
        d.addCallback(filterInstance.getFilterCallback)

        
    def addDeferred(self, string):
        """
        This is used for creating deferred objects when expecting to receive data.
        """
        d = self._deferreds[string] = defer.Deferred()
        return d

    def removeDeferred(self, string):
        """
        Used to get rid of any trailing deferred obejcts (e.g. realSent after an abort)
        """
        if(string in self._deferreds):
            self._deferreds.pop(string)

    def connectionLost(self, reason):
        """
        Called when connection is lost to the filter server.
        """
        ## Add a "callback" that will close down the gui functionality when camera connection is closed.
        filterInstance = self.gui.takeImage.filterInstance
        filterInstance.filterConnection = False
        self.gui.stats.SetStatusText("Filter: offline", 3)


class TransferForwarder(basic.LineReceiver):
    """
    Handles outgoing/incoming data with filter server.
    """
    def __init__(self):
        self.output = None
        self._deferreds = {}
        self.gui = None

    def dataReceived(self, data):
        """
        Handles incoming data and executes the appropriate twisted callback method.
        """
        logger.debug("Receieved from transfer server (5505): " + data)        
            
        
        # if there is more than one line that was received 
        sep_data = data.rsplit()  # split for multiple lines
        size = len(sep_data) # size of sep_data will always be even (key followed by data pair)
        for i in range(0, size, 2):
            singular_sep_data = [sep_data[i], sep_data[i+1]]

            # run singular_sep_data command one at a time
            if singular_sep_data[0] in self._deferreds:
                self._deferreds.pop(singular_sep_data[0]).callback(singular_sep_data[1])
        
    def sendCommand(self, data):
        logger.debug("Sending to transfer image: " +  str(data))
        self.sendLine(str(data))
        d = self._deferreds[data.split(" ")[0]] = defer.Deferred()
        return d

    def connectionMade(self):
        """
        Executes when conncetion is made to filter.
        """
        self.gui = self.factory.gui
        self.gui.takeImage.exposureInstance.ftpLayer = self
        logger.info("Connection made to transfer images.")

    def addDeferred(self, string):
        """
        This is used for creating deferred objects when expecting to receive data.
        """
        d = self._deferreds[string] = defer.Deferred()
        return d

    def removeDeferred(self, string):
        """
        Used to get rid of any trailing deferred obejcts (e.g. realSent after an abort)
        """
        if(string in self._deferreds):
            self._deferreds.pop(string)

    def connectionLost(self, reason):
        """
        Called when connection is lost to the filter server.
        """
        ## Add a "callback" that will close down the gui functionality when camera connection is closed.
        print("Lost connectiont to transfer server.")
        
class FilterClient(protocol.ClientFactory):
    """
    Makes a filter wheel client instance.
    """
    def __init__(self, gui):
        self.gui = gui
        self.protocol = FilterForwarder

    def clientConnectionLost(self, transport, reason):
        """
        Executes when client has lost connection normally.
        """
        filterInstance = self.gui.takeImage.filterInstance
        filterInstance.logFunction = filterInstance.logFilter
        logString = als.getLogString("filter connectLost 1", 'post')
        filterInstance.log(filterInstance.logFunction, logString)

        logger.info("connection lost normally on port 5503")
        
    def clientConnectionFailed(self, transport, reason):
        """
        Executes when client has lost connection unexpectedly.
        """
        filterInstance = self.gui.takeImage.filterInstance
        filterInstance.logFunction = filterInstance.logFilter
        logString = als.getLogString("filter connectFailed 1", 'post')
        filterInstance.log(filterInstance.logFunction, logString)

        logger.warning("connection failed on port 5503")

class TransferClient(protocol.ClientFactory):
    """
    Makes a filter wheel client instance.
    """
    def __init__(self, gui):
        self.gui = gui
        self.protocol = TransferForwarder

    def clientConnectionLost(self, transport, reason):
        """
        Executes when client has lost connection normally.
        """
        filterInstance = self.gui.takeImage.filterInstance
        filterInstance.logFunction = filterInstance.logFilter
        logString = als.getLogString("filter connectLost 1", 'post')
        filterInstance.log(filterInstance.logFunction, logString)

        logger.info("connection lost normally on port 5503")
        
    def clientConnectionFailed(self, transport, reason):
        """
        Executes when client has lost connection unexpectedly.
        """
        filterInstance = self.gui.takeImage.filterInstance
        filterInstance.logFunction = filterInstance.logFilter
        logString = als.getLogString("filter connectFailed 1", 'post')
        filterInstance.log(filterInstance.logFunction, logString)

        logger.warning("connection failed on port 5503")

        
class FileClient(FTPClient, object):

    def __init__(self, factory, username, password, passive):
        super(FileClient, self).__init__(username=username, password=password, passive=passive)
        # Set to not be passive ftp protocol, ie 1.
        self.factory = factory

    def connectionMade(self):
        # Pass the protocol to the gui when connection is made to FTP Sever
        gui = self.factory.gui
        # Main wx.Frame
        gui.ftp = self
        gui.takeImage.exposureInstance.ftp = self
        
class FileClientFactory(protocol.ClientFactory):
    def __init__(self, gui):
        self.gui = gui
        self.protocol = None

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
    ## Deprecated
    #log.startLogging(sys.stdout)
    #sys.stdout = als.Logger(sys.stdout)
    #sys.stderr = als.Logger(sys.stderr)
    
    app = wx.App(False)
    app.frame1 = Evora()
    app.frame1.Show()
    #app.frame2 = ImageWindow()
    #app.frame2.Show()
    reactor.registerWxApp(app)
    #reactor.connectTCP("localhost", 5502, EvoraClient(app.frame1))
    reactor.run()
    app.MainLoop()    
