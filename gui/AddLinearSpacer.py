#!/usr/bin/python

import wx # get wxPython
from astropy.io import fits
import numpy as np
from scipy import stats

def AddLinearSpacer(boxsizer, pixelSpacing) :
    """
    A one-dimensional spacer along only the major axis for any BoxSizer

    Found this on a wxPython tutorial and it has proved to be very handy.

    It takes in a box sizer as boxsizer and the spacing as pixelSpacing and expands the
    passed in sizer along its major axis.  This is used over boxsizer.AddSpacer(...) as this
    expands along both axises causing untold issues.  It also is more intuitive than
    boxsizer.AddSpacer((..,..)) where you pass a 0 to the width or height to obtain the same
    results.
    """
    orientation = boxsizer.GetOrientation()
    if   (orientation == wx.HORIZONTAL) :
        boxsizer.Add( (pixelSpacing, 0) )
    elif (orientation == wx.VERTICAL) :
        boxsizer.Add( (0, pixelSpacing) )

def isNumber(string):
    """
    Takes in a string and trys to convert it to a float, upon success it returns True and if
    it fails then it returns false.  Useful in the usage of when I want to test is a string
    is a number or not.
    """
    try:
        float(string)
        return True
    except ValueError:
        return False


def getData(path):
    return fits.getdata(path)

def calcStats(data):
    stats_list = []
    stats_list.append(min(data.flat))
    stats_list.append(max(data.flat))
    stats_list.append(np.mean(data.flat))
    #stats_list.append(stats.mode(data.flat)[0][0])
    stats_list.append(np.median(data.flat))
    
    return stats_list
