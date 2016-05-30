#!/usr/bin/python2

from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import wx
import matplotlib
matplotlib.use("WXAgg")
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2Wx as Toolbar
import matplotlib.pyplot as plt
from astropy.io import fits
import numpy as np
from scipy import stats
import EnhancedStatusBar
import sys
import threading
import Queue
import thread

# twisted imports
from twisted.python import log
from twisted.internet import protocol
from twisted.internet import wxreactor
wxreactor.install()

# always goes after wxreactor install
from twisted.internet import reactor
from twisted.internet import defer
from twisted.internet import threads
from twisted.protocols import basic

import acquisitionClasses as ac
import controlClasses as cc
import scriptingClasses as sc
import logClasses as lc
import AddLinearSpacer as als


## Global Variables
app = None

## Getting to parents (i.e. different classes)
# Three parents will get to the Evora class and out of the notebook


# Frame class.
class Evora(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, None, -1, "Evora Acquisition GUI", size=(600, 450))

        self.protocol = None # client protocol
        self.connection = None
        self.connected = False
        self.active_threads = {}  # list of the active threads
        self.imageOpen = False # keep track of whether the image window is open
        self.window = None # holds the image window
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
        self.takeImage = notebook.GetPage(0)
        #self.otherParams = notebook.GetPage(1)
        self.scripting = notebook.GetPage(1)
        self.log = notebook.GetPage(2)

        # Widgets

        #
        self.binning = "2" # starts in 2x2 binning

        ## Menu
        self.menuBar = wx.MenuBar()

        ## Sub menus
        filterSub = wx.Menu()
        filterSub.Append(1110, "&Connect", "Connect to the filter")
        filterSub.Append(1111, "&Refresh", "Refresh filter list")

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

        # create main menus
        fileMenu = wx.Menu()
        fileMenu.AppendMenu(1001, "&Filter", filterSub)
        fileMenu.AppendMenu(1002, "&Binning", binningSub)
        #fileMenu.AppendMenu(1003, "&Camera", cameraSub)
        fileMenu.Append(1000, "&Exit", "Quit from Evora")

        viewMenu = wx.Menu()
        viewMenu.Append(1200, "&Image", "Open Image Window")

        helpMenu = wx.Menu()
        helpMenu.Append(1300, "&Help")

        # add to menu bar
        self.menuBar.Append(fileMenu, "&File")
        self.menuBar.Append(cameraSub, "&Camera")
        self.menuBar.Append(viewMenu, "&View")
        self.menuBar.Append(helpMenu, "&Help")
        # instantiate menubar
        self.SetMenuBar(self.menuBar)

        ## Status Bar:  include temperature, binning type, gauge for exposure
        self.stats = EnhancedStatusBar.EnhancedStatusBar(self)
        self.stats.SetSize((23,-1))
        self.stats.SetFieldsCount(3)
        self.SetStatusBar(self.stats)
        self.stats.SetStatusText("Current Temp:            ... C", 0)
        self.stats.SetStatusText("Binning Type: 2x2", 2)
        self.stats.SetStatusText("Exp. Status:", 1)
        self.expGauge = wx.Gauge(self.stats, id=1, range=100, size=(110, -1))
        self.stats.AddWidget(self.expGauge, pos=1, horizontalalignment=EnhancedStatusBar.ESB_ALIGN_RIGHT)
        
        #self.bitmap = wx.StaticBitmap(self.stats, -1, wx.Bitmap("greenCirc.png"),size=(90, 17))
        #self.bitmap.SetBitmap(wx.Bitmap('greenCirc.png'))
        #tempText = wx.StaticText(self.stats, -1, label="50 C")
        #self.stats.AddWidget(self.bitmap, pos=0, horizontalalignment=EnhancedStatusBar.ESB_ALIGN_RIGHT)
        #self.stats.AddWidget(tempText, pos=0, horizontalalignment=EnhancedStatusBar.ESB_ALIGN)



        #self.takeImage.tempInstance.changeTemp(50, self.stats)

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
        self.Bind(wx.EVT_MENU, self.onConnect, id=1130)
        self.Bind(wx.EVT_MENU, self.onDisconnect, id=1131)
        self.Bind(wx.EVT_MENU, self.onShutdown, id=1132)
        self.Bind(wx.EVT_MENU, self.onFilterConnect, id=1110)
        self.Bind(wx.EVT_MENU, self.onFilterListRefresh, id=1111)
        #self.Bind(wx.EVT_MENU, self.onStartup, id=1133)
        #self.Bind(wx.EVT_CLOSE, self.onClose)

        #wx.EVT_CLOSE(self, lambda evt: reactor.stop())

        self.disableButtons(True)

        # Add and set icon
        #logo = wx.StaticBitmap(None, -1, wx.Bitmap("evora_logo"))
        ico = wx.Icon("evora_logo_circ.ico", wx.BITMAP_TYPE_ICO)
        self.SetIcon(ico)

        panel.SetSizer(sizer)
        panel.Layout()
  
    ## Memory upon destruction seems to not release.  This could cause memory usage to increase
    ## with newly loaded images when using the evora camera.
    def openImage(self, event):
        self.window = ImageWindow(self)
        self.window.Show()
        self.imageOpen = True

    def onClose(self, event):
        dialog = wx.MessageDialog(None, "Close Evora GUI?", "Closing Evora", wx.OK | wx.CANCEL|wx.ICON_QUESTION)
        answer = dialog.ShowModal()
        dialog.Destroy()
        #print (answer)
        if answer == wx.ID_OK:
            self.quit()
            #if(self.protocol is not None):
            #    d = self.protocol.sendCommand("shutdown")
            #    d.addCallback(self.quit)

            #self.Destroy()
            #reactor.stop()
    
    def quit(self):
        #print (msg)
        if self.connected:
            self.connection.disconnect()
        self.Destroy()
        reactor.stop()

    def onHelp(self, event):
        """
        Open up, ideally, markdown window (or potentially html markup) that gives indepth
        documentations on what is what.
        """
        print("Help")
        
    def onRefresh(self, event):
        self.takeImage.filterInstance.refreshList()
        print ("hello")

    def on1x1(self, event):
        self.binning = "1"
        self.stats.SetStatusText("Binning Type: 1x1", 2)

    def on2x2(self, event):
        self.binning = "2"
        self.stats.SetStatusText("Binning Type: 2x2", 2)

    def onConnect(self, event):
        print ("Connecting")
        #reactor.run()
        self.connection = reactor.connectTCP("localhost", 5502, EvoraClient(app.frame1))

    def onConnectCallback(self, msg):
        #msg = args[0]
        #thread = args[1]

        print (msg, "Startup callback entered")
        self.connected = True

        # get the number of clients
        status = int(msg.split(",")[0])

        if(status == 20075):  # camera is uninitialized
            d = self.protocol.sendCommand("connect")
            d.addCallback(self.callStartup)
        else:  # if camera is already initialized then start server like regular
            # start temperature thread
            t = threading.Thread(target=self.takeImage.tempInstance.watchTemp, args=(), name="temp thread")
            self.takeImage.tempInstance.isConnected = True # setups infinite loop in watchTemp method
            t.daemon = True
            t.start()
            self.active_threads["temp"] = t
            
            # Enable disconnect and shutdown and disable connect menu items
            self.enableConnections(False, True, True)
            self.disableButtons(False)

        #settings.done_ids.put(threading.current_thread().name)
        #signal.alarm(1) # signal thread is done here
        #print "done"
            

    def callStartup(self, msg):
        result = int(msg)

        self.connected = True # boolean to tell if connected to server
        self.enableConnections(False, True, True) # grey and un-grey camera menu options
        self.disableButtons(False) # enable gui functionality
        self.takeImage.tempInstance.isConnected = True # setups infinite loop in watchTemp method
        t = threading.Thread(target=self.takeImage.tempInstance.watchTemp, args=(), name="temp thread")
        t.daemon = True
        t.start()
        self.active_threads["temp"] = t

        print("Started up")

        #settings.done_ids.put(threading.current_thread().name)
        #signal.alarm(1)

    

    
    def onDisconnect(self, event):
        print("Disconnecting")
        self.takeImage.tempInstance.isConnected = False # closes infinite loop in watchTemp method
        
        bitmap = wx.StaticBitmap(self.stats, -1, size=(90, 17))
        self.stats.AddWidget(bitmap, pos=0, horizontalalignment=EnhancedStatusBar.ESB_ALIGN_RIGHT)
        self.stats.SetStatusText("Current Temp:            ... C", 0)
        
        #t = threading.Thread(target=self.joinThreads, args=("temp",))
        #t.start()
        self.joinThreads("temp", demonized=True)
        self.connection.disconnect() # this is the acutal disconnection from the server'

        self.connected = False
        self.enableConnections(True, False, False)
        self.disableButtons(True)

        #reactor.stop()
        
    def onDisconnectCallback(self):
        self.connected = False
        self.enableConnections(True, False, False) # edit the connections menu in the file menu
        self.disableButtons(True)
        
    """
    def onStartup(self, event):
        #self.connection = reactor.connectTCP("localhost", 5502, EvoraClient(app.frame1))
        d = self.protocol.sendCommand("connect")
        d.addCallback(self.callStartup)
    """

    def onShutdown(self, event):
        if(self.protocol is not None):
            d = self.protocol.sendCommand("shutdown")
            d.addCallback(self.callShutdown)
            self.disableButtons(True)

    def callShutdown(self, msg):
        self.takeImage.tempInstance.isConnected = False

        bitmap = wx.StaticBitmap(self.stats, -1, size=(90, 17))
        self.stats.AddWidget(bitmap, pos=0, horizontalalignment=EnhancedStatusBar.ESB_ALIGN_RIGHT)
        self.stats.SetStatusText("Current Temp:            ... C", 0)

        self.joinThreads("temp", demonized=False)
        self.connection.disconnect()
        self.connected = False
        self.enableConnections(True, False, False)

    def enableConnections(self, con, discon, shut):
        # get file menu
        cameraSub = self.menuBar.GetMenu(1)  # first index
        # get camera sub menu
        #cameraSub = [fileMenu.FindItemById(1130), fileMenu.FindItemById(1131)]

        cameraSub.Enable(1130, con)
        cameraSub.Enable(1131, discon)
        cameraSub.Enable(1132, shut)

    def disableButtons(self, boolean):
        # Diable GUI functionality (expose, stop, cool, warmup, rotate to)
        boolean = not boolean
        self.takeImage.exposureInstance.expButton.Enable(boolean)
        #self.takeImage.exposureInstance.stopExp.Enable(boolean)
        
        self.takeImage.tempInstance.tempButton.Enable(boolean)
        self.takeImage.tempInstance.stopCool.Enable(boolean)

        self.takeImage.filterInstance.filterButton.Enable(boolean)

    def onFilterConnect(self, event):
        """
        When 'Connect' is pressed in the filter sub-menu of file this will run the initialization process for the filter.
        The server will will start the filter motor and then use the connect function
        """
        # send command on filter setup
        
        # lock the connect button up and unlock the disconnect        
        pass

    def onFilterListRefresh(self, event):
        """
        This will simply refresh the filter list so that the menu gets displayed correctly.  This is only used when
        a filter the file "filter.txt" has been edited.
        """
        pass

    def joinThreads(self, threadKey, demonized=False):
        t = self.active_threads.pop(threadKey)
        if demonized:
            t.join(0)
        else:
            t.join(0)
        print("Thread with key", threadKey, "is shutdown")


