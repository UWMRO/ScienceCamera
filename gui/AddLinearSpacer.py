#!/usr/bin/python

import wx

def AddLinearSpacer(boxsizer, pixelSpacing) :
    """ A one-dimensional spacer along only the major axis for any BoxSizer """
    orientation = boxsizer.GetOrientation()
    if   (orientation == wx.HORIZONTAL) :
        boxsizer.Add( (pixelSpacing, 0) )
    elif (orientation == wx.VERTICAL) :
        boxsizer.Add( (0, pixelSpacing) )
