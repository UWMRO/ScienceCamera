#!/usr/bin/python2

import wx  # get wxPython
from astropy.io import fits
import numpy as np
import threading
import time
import os
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


def getLogString(command, prePost):
    """
    Pre: Takes in command that is either sent to or from the server.  Parses that command and constructs
         a string for reporting in any particular status box.  Must pass in as prePost whether the command
         is pre-server exectution or post server exection.
    Post: Returns a string that is used to report in a status box through the GUI, e.g. the log box in the
          log tab.  If string is not made then it returns None.
    """
    command = command.split(" ")
    if(prePost == 'pre'):  # command is split with by white space
        key = command[0]

        if(key == 'expose'):
            itime = float(command[3])
            return "Exposing for time %.2f sec" % itime
        if(key == 'real'):
            itime = float(command[3])
            return "Starting real time expsoures with %.2f sec" % itime
        if(key == 'series'):
            itime = float(command[3])
            number = int(command[2])
            return "Exposing for %d images with time %.2f sec" % (number, itime)
        if(key == 'setTEC'):
            temp = float(command[1])
            return "Setting temperature to %.1f C" % temp
        if(key == 'warmup'):
            return "Turning off cooler"
        if(key == 'abort'):
            return "Aborting current exposure..."
        if(key == 'filter'):
            key2 = command[1]
            if(key2 == 'home'):
                return "Starting homing sequence..."
            if(key2 == 'move'):
                filter = command[2]
                return "Moving to filter %s" % filter

    if(prePost == 'post'):  # command has a key then is followed by relavent information delimited with commas
        key = command[0]
        stats = command[1].split(",")
        print("Stats in log:", stats)
        if(key == 'status'):
            if(stats[0] == 20002):  # 20002 is "success" to Evora
                return "Camera already initialized connecting..."
            else:
                return "Camera uninitialized this will take a few..."
        if(key == 'expose'):
            # at the end of stats is the image name
            name = stats[-1]
            itime = float(stats[2])
            results = int(stats[0])
            if(results == 1):  # 1 for successful exposure
                return "\"%s\" completed with time %.2f sec" % (name, itime)
            else:
                return "\"%s\" failed to expose..." % name
        if(key == 'real'):
            results = stats[0]
            return "Real time exposure successfully done..."
        if(key == 'series'):
            results = stats[0]
            return "Done take series images..."
        if(key[:-1] == 'seriesSent'):
            name = stats[-1]
            itime = float(stats[1])
            return "\"%s\" completed with time %.2f sec" % (name, itime)
        if(key == 'connect'):
            if(stats[0] == 20002):  # 20002 is "success" Evora
                return "Initialization completed..."
            else:
                return "Initialization failed..."
        if(key == 'getTEC'):
            pass
        if(key == 'setTEC'):
            temp = float(stats[0])
            return "Successfully set cooler to %.1f C" % temp
        if(key == 'warmup'):
            return "Successfully warming up..."
        if(key == 'temp'):
            results = stats[0]  # 1 for success 0 for failure
            if(results == 1):
                return "Successfully shutdown cooler..."
            else:
                return "Failure in setting cooler down..."
        if(key == 'shutdown'):
            results = stats[0]
            return "Successfully shutdown camera..."
        if(key == 'abort'):
            results = stats[0]
            return "Successfully aborted exposure..."
        if(key == 'filter'):
            key2 = command[1]
            stats = command[2].split(",")
            if(key2 == 'home'):
                if(int(stats[0]) == 1):
                    return "Successfully homed..."
                else:
                    return "Failed to home, try again..."
            if(key2 == 'move'):
                if(int(stats[0]) == 1):
                    return "Successfully moving filter give it a moment..."
                else:
                    return "Failed to move filter..."

    return None
def timeStamp():
    """
    Pre: No arguments are needed to invoke this method.
    Post: Returns a string with the current date and time.
    """
    time = datetime.today()
    #stamp = "[%s/%s/%s, " % (time.month, time.day, time.year)
    stamp = "[%s:%s:%s]" % (time.hour, time.minute, time.second)
    return stamp


def checkForFile(path):
    boolean = os.path.isfile(path)
    return boolean


def getImagePath():
    """
    Pre: No inputs.
    Post: Returns the file path /data/forTCC/ plus an image name with a time stamp
          with accuracy of milliseconds.
    """
    time = datetime.today()
    fileName = "image_%s%s%s_%s%s%s_%s.fits" % (time.year, time.month, time.day, time.hour, time.minute, time.second, time.microsecond)
    return "/data/forTCC/" + fileName


def checkForImageCounter(name):
    """
    Note: This method is only ever entered if there actually is a name as well as there will never
    be a .fits at the end.
    Pre: Takes in an image name as a string and sees if the standard iterator is on the end of the image
    name.
    Post: Returns a boolean of whether the standard iterator is on the end of the image name.  That
              standard format follows like *_XXX.fits where XXX goes from 001 an up.
    """
    if("_" in name):
        name.split("_")
        if(isInt(name[-1])):
            return True
        else:
            return False
    else:
        return False


def iterateImageCounter(name):
    """
    Note: This method is only invoked if the current image name has been checked to have a counter.
    Pre: Takes in an image name with a counter.
    Post: Gets the counter and iterates it, and then edits self.currentImage to have an iterated count string
          in the standard format.
    """
    temp = name.split('_')
    count = int(temp[-1])
    print(count)
    count += 1
    if(count < 10):
        temp[-1] = "00" + str(count)
    elif(count < 100):
        temp[-1] = "0" + str(count)
    else:
        temp[-1] = str(count)
    name = "_".join(temp[:])
    print("Iterated to: " + name)
    return name


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
