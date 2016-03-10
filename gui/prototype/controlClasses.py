#!/usr/bin/python

import wx # get wxPython
import AddLinearSpacer as als # access to simple functions

# Class that handles selection of different types of binning
class Binning(wx.Panel):
    """
    Currently not in use, where it would be held in the Controls tab.

    This class creates the panel that holds the widgets for Binning Type
    """

    def __init__(self, parent):
        """
        Initailizes panel with radio box widget that handles the selection of binning type.
        """
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
