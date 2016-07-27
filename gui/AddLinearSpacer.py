#!/usr/bin/python2

# Comment on documentation:
# When reading the doc strings if "Pre:" is present then this stands for "precondition", or the conditions in order to invoke something.
# Oppositely, "Post:" stands for "postcondition" and states what is returned by the method.

__author__ = "Tristan J. Hillis"

## Imports
import wx  # get wxPython
from astropy.io import fits
import numpy as np
import threading
import time
import os
from datetime import datetime
from datetime import date
import sys

## Global Variables

# Get gregorian date, local
d = date.today()
logFile = open("/home/mro/ScienceCamera/gui/logs/log_gui_" + d.strftime("%Y%m%d") + ".log", "a")


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
            if(key2 == 'getFilter'):
                return "Getting filter position..."
            if(key2 == 'connect'):
                return "Please home filter..."

    if(prePost == 'post'):  # command has a key then is followed by relavent information delimited with commas
        key = command[0]
        print(printStamp() + "key from post:", key)
        stats = command[1].split(",")
        print(printStamp() + "Stats in log:", stats)
        if(key == 'status'):
            if(int(stats[0]) == 20002):  # 20002 is "success" to Evora
                return "Camera already initialized connecting..."
            elif(int(stats[0]) == 20075):
                return "Camera uninitialized this will take a few..."
            else:
                return "Camera drivers reporting incorrectly please run reinstall..."
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
        if(key == 'seriesSent'):            
            name = stats[-1]
            itime = float(stats[1])
            return "\"%s\" completed with time %.2f sec" % (name, itime)
        if(key == 'connect'):
            if(int(stats[0]) == 20002):  # 20002 is "success" Evora
                return "Initialization completed..."
            else:
                return "Initialization failed..."
        if(key == 'connectLost'):
            return "Disconnected from camera normally..."
        if(key == 'connectFailed'):
            return "Disconnected from camera suddenly..."
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
        if(key == 'startup'):
            if int(stats[0]) == 20002:
                return "Camera initialization successful..."
            else:
                return "Camera initialization went wrong check the server..."
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
                if(bool(stats[0]) == True):
                    return "Successfully moved filter..."
                else:
                    return "Failed to move filter..."
            if(key2 == 'findPos'):
                return "Adjusting fitler this can take awhile..."
            if(key2 == 'getFilter'):
                key3 = command[2]
                stats = command[3].split(",")
                if(key3 == 'report'):
                    filter = stats[0]
                    return "At filter %s" % filter
                if(key3 == 'finding'):
                    filter = stats[0]
                    pos = int(stats[1])
                    return "Filter settleing in on position %d, or filter %s..." % (pos, filter)
                else:
                    filter = stats[0]
                    pos = int(stats[1])
                    return "At position %d, setting filter to %s..." % (pos, filter)
            if(key2 == 'connectLost'):
                return "Connection to filter lost normally..."
            if(key2 == 'connectFailed'):
                return "Connection to filter failed suddenly..."
    return None


def timeStamp():
    """
    Pre: No arguments are needed to invoke this method.
    Post: Returns a string with the current date and time.
    """
    time = datetime.today()
    #stamp = "[%s/%s/%s, " % (time.month, time.day, time.year)
    hour = ""
    minute = ""
    second = ""
    if(time.hour < 10):
        hour += "0" + str(time.hour)
    else:
        hour += str(time.hour)
    if(time.minute < 10):
        minute += "0" + str(time.minute)
    else:
        minute += str(time.minute)
    if(time.second < 10):
        second += "0" + str(time.second)
    else:
        second += str(time.second)
    stamp = "[%s:%s:%s]" % (hour, minute, second)
    return stamp


def checkForFile(path):
    """
    Pre: User specifies a path to a file.
    Post: This method will chekc if the specified file exists and return a boolean.
    """
    boolean = os.path.isfile(path)
    return boolean


def getImagePath(type):
    """
    Pre: No inputs.
    Post: Returns the file path /data/forTCC/ plus an image name with a time stamp
          with accuracy of milliseconds.
    """
    saveDirectory = "/home/mro/data/evora_server/raw/"
    time = datetime.today()
    fileName = "image_%s%s%s_%s%s%s_%s.fits" % (time.year, time.month, time.day, time.hour, time.minute, time.second, time.microsecond)
    if(type == 'real'):
        return "/tmp/" + fileName
    else:
        return saveDirectory + fileName


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
    print(printStamp() + str(count))
    count += 1
    if(count < 10):
        temp[-1] = "00" + str(count)
    elif(count < 100):
        temp[-1] = "0" + str(count)
    else:
        temp[-1] = str(count)
    name = "_".join(temp[:])
    print(printStamp() + "Iterated to: " + name)
    return name

def printStamp():
    """
    Pre: User needs nothing to pass in.
    Post: Returns a string catalogging the date and time in the format of [month day year, 24hour:minute:seconds]
    """
    day = datetime.today()
    string = day.strftime("[%b %m, %y, %H:%M:%S]")
    return string + " "

class Logger(object):
    """
    This class when assigned to sys.stdout or sys.stderr it will write to a file that is opened everytime a new GUI session is started.
    It also writes to the terminal window.
    """
    def __init__(self, stream):
        self.terminal = stream

    def write(self, message):
        self.terminal.flush()
        self.terminal.write(message)
        logFile.write(message)

    def stamp(self):
        d = datetime.today()
        string = d.strftime("[%b %m, %y, %H:%M:%S]")
        return string


class SampleTimer(object):
    """
    This is a timer object that can be used to sample the time off of a certain time length.
    """
    def __init__(self, timeLength):
        """
        Pre: User passes in a time length in seconds as "timeLength".
        Post: Initializes the timer object.
        """
        self.end = timeLength
        self.tick = 10 * 10 ** -3  # tick is 10 milliseconds

        self.stopTimer = False

        self.currentTick = 0
        self.totalTicks = self.end / self.tick

        self.t = None

    def _timer(self):
        """
        Note: User does not call this method.
        This method keeps count on the time.
        """
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
        """
        Pre: No user input.
        Post: Returns the current tick out of the total amount over the specified time length.
        """
        return [self.currentTick, self.totalTicks]

    def stop(self):
        """
        Pre: No user input.
        Post: Stops the timer object when called by the user.
        """
        self.stopTimer = True
        self.t.join(0)

    def start(self):
        """
        Pre: No user input.
        Post: When called by the user this will start the timer object.
        """
        self.stopTimer = False
        self.currentTick = 1
        # Start new thread to avoid blocking in its application.
        self.t = threading.Thread(target=self._timer, args=())
        self.t.daemon = True
        self.t.start()