class ImageWindow(wx.Frame):

    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, "Image Window", size=(650,550))

        self.image = 'example.fit'
        self.parent = parent

        ## Main sizers
        self.topSizer = wx.BoxSizer(wx.VERTICAL)
        self.sideSizer = wx.BoxSizer(wx.HORIZONTAL)

        ## Minor Sizers
        self.sliderSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.panel = DrawImage(self)
        self.parent.imageOpen = True

        #self.data = self.panel.getData(self.image)

        ### Put in matplotlib imshow window
        #self.panel.plotImage(self.data, 6.0, 'gray')
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
        #self.stats.SetStatusText("Mode: %.0f"%(self.panel.mode), 3)
        self.stats.SetStatusText("Median: %.0f"%(self.panel.median), 3)


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
        self.Bind(wx.EVT_CLOSE, self.onClose)

        # Set Icon
        ico = wx.Icon("evora_logo_circ.ico", wx.BITMAP_TYPE_ICO)
        self.SetIcon(ico)

        self.SetSizer(self.topSizer)
        self.Fit()


    def onSlide(self, event):
        value = float(event.GetPosition()) / 10.0
        lower = self.panel.median - value * self.panel.mad
        upper = self.panel.median + value * self.panel.mad
        self.panel.updateLims(lower, upper)
        self.panel.refresh()

    def onClose(self, event):
        print("entered close")
        self.parent.imageOpen = False
        self.panel.closeFig()
        self.Destroy()
        #self.Close()

    def onInvert(self, event):
        value = event.IsChecked()
        if value is True:
            self.panel.updateCmap("gray_r")
            self.panel.refresh()
        if value is False:
            self.panel.updateCmap('gray')
            self.panel.refresh()


    def resetWidgets(self):
        # Set slid to 60
        self.devSlider.SetValue(60)
        self.invert.SetValue(False)


