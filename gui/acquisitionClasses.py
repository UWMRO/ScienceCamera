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
        #####

        ##### Line up smaller sub sizers

        self.exposeSizer.Add(self.expTime, flag=wx.ALIGN_CENTER)
        als.AddLinearSpacer(self.exposeSizer, 10)
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
        als.AddLinearSpacer(self.horzSizer, 25)

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
        self.radioSizer = wx.BoxSizer(wx.HORIZONTAL)


        ### Widgets (specifially radio boxes)
