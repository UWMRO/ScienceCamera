#!/usr/bin/python

import wx
import AddLinearSpacer as als

# Class that handles selection of different types of binning
class Binning(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        ### Main Sizers
        self.vertSizer = wx.BoxSizer(wx.VERTICAL)
        
        ###

        ### Additional Sub-sizers


        ### Widgets
        self.binType = wx.RadioBox(self, label="Binning Type", size=wx.DefaultSize, choices=["1X1", "2X2"], style=wx.RA_HORIZONTAL)


        ### Line up smaller Sub-sizers



        ### Line up main sizers
        self.vertSizer.Add(self.binType, flag=wx.ALIGN_CENTER)

        self.SetSizer(self.vertSizer)
        self.vertSizer.Fit(self)
