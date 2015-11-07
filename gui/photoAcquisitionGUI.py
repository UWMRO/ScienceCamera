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


# Frame class.
class Evora(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, None, -1, "Evora Acquisition GUI", size = (700, 600))

        panel = wx.Panel(self)
        notebook = wx.Notebook(panel)

        # define the each tab
        page1 = TakeImage(notebook)
        page2 = OtherParams(notebook)
        page3 = Scripting(notebook)
        page4 = Log(notebook)

        # add each tab to the notebook
        notebook.AddPage(page1, "Imaging")
        notebook.AddPage(page2, "Controls")
        notebook.AddPage(page3, "Scripting")
        notebook.AddPage(page4, "Log")

        # make instances of the tabs to access variables within them
        self.takeImage = notebook.GetPage(0)
        self.otherParams = notebook.GetPage(1)
        self.scripting = notebook.GetPage(2)
        self.log = notebook.GetPage(3)

        ## Menu
        self.menuBar = wx.MenuBar()

        # create menus
        self.fileMenu = wx.Menu()
        self.fileMenu.Append(-1, "Exit Program")

        self.helpMenu = wx.Menu()
        self.helpMenu.Append(-1, "Help")

        # add to menu bar
        self.menuBar.Append(self.fileMenu, "File")
        self.menuBar.Append(self.helpMenu, "Help")

        # size panels
        sizer = wx.BoxSizer()
        sizer.Add(notebook, 1, wx.EXPAND)

        self.SetMenuBar(self.menuBar)
        panel.SetSizer(sizer)
        panel.Layout()

class ImageWindow(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, None, -1, "Image Window", size=(650,550))

        self.image = 'example.fit'

        ## Main sizers
        self.topSizer = wx.BoxSizer(wx.VERTICAL)
        self.sideSizer = wx.BoxSizer(wx.HORIZONTAL)

        # add ability to invert gray scale with check radio BoxSizer
        # add min, max, mean, mode, and median as static text

        self.panel = DrawImage(self)



        ### Put in matplotlib imshow window
        self.panel.plotImage(self.image, 6.0)
        self.devSlider = wx.Slider(self, id=-1, value=60, minValue=1, maxValue=200, size=(250,-1),\
                         style=wx.SL_HORIZONTAL | wx.SL_LABELS)




        self.topSizer.Add(self.panel, proportion=1, flag=wx.EXPAND)
        self.topSizer.Add(self.devSlider, flag=wx.ALIGN_CENTER)


        self.devSlider.Bind(wx.EVT_SCROLL_CHANGED, self.onSlide)

        self.SetSizer(self.topSizer)
        self.Fit()


    def onSlide(self, event):
        value = float(event.GetPosition()) / 10.0
        self.panel.plotImage(self.image, value)
        self.panel.refresh()






class DrawImage(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        # Create figure, plot space, and canvas for drawing fit image
        self.figure, self.axes = plt.subplots(1)
        self.figure.frameon = False
        self.canvas = FigureCanvas(self, -1, self.figure)
        #self.toolbar = Toolbar(self.canvas)
        #self.toolbar.Realize()


        # set sizers
        self.vertSizer = wx.BoxSizer(wx.VERTICAL)
        #self.horzSizer = wx.BoxSizer(wx.HORIZONTAL)

        # add to sizers

        self.vertSizer.Add(self.canvas, proportion=1, flag=wx.LEFT | wx.TOP | wx.GROW)
        #self.vertSizer.Add(self.toolbar, proportion=0, flag= wx.EXPAND)


        self.SetSizer(self.vertSizer)
        self.Fit()

    def plotImage(self, image, scale):
        # get data
        hdulist = fits.open(image)
        data = hdulist[0].data
        hdulist.close()

        median = np.median(data.flat)
        self.mad = np.median(np.abs(data.flat-median)) # median absolute deviation
        self.deviation = scale * self.mad
        self.upper = median + self.deviation
        self.lower = median - self.deviation


        plot = self.axes.imshow(data, cmap='gray', vmin=self.lower, vmax=self.upper)
        self.figure.tight_layout()

        #self.canvas.draw()
        #self.canvas.Refresh()

    def refresh(self):
        self.canvas.draw()
        self.canvas.Refresh()










class TakeImage(wx.Panel): ## first tab; with photo imaging

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        # Things to add: drop down menu for filters
        #                drop down menu for type of image
        #                add button to filter drop down menu
        #                add button for taking exposure
        #                add updating text for temperature in bottom left of GUI

        # Add functionalality here
        #self.expTime = wx.StaticText(self, label="Exposure Time (s)")
        #self.expValue = wx.TextCtrl(self, size=(75, -1), style=wx.TE_PROCESS_ENTER)
        #self.expValue.SetStyle(self, style=wx.TE_PROCESS_ENTER)
        #self.expButton = wx.Button(self, label="Expose", size=(60, -1))

        # Set sizers so I have horizontal and vertical control
        self.topbox = wx.BoxSizer(wx.VERTICAL)
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)

        ### Sub sizer
        self.leftVert = wx.BoxSizer(wx.VERTICAL)

        ## Place sections

        als.AddLinearSpacer(self.hbox, 30)
        self.leftVert.Add(ac.Exposure(self))
        als.AddLinearSpacer(self.leftVert, 20)
        self.leftVert.Add(ac.TypeSelection(self), flag=wx.ALIGN_CENTER)
        als.AddLinearSpacer(self.leftVert, 20)
        self.leftVert.Add(ac.TempControl(self))


        self.hbox.Add(self.leftVert)
        als.AddLinearSpacer(self.hbox, 180)

        self.hbox.Add(ac.FilterControl(self))


        als.AddLinearSpacer(self.topbox, 15)
        self.topbox.Add(self.hbox, proportion=5, flag=wx.EXPAND)



        #self.Bind(wx.EVT_TEXT_ENTER, self.getExpVal, self.expValue)
        #self.Bind(wx.EVT_BUTTON, self.getValsButton, self.)

        # comes last
        self.SetSizer(self.topbox)
        self.topbox.Fit(self)
        #self.Layout()

    def getExpVal(self, e):
        self.exp = self.expValue.GetValue()
        print float(self.exp)

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


        # adjust sub sizers


        # adjust main sizers
        #als.AddLinearSpacer(self.horzSizer, 5)
        #self.horzSizer.Add(lc.logBox(self), flag=wx.ALIGN_CENTER)

        als.AddLinearSpacer(self.vertSizer, 40)
        self.vertSizer.Add(lc.logBox(self), flag=wx.ALIGN_CENTER)

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



if __name__ == "__main__":
    app = wx.PySimpleApp()
    app.frame1 = Evora()
    app.frame1.Show()
    app.frame2 = ImageWindow()
    app.frame2.Show()
    app.MainLoop()
