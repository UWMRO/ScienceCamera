#!/usr/bin/python

import wx
import AddLinearSpacer as als

class logBox(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        # Main Sizers
        #self.vertSizer = wx.BoxSizer(wx.VERTICAL)


        # subsizers


        # widgets
        self.logFrame = wx.StaticBox(self, label = "Event Log", size=(500, 300), style=wx.ALIGN_CENTER)
        self.logFrameSizer = wx.StaticBoxSizer(self.logFrame, wx.VERTICAL)

        self.logBox = wx.TextCtrl(self, size=(500,300), style=wx.TE_READONLY|wx.TE_MULTILINE)


        # adjust subsizers
        self.logFrameSizer.Add(self.logBox, proportion=1, flag=wx.ALIGN_CENTER|wx.EXPAND)


        # adjust main sizers
        #self.vertSizer.Add(self.logFrameSizer, flag=wx.ALIGN_CENTER)


        self.SetSizer(self.logFrameSizer)
        self.logFrameSizer.Fit(self)
