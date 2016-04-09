#!/usr/bin/python

import wx
import acquisitionClasses as ac
import controlClasses as cc
import scriptingClasses as sc
import logClasses as lc
import AddLinearSpacer as als
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

# twisted imports
from twisted.python import log
from twisted.internet import wxreactor, protocol
wxreactor.install()

# always goes after wxreactor install
from twisted.internet import reactor
from twisted.protocols import basic

# Frame class.
class Evora(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, None, -1, "Evora Acquisition GUI", size = (600, 450))

        self.protocol = None # client protocol

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
        self.binning = "1"

        ## Menu
        menuBar = wx.MenuBar()

        ## Sub menus
        filterSub = wx.Menu()
        filterSub.Append(1110, "&Connect", "Connect to the filter")
        filterSub.Append(1111, "&Refresh", "Refresh filter list")

        binningSub = wx.Menu()
        binningSub.Append(1120, "1x1", "Set CCD readout binning", kind=wx.ITEM_RADIO)
        binningSub.Append(1121, "2x2", "Set CCD readout binning", kind=wx.ITEM_RADIO)

        # create main menus
        fileMenu = wx.Menu()
        fileMenu.AppendMenu(1001, "&Filter", filterSub)
        fileMenu.AppendMenu(1002, "&Binning", binningSub)
        fileMenu.Append(1000, "&Exit", "Quit from Evora")

        viewMenu = wx.Menu()
        viewMenu.Append(1200, "&Image", "Open Image Window")

        helpMenu = wx.Menu()
        helpMenu.Append(1300, "&Help")

        # add to menu bar
        menuBar.Append(fileMenu, "&File")
        menuBar.Append(viewMenu, "&View")
        menuBar.Append(helpMenu, "&Help")
        # instantiate menubar
        self.SetMenuBar(menuBar)

        ## Status Bar:  include temperature, binning type, gauge for exposure
        self.stats = EnhancedStatusBar.EnhancedStatusBar(self)
        self.stats.SetSize((23,-1))
        self.stats.SetFieldsCount(3)
        self.SetStatusBar(self.stats)
        self.stats.SetStatusText("Current Temp:        0 C", 0)
        self.stats.SetStatusText("Binning Type: ...", 2)
        self.stats.SetStatusText("Exp. Status:", 1)
        self.expGauge = wx.Gauge(self.stats, id=1, range=100, size=(110, -1))
        self.stats.AddWidget(self.expGauge, pos=1, horizontalalignment=EnhancedStatusBar.ESB_ALIGN_RIGHT)
        bitmap = wx.StaticBitmap(self.stats, -1, size=(90, 0))
        bitmap.SetBitmap(wx.Bitmap('greenCirc.png'))
        #tempText = wx.StaticText(self.stats, -1, label="50 C")
        self.stats.AddWidget(bitmap, pos=0, horizontalalignment=EnhancedStatusBar.ESB_ALIGN_RIGHT)
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
        #self.Bind(wx.EVT_CLOSE, self.onClose)

        #wx.EVT_CLOSE(self, lambda evt: reactor.stop())

        panel.SetSizer(sizer)
        panel.Layout()

    ## Memory upon destruction seems to not release.  This could cause memory usage to increase
    ## with newly loaded images when using the evora camera.
    def openImage(self, event):
        self.window = ImageWindow(self)
        self.window.Show()

    def onClose(self, event):
        dialog = wx.MessageDialog(None, "Close Evora GUI?", "Closing Evora", wx.OK | wx.CANCEL|wx.ICON_QUESTION)
        answer = dialog.ShowModal()
        dialog.Destroy()
        #print answer
        if answer == wx.ID_OK:
            self.protocol.sendLine("shutdown")
            self.Destroy()
            reactor.stop()

    def onHelp(self, event):
        print "Help"

    def onRefresh(self, event):
        self.takeImage.filterInstance.refreshList()
        print "hello"

    def on1x1(self, event):
        self.binning = "1"
        self.stats.SetStatusText("Binning Type: 1x1", 2)

    def on2x2(self, event):
        self.binning = "2"
        self.stats.SetStatusText("Binning Type: 2x2", 2)



