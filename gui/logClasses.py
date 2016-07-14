#!/usr/bin/python2

# Python 3 like changes
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

# Comment on documentation:
# When reading the doc strings if "Pre:" is present then this stands for "precondition", or the conditions in order to invoke something.
# Oppositely, "Post:" stands for "postcondition" and states what is returned by the method.

__author__ = "Tristan J. Hillis"

## Imports
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


    def threadSafeLogStatus(self, string):
        """ 
        Note: This should be called with with wx.CallAfter to update a GUI element.
        Pre: Takes in a string.
        Post: Displays that string in the log status box in the log tab of the gui.
        """
        msg = als.timeStamp() + " " + string
        val = self.logBox.GetValue()
        self.logBox.SetValue(val + msg + "\n")
        self.logBox.SetInsertionPointEnd()
