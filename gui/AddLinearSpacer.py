#!/usr/bin/python

import wx # get wxPython
from astropy.io import fits
import numpy as np
from scipy import stats
import threading
import time

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

class SampleTimer(object):
    def __init__(self, timeLength):
        self.end = timeLength
        
        self.tick = 10 * 10 ** -3 # tick is 10 milliseconds

        self.stopTimer = False

        self.currentTick = 0
        self.totalTicks = self.end / self.tick
        
    def timer(self):
        while not self.stopTimer:
            if(self.currentTick == self.totalTicks):
                self.currentTick = 0
            else:
                self.currentTick += 1
            time.sleep(0.01)

    def sample(self):
        return [self.currentTick, self.totalTicks]

    def stop(self):
        self.stopTimer = True
        self.t.join(0)
                
    def start(self):
        self.stopTimer = False
        self.currentTick = 1
        self.t = threading.Thread(target=self.timer, args=())
        self.t.daemon = True
        self.t.start()
    
