#!/usr/bin/python

import wx
import AddLinearSpacer as als
import numpy as np

## Class that handles widgets related to exposure
class Exposure(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        ### Main sizers
        self.vertSizer = wx.BoxSizer(wx.VERTICAL)
        self.horzSizer = wx.BoxSizer(wx.HORIZONTAL)

        #####

        ### Additional sub sizers
        self.exposeSizer = wx.BoxSizer(wx.HORIZONTAL) # used for spacing expTime and expValue
        self.buttonSizer = wx.BoxSizer(wx.HORIZONTAL) # used for spacing expose and stop buttons
        self.nameSizer = wx.BoxSizer(wx.VERTICAL) # use for spacing name text and text ctrl
        #####

        #### Widgets
        self.expTime = wx.StaticText(self, id=2000, label="Exposure Time (s)")
        self.name = wx.StaticText(self, id=2001, label="Save Name")
        self.nameField = wx.TextCtrl(self, id=2002, size=(150, -1))
        self.expValue = wx.TextCtrl(self, id=2003, size=(45, -1))
        self.expButton = wx.Button(self, id=2004, label="Expose", size=(60, -1))
        self.stopExp = wx.Button(self, id=2005, label="Stop", size=(60,-1))
        self.expBox = wx.StaticBox(self, id=2006, label = "Exposure Controls", size=(100,100), style=wx.ALIGN_CENTER)
        self.expBoxSizer = wx.StaticBoxSizer(self.expBox, wx.VERTICAL)
        #####

        ##### Line up smaller sub sizers

        als.AddLinearSpacer(self.exposeSizer, 15)
        self.exposeSizer.Add(self.expTime, flag=wx.ALIGN_CENTER)
        als.AddLinearSpacer(self.exposeSizer, 15)
        self.exposeSizer.Add(self.expValue, flag=wx.ALIGN_CENTER)
        als.AddLinearSpacer(self.exposeSizer, 15)

        self.buttonSizer.Add(self.expButton, flag=wx.ALIGN_CENTER)
        als.AddLinearSpacer(self.buttonSizer, 10)
        self.buttonSizer.Add(self.stopExp, flag=wx.ALIGN_CENTER)

        self.nameSizer.Add(self.name, flag=wx.ALIGN_CENTER)
        als.AddLinearSpacer(self.nameSizer, 8)
        self.nameSizer.Add(self.nameField, flag=wx.ALIGN_CENTER)

        ####

        #### Line up larger chuncks with main sizer
        als.AddLinearSpacer(self.expBoxSizer, 10)
        self.expBoxSizer.Add(self.nameSizer, flag=wx.ALIGN_CENTER)
        als.AddLinearSpacer(self.expBoxSizer, 5)
        self.expBoxSizer.Add(self.exposeSizer, flag=wx.ALIGN_CENTER)
        als.AddLinearSpacer(self.expBoxSizer, 5)
        self.expBoxSizer.Add(self.buttonSizer, flag=wx.ALIGN_CENTER)
        als.AddLinearSpacer(self.expBoxSizer, 5)

        self.vertSizer.Add(self.expBoxSizer, flag=wx.ALIGN_CENTER)

        ####

        ## variables
        self.timeToSend = 0.0
        self.nameToSend = ""


        ### Bindings
        self.Bind(wx.EVT_TEXT, self.nameText, id=2002)
        self.Bind(wx.EVT_TEXT, self.onExpTime, id=2003)
        self.Bind(wx.EVT_BUTTON, self.onExpose, id=2004)
        self.Bind(wx.EVT_BUTTON, self.onStop, id=2005)
        ###

        self.SetSizer(self.vertSizer)
        self.vertSizer.Fit(self)

    def nameText(self, event):
        self.nameToSend = self.nameField.GetValue()

    def onExpTime(self, event):
        self.timeToSend = self.expValue.GetValue()

    def onExpose(self, event):
        if als.isNumber(self.timeToSend):
            print float(self.timeToSend)
        else:
            dialog = wx.MessageDialog(None, "Exposure time not a number...will not expose.", "", wx.OK|wx.ICON_ERROR)
            dialog.ShowModal()

        if self.nameToSend is "":
            dialog = wx.MessageDialog(None,"No name was given...will not expose", "", wx.OK|wx.ICON_ERROR)
            dialog.ShowModal()
        else:
            print self.nameToSend

    def onStop(self, event):
        print "Stop Exposure"


# Class that handles Radio boxes for image types and exposure types
class TypeSelection(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        ### Main Sizers
        self.vertSizer = wx.BoxSizer(wx.VERTICAL)
        self.horzSizer = wx.BoxSizer(wx.HORIZONTAL)

        #### Additianl Sub Sizers
        self.radioSizer = wx.BoxSizer(wx.HORIZONTAL)

        ### Widgets (specifially radio boxes)
        self.imageType = wx.RadioBox(self, id=2010, label="Image Type", size=wx.DefaultSize, \
                         choices=["Bias", "Flat", "Dark", "Object"], style=wx.RA_HORIZONTAL)
        self.exposeType = wx.RadioBox(self, id=2011, label = "Exposure Type", size=wx.DefaultSize, \
                          choices=["Single", "Real Time", "Series"], style=wx.RA_HORIZONTAL)

        ### Line up sub-chunks
        self.radioSizer.Add(self.imageType)
        als.AddLinearSpacer(self.radioSizer, 50)
        self.radioSizer.Add(self.exposeType)

        #### Line up big chuncks
        self.vertSizer.Add(self.radioSizer)

        ####

        ### Bindings
        self.Bind(wx.EVT_RADIOBOX, self.onImageType, id=2010)
        self.Bind(wx.EVT_RADIOBOX, self.onExposeType, id=2011)
        ###

        self.SetSizer(self.vertSizer)
        self.vertSizer.Fit(self)

    def onImageType(self, event):
        index = self.imageType.GetSelection()
        print self.imageType.GetStringSelection()

    def onExposeType(self, event):
        index = self.exposeType.GetSelection()
        print self.exposeType.GetStringSelection()


class TempControl(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        ### Main sizers
        self.vertSizer = wx.BoxSizer(wx.VERTICAL)
        self.horzSizer = wx.BoxSizer(wx.HORIZONTAL)

        #####

        ### Additional sub sizers
        self.tempSizer = wx.BoxSizer(wx.HORIZONTAL) # used for spacing tempText and tempValue
        self.buttonSizer = wx.BoxSizer(wx.HORIZONTAL) # used for spacing expose and stop buttons
        #####

        #### Widgets
        self.tempText = wx.StaticText(self, id=2030, label="Temperature (C)")
        self.tempValue = wx.TextCtrl(self, id=2031, size=(45, -1), style=wx.TE_PROCESS_ENTER)
        self.tempButton = wx.Button(self, id=2032, label="Cool", size=(60, -1))
        self.stopExp = wx.Button(self, id=2033, label="Stop", size=(60,-1))
        self.tempBox = wx.StaticBox(self, id=2034, label="Temperature Controls", size=(100,100), style=wx.ALIGN_CENTER)
        self.tempBoxSizer = wx.StaticBoxSizer(self.tempBox, wx.VERTICAL)
        #####

        ##### Line up smaller sub sizers

        als.AddLinearSpacer(self.tempSizer, 10)
        self.tempSizer.Add(self.tempText, flag=wx.ALIGN_CENTER)
        als.AddLinearSpacer(self.tempSizer, 10)
        self.tempSizer.Add(self.tempValue, flag=wx.ALIGN_CENTER)
        als.AddLinearSpacer(self.tempSizer, 25)

        self.buttonSizer.Add(self.tempButton, flag=wx.ALIGN_CENTER)
        als.AddLinearSpacer(self.buttonSizer, 10)
        self.buttonSizer.Add(self.stopExp, 1, flag=wx.ALIGN_CENTER)


        ####

        #### Line up larger chunks with main sizer
        als.AddLinearSpacer(self.tempBoxSizer, 5)
        self.tempBoxSizer.Add(self.tempSizer, flag=wx.ALIGN_CENTER)
        als.AddLinearSpacer(self.tempBoxSizer, 5)
        self.tempBoxSizer.Add(self.buttonSizer, flag=wx.ALIGN_CENTER)
        als.AddLinearSpacer(self.tempBoxSizer, 15)
        self.vertSizer.Add(self.tempBoxSizer, flag=wx.ALIGN_CENTER)
        ####

        ### Variables
        self.tempToSend = 0.0

        ## Bindings
        self.Bind(wx.EVT_TEXT, self.getTemp, id=2031)
        self.Bind(wx.EVT_BUTTON, self.onCool, id=2032)
        self.Bind(wx.EVT_BUTTON, self.onStopCooling, id=2033)
        ##


        self.SetSizer(self.vertSizer)
        self.vertSizer.Fit(self)

    def getTemp(self, event):
        self.tempToSend = self.tempValue.GetValue()

    def onCool(self, event):
        if als.isNumber(self.tempToSend):
            print float(self.tempToSend)
        else:
            dialog = wx.MessageDialog(None, "Temperature specified is not a number.", "", wx.OK|wx.ICON_ERROR)
            dialog.ShowModal()

    def onStopCooling(self, event):
        print "Stopping Cooler"

class FilterControl(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        ### Main sizers
        self.vertSizer = wx.BoxSizer(wx.VERTICAL)


        ### Additional Sub-sizers
        self.filterSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.subVert = wx.BoxSizer(wx.VERTICAL)
        self.statusVert = wx.BoxSizer(wx.VERTICAL)

        ## Variables
        self.filterList = np.genfromtxt("filters.txt", dtype='str').tolist()
        ##

        #### Widgets
        self.filterBox = wx.StaticBox(self, id=2040, label = "Filter Controls", size=(100,100), style=wx.ALIGN_CENTER)
        self.filBoxSizer = wx.StaticBoxSizer(self.filterBox, wx.VERTICAL)

        self.statusBox = wx.StaticBox(self, id=2041, label = "Filter Status", size=(150,150), style=wx.ALIGN_CENTER)
        self.statusBoxSizer = wx.StaticBoxSizer(self.statusBox, wx.VERTICAL)

        self.filterText = wx.StaticText(self, id=2042, label="Filter Type")
        self.filterMenu = wx.ComboBox(self, id=2043, choices=["g", "r", "i", "V", "B", "Ha"], size=(50, -1), style=wx.CB_READONLY)
        self.filterButton = wx.Button(self, id=2044, label = "Rotate To")
        self.statusBox = wx.TextCtrl(self, id=2045, style=wx.TE_READONLY|wx.TE_MULTILINE, size=(200,100))


        #### Line Up Smaller Sub Sizers

        self.filterSizer.Add(self.filterText, flag=wx.ALIGN_CENTER)
        als.AddLinearSpacer(self.filterSizer, 15)
        self.filterSizer.Add(self.filterMenu, flag=wx.ALIGN_CENTER)

        self.subVert.Add(self.filterSizer)
        als.AddLinearSpacer(self.subVert, 10)
        self.subVert.Add(self.filterButton, flag=wx.ALIGN_CENTER)


        self.filBoxSizer.Add((200, 10))
        self.filBoxSizer.Add(self.subVert, flag=wx.ALIGN_CENTER)
        self.filBoxSizer.Add((0,30))

        self.statusBoxSizer.Add(self.statusBox, flag=wx.ALIGN_CENTER)

        #### Line up larger chunks with main sizers
        self.vertSizer.Add(self.filBoxSizer)
        als.AddLinearSpacer(self.vertSizer, 15)
        self.vertSizer.Add(self.statusBoxSizer)

        ## Variables
        self.filterSelection = ""
        ##

        ## Bindings
        self.Bind(wx.EVT_COMBOBOX, self.onFilterSelection, id=2043)
        self.Bind(wx.EVT_BUTTON, self.onRotate, id=2044)
        ##

        self.SetSizer(self.vertSizer)
        self.vertSizer.Fit(self)

    def onFilterSelection(self, event):
        self.filterSelection = self.filterMenu.GetValue()

    def onRotate(self, event):
        if self.filterSelection is "":
            print "No filter selected"
        else:
            print self.filterSelection

    def refreshList(self):
        self.filterMenu.Clear()
        newList = np.genfromtxt('filters.txt', dtype='str').tolist()
        for i in newList:
            self.filterMenu.Append(i)
