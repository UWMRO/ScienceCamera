#!/usr/bin/python

import wx
import AddLinearSpacer as als

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
        #####

        #### Widgets
        self.expTime = wx.StaticText(self, label="Exposure Time (s)")
        self.expValue = wx.TextCtrl(self, size=(45, -1), style=wx.TE_PROCESS_ENTER)
        self.expButton = wx.Button(self, label="Expose", size=(60, -1))
        self.stopExp = wx.Button(self, label="Stop", size=(60,-1))
        self.save = wx.Button(self, label="Save", size=(60,-1))
        #####

        ##### Line up smaller sub sizers

        als.AddLinearSpacer(self.exposeSizer, 15)
        self.exposeSizer.Add(self.expTime, flag=wx.ALIGN_CENTER)
        als.AddLinearSpacer(self.exposeSizer, 15)
        self.exposeSizer.Add(self.expValue, flag=wx.ALIGN_CENTER)
        als.AddLinearSpacer(self.exposeSizer, 25)

        self.buttonSizer.Add(self.expButton, flag=wx.ALIGN_CENTER)
        als.AddLinearSpacer(self.buttonSizer, 10)
        self.buttonSizer.Add(self.stopExp, flag=wx.ALIGN_CENTER)

        ####

        #### Line up larger chuncks with main sizer

        self.vertSizer.Add(self.exposeSizer, flag=wx.ALIGN_CENTER)
        als.AddLinearSpacer(self.vertSizer, 15)
        self.vertSizer.Add(self.buttonSizer, flag=wx.ALIGN_CENTER)
        als.AddLinearSpacer(self.horzSizer, 15)
        als.AddLinearSpacer(self.vertSizer, 10)

        self.vertSizer.Add(self.save, flag = wx.ALIGN_CENTER)

        ####

        self.SetSizer(self.vertSizer)
        self.vertSizer.Fit(self)

# Class that handles Radio boxes for image types and exposure types
class TypeSelection(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        ### Main Sizers
        self.vertSizer = wx.BoxSizer(wx.VERTICAL)
        self.horzSizer = wx.BoxSizer(wx.HORIZONTAL)

        #### Additianl Sub Sizers
        self.radioSizer = wx.BoxSizer(wx.VERTICAL)

        ### Widgets (specifially radio boxes)
        self.imageType = wx.RadioBox(self, label="Image Type", size=wx.DefaultSize, choices=["Bias", "Flat", "Dark", "Object"], style=wx.RA_HORIZONTAL)
        self.exposeType = wx.RadioBox(self, label = "Exposure Type", size=wx.DefaultSize, choices=["Single", "Continuous", "Series"], style=wx.RA_HORIZONTAL)

        ### Line up sub-chunks
        self.radioSizer.Add(self.imageType)
        als.AddLinearSpacer(self.radioSizer, 10)
        self.radioSizer.Add(self.exposeType)

        #### Line up big chuncks
        self.vertSizer.Add(self.radioSizer)

        ####

        self.SetSizer(self.vertSizer)
        self.vertSizer.Fit(self)


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
        self.tempText = wx.StaticText(self, label="Temperature (C)")
        self.tempValue = wx.TextCtrl(self, size=(45, -1), style=wx.TE_PROCESS_ENTER)
        self.tempButton = wx.Button(self, label="Cool", size=(60, -1))
        self.stopExp = wx.Button(self, label="Stop", size=(60,-1))
        #####

        ##### Line up smaller sub sizers

        self.tempSizer.Add(self.tempText, flag=wx.ALIGN_CENTER)
        als.AddLinearSpacer(self.tempSizer, 10)
        self.tempSizer.Add(self.tempValue, flag=wx.ALIGN_CENTER)
        als.AddLinearSpacer(self.tempSizer, 25)

        self.buttonSizer.Add(self.tempButton, flag=wx.ALIGN_CENTER)
        als.AddLinearSpacer(self.buttonSizer, 10)
        self.buttonSizer.Add(self.stopExp, 1, flag=wx.ALIGN_CENTER)


        ####

        #### Line up larger chunks with main sizer

        self.vertSizer.Add(self.tempSizer, flag=wx.ALIGN_CENTER)
        als.AddLinearSpacer(self.vertSizer, 15)
        self.vertSizer.Add(self.buttonSizer, flag=wx.ALIGN_CENTER)
        als.AddLinearSpacer(self.horzSizer, 25)

        ####

        self.SetSizer(self.vertSizer)
        self.vertSizer.Fit(self)


class FilterControl(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        ### Main sizers
        self.vertSizer = wx.BoxSizer(wx.VERTICAL)


        ### Additional Sub-sizers
        self.filterSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.subVert = wx.BoxSizer(wx.VERTICAL)
        self.statusVert = wx.BoxSizer(wx.VERTICAL)


        #### Widgets
        self.filterBox = wx.StaticBox(self, label = "Filter Controls", size=(100,100), style=wx.ALIGN_CENTER)
        self.filBoxSizer = wx.StaticBoxSizer(self.filterBox, wx.VERTICAL)

        self.filterText = wx.StaticText(self, label="Filter Type")
        self.filterMenu = wx.ComboBox(self, choices=["g", "r", "i", "V", "B", "Ha"], size=(50, -1))
        self.filterButton = wx.Button(self, label = "Rotate To")
        self.statusText = wx.StaticText(self, label="Filter Status")
        self.statusBox = wx.TextCtrl(self, style=wx.TE_READONLY, size=(200,100))


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

        self.statusVert.Add(self.statusText, flag=wx.ALIGN_CENTER)
        als.AddLinearSpacer(self.statusVert, 10)
        self.statusVert.Add(self.statusBox, flag=wx.ALIGN_CENTER)


        #### Line up larger chunks with main sizers
        self.vertSizer.Add(self.filBoxSizer)
        als.AddLinearSpacer(self.vertSizer, 20)
        self.vertSizer.Add(self.statusVert)

        self.SetSizer(self.vertSizer)
        self.vertSizer.Fit(self)