class DrawImage(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.parent = parent

        # Create figure, plot space, and canvas for drawing fit image
        self.figure, self.axes = plt.subplots(1)
        self.figure.frameon = False
        self.axes.get_yaxis().set_visible(False)
        self.axes.get_xaxis().set_visible(False)
        self.canvas = FigureCanvas(self, -1, self.figure)
        #self.toolbar = Toolbar(self.canvas)
        #self.toolbar.Realize()

        self.min = 0
        self.max = 0
        self.mean = 0
        self.median = 0
        #self.mode = 0
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
        Should call updatePassedStats first before calling this.
        """
        # get data

        """
        self.min = np.min(data.flat)
        self.max = np.max(data.flat)
        self.mean = np.mean(data.flat)
        self.median = np.median(data.flat)
        self.mode = stats.mode(data.flat)[0][0]
        """
        #print "Reached"

        self.mad = np.median(np.abs(data.flat-self.median)) # median absolute deviation
        deviation = scale * self.mad
        self.upper = self.median + deviation
        self.lower = self.median - deviation

        self.plot = self.axes.imshow(data, vmin=self.lower, vmax=self.upper)
        
        #print "Not reached"
        self.plot.set_clim(vmin=self.lower, vmax=self.upper)
        self.plot.set_cmap(cmap)
        self.figure.tight_layout()
    
    def refresh(self):
        self.canvas.draw()
        self.canvas.Refresh()
    
    def clear(self):
        self.axes.clear()

    def getData(self, image):
        return fits.getdata(image)

    def updateScreenStats(self):
        self.parent.stats.SetStatusText("Min: %.0f"%(self.min), 0)
        self.parent.stats.SetStatusText("Max: %.0f"%(self.max), 1)
        self.parent.stats.SetStatusText("Mean: %.1f"%(self.mean), 2)
        #self.parent.stats.SetStatusText("Mode: %.0f"%(self.mode), 3)
        self.parent.stats.SetStatusText("Median: %.0f"%(self.median), 3)


    def updatePassedStats(self, stats_list):  # list needs to be [min, max, mean, median]
        self.min = stats_list[0]
        self.max = stats_list[1]
        self.mean = stats_list[2]
        #self.mode = stats_list[3]
        self.median = stats_list[3]

    def updateStats(self, data):
        self.min = np.min(data.flat)
        self.max = np.max(data.flat)
        self.mean = np.mean(data.flat)
        self.median = np.median(data.flat)

    def updateLims(self, min, max):
        self.plot.set_clim(vmin=min, vmax=max)

    def updateCmap(self, cmap):
        self.plot.set_cmap(cmap)

    def closeFig(self):
        plt.close('all')



class TakeImage(wx.Panel): ## first tab; with photo imaging

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        # Things to add:  add updating text for temperature in bottom left of GUI
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


class OtherParams(wx.Panel): # second tab; with other parameters like setting the temperature to cool.

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        # Main Sizers
        self.vertSizer = wx.BoxSizer(wx.VERTICAL)
        self.horzSizer = wx.BoxSizer(wx.HORIZONTAL)

        ### Sub-sizers

        # Place items
        als.AddLinearSpacer(self.horzSizer, 20)
        self.horzSizer.Add(cc.Binning(self))

        als.AddLinearSpacer(self.vertSizer, 20)
        self.vertSizer.Add(self.horzSizer)

        self.SetSizer(self.vertSizer)
        self.vertSizer.Fit(self)


class Log(wx.Panel): # fourth tab; with logging of each command

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        ## Main Sizers
        self.vertSizer = wx.BoxSizer(wx.VERTICAL)
        self.horzSizer = wx.BoxSizer(wx.HORIZONTAL)

        # sub sizers
        self.logInstance = lc.logBox(self)

        # adjust sub sizers


        # adjust main sizers
        #als.AddLinearSpacer(self.horzSizer, 5)
        #self.horzSizer.Add(lc.logBox(self), flag=wx.ALIGN_CENTER)

        als.AddLinearSpacer(self.vertSizer, 20)
        self.vertSizer.Add(self.logInstance, proportion=1, flag=wx.ALIGN_CENTER|wx.EXPAND)

        self.SetSizer(self.vertSizer)
        self.vertSizer.Fit(self)

class Scripting(wx.Panel): # 3rd tab that handles scripting

    def __init__(self,parent):
        wx.Panel.__init__(self, parent)

        self.parent = parent

        ## Main Sizers
        self.vertSizer = wx.BoxSizer(wx.VERTICAL)
        self.horzSizer = wx.BoxSizer(wx.HORIZONTAL)

        ## Subsizers

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
    def __init__(self):
        self.output = None
        self._deferreds = {}

    def dataReceived(self, data):
        print("Receieved:", data)
        
        gui = self.factory.gui
            
        gui.protocol = self
        gui.takeImage.exposureInstance.protocol = self
        gui.takeImage.tempInstance.protocol = self
        gui.takeImage.filterInstance.protocol = self
        gui.scripting.scriptCommands.protocol = self

        if gui:
            val = gui.log.logInstance.logBox.GetValue()
            #print val
            gui.log.logInstance.logBox.SetValue(val + data)
            gui.log.logInstance.logBox.SetInsertionPointEnd()
            #sep_data = data.split(" ")
            #print sep_data
        
        # if there is more than one line that was sent and received 
        sep_data = data.rsplit() # split for multiple lines
        size = len(sep_data) # size of sep_data will always be even (key followed by data pair)
        for i in range(0, size, 2):
            singular_sep_data = [sep_data[i], sep_data[i+1]]

            #print singular_sep_data
            if singular_sep_data[0] in self._deferreds:
                self._deferreds.pop(singular_sep_data[0]).callback(singular_sep_data[1])
        
    def sendCommand(self, data):
        self.sendLine(data)
        d = self._deferreds[data.split(" ")[0]] = defer.Deferred()
        return d

    def connectionMade(self):
        self.output = self.factory.gui.log.logInstance.logBox
        
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
        ## Add a "callback" that will close down the gui functionality when camera connection is closed.
        #gui = self.factory.gui
        #gui.onDisconnectCallback()
        pass



class EvoraClient(protocol.ClientFactory):
    def __init__(self, gui):
        self.gui = gui
        self.protocol = EvoraForwarder

    def clientConnectionLost(self, transport, reason):
        print("connection Lost")
        #reactor.stop()

    def clientConnectionFailed(self, transport, reason):
        reactor.stop()


if __name__ == "__main__":
    #log.startLogging(sys.stdout)

    app = wx.App(False)
    app.frame1 = Evora()
    app.frame1.Show()
    #app.frame2 = ImageWindow()
    #app.frame2.Show()
    reactor.registerWxApp(app)
    #reactor.connectTCP("localhost", 5502, EvoraClient(app.frame1))
    reactor.run()
    app.MainLoop()
    