class ImageWindow(wx.Frame):

    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, "Image Window", size=(650,550))

        self.image = 'example.fit'

        ## Main sizers
        self.topSizer = wx.BoxSizer(wx.VERTICAL)
        self.sideSizer = wx.BoxSizer(wx.HORIZONTAL)

        ## Minor Sizers
        self.sliderSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.panel = DrawImage(self)

        self.data = self.panel.getData(self.image)

        ### Put in matplotlib imshow window
        self.panel.plotImage(self.data, 6.0, 'gray')
        self.devSlider = wx.Slider(self, id=-1, value=60, minValue=1, maxValue=200, size=(250,-1),\
                         style=wx.SL_HORIZONTAL)
        self.invert = wx.CheckBox(self, id=-1, label="Invert")
        self.invert.SetValue(False)
        self.text = wx.StaticText(self, label='Contrast:')

        self.stats = self.CreateStatusBar(5)
        self.stats.SetStatusStyles([1,1,1,1,1])
        self.stats.SetStatusText("Min: %.0f"%(self.panel.min), 0)
        self.stats.SetStatusText("Max: %.0f"%(self.panel.max), 1)
        self.stats.SetStatusText("Mean: %.1f"%(self.panel.mean), 2)
        self.stats.SetStatusText("Mode: %.0f"%(self.panel.mode), 3)
        self.stats.SetStatusText("Median: %.0f"%(self.panel.median), 4)


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

        self.SetSizer(self.topSizer)
        self.Fit()


    def onSlide(self, event):
        value = float(event.GetPosition()) / 10.0
        lower = self.panel.median - value * self.panel.mad
        upper = self.panel.median + value * self.panel.mad
        self.panel.updateLims(lower, upper)
        self.panel.refresh()

    def onClose(self, event):
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



class DrawImage(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

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
        self.mode = 0
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
        # get data

        self.min = np.min(data.flat)
        self.max = np.max(data.flat)
        self.mean = np.mean(data.flat)
        self.median = np.median(data.flat)
        self.mode = stats.mode(data.flat)[0][0]

        self.mad = np.median(np.abs(data.flat-self.median)) # median absolute deviation
        deviation = scale * self.mad
        self.upper = self.median + deviation
        self.lower = self.median - deviation

        self.plot = self.axes.imshow(data, vmin=self.lower, vmax=self.upper)
        self.plot.set_clim(vmin=self.lower, vmax=self.upper)
        self.plot.set_cmap(cmap)
        self.figure.tight_layout()
    
    def refresh(self):
        self.canvas.draw()
        self.canvas.Refresh()

    def getData(self, image):
        return fits.getdata(image)

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

        ## Main Sizers
        self.vertSizer = wx.BoxSizer(wx.VERTICAL)
        self.horzSizer = wx.BoxSizer(wx.HORIZONTAL)

        ## Subsizers

        # adjust subsizers


        # adjust main sizers
        als.AddLinearSpacer(self.horzSizer, 15)
        self.horzSizer.Add(sc.ScriptStatus(self), flag=wx.ALIGN_CENTER)


        als.AddLinearSpacer(self.vertSizer, 15)
        self.vertSizer.Add(sc.ScriptCommands(self), flag=wx.ALIGN_CENTER)
        als.AddLinearSpacer(self.vertSizer, 15)
        self.vertSizer.Add(self.horzSizer, flag=wx.ALIGN_CENTER)


        self.SetSizer(self.vertSizer)
        self.vertSizer.Fit(self)

### Classes for twisted
class EvoraForwarder(basic.LineReceiver):
    def __init__(self):
        self.output = None

    def dataReceived(self, data):
        gui = self.factory.gui
        
        gui.protocol = self
        gui.takeImage.exposureInstance.protocol = self
        gui.takeImage.tempInstance.protocol = self

        if gui:
            val = gui.log.logInstance.logBox.GetValue()
            gui.log.logInstance.logBox.SetValue(val + data)
            gui.log.logInstance.logBox.SetInsertionPointEnd()

    def connectionMade(self):
        self.output = self.factory.gui.log.logInstance.logBox

class EvoraClient(protocol.ClientFactory):
    def __init__(self, gui):
        self.gui = gui
        self.protocol = EvoraForwarder

    def clientConnectionLost(self, transport, reason):
        reactor.stop()

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
    reactor.connectTCP("localhost", 5502, EvoraClient(app.frame1))
    reactor.run()
    app.MainLoop()
