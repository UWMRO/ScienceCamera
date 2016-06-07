#!/usr/bin/python2

import wx  # get wxPython
from astropy.io import fits
import numpy as np
import threading
import time
from datetime import datetime


def AddLinearSpacer(boxsizer, pixelSpacing):
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
    if(orientation == wx.HORIZONTAL):
        boxsizer.Add((pixelSpacing, 0))
    elif(orientation == wx.VERTICAL):
        boxsizer.Add((0, pixelSpacing))


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


def isInt(string):
    """
    Takes in a string and trys to convert it to an int.  If successful it returns True otherwise
    it captures the error and returns False.
    """
    try:
        int(string)
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
    stats_list.append(np.median(data.flat))
    return stats_list


def timeStamp():
    """
    Pre: No arguments are needed to invoke this method.
    Post: Returns a string with the current date and time.
    """
    time = datetime.today()
    stamp = "[%s/%s/%s, " % (time.month, time.day, time.year)
    stamp += "%s:%s:%s]:" % (time.hour, time.minute, time.second)
    return stamp


class SampleTimer(object):
    def __init__(self, timeLength):
        self.end = timeLength + 0.24  # add an extra 0.24 for readout and shutter time
        self.tick = 10 * 10 ** -3  # tick is 10 milliseconds

        self.stopTimer = False

        self.currentTick = 0
        self.totalTicks = self.end / self.tick

        self.t = None

    def timer(self):
        counter = 0
        while not self.stopTimer:
            if(self.currentTick == self.totalTicks):
                if(counter == 9):
                    self.currentTick = -10
                    counter = 0
                else:
                    self.currentTick = 0
                    counter += 1
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
