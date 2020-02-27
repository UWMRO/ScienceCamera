#!/usr/bin/python2
from __future__ import print_function, division

# Imports
# Core Imports
import threading
import time
import shutil
from io import BytesIO
import my_logger

# Third-party imports
import wx
from twisted.internet import protocol

__author__ = "Tristan J. Hillis"

"""
Comment on documentation:
When reading the doc strings if "Pre:" is present then this stands for "precondition", or the conditions in order
to invoke something.  Oppositely, "Post:" stands for "postcondition" and states what is returned by the method.

File Description: This file contains a set of functions that the GUI or server code calls throughout.
"""


# Deprecated
logger = my_logger.myLogger("gui_elements.py", "client")
# Get gregorian date, local
# d = date.today()
# logFile = open("/home/mro/ScienceCamera/gui/logs/log_gui_" + d.strftime("%Y%m%d") + ".log", "a")


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
    if orientation == wx.HORIZONTAL:
        boxsizer.Add((pixelSpacing, 0))
    elif orientation == wx.VERTICAL:
        boxsizer.Add((0, pixelSpacing))


def SetButtonColor(btn, fore, back):
    btn.SetForegroundColour(fore)
    btn.SetBackgroundColour(back)


class FileWriter(protocol.Protocol):

    def __init__(self, directory, fileName):
        """
        Pass full directory in for the file to be saved with just the fileName
        """
        self.f = open(directory+fileName, 'wb')

    def dataReceived(self, data):
        # print("Byte size", len(data))
        self.f.write(data)

    def connectionLost(self, reason):
        print("Writing closed and done")
        self.f.close()


class FileBuffer(protocol.Protocol):
    def __init__(self, directory, fileName):
        """
        Pass full directory in for the file to be saved with just the fileName
        """
        self.time = 0 - time.clock()
        self.fileName = directory+fileName
        self.buffer = BytesIO()

    def dataReceived(self, data):
        # print("Byte size", len(data))
        self.buffer.write(data)

    def connectionLost(self, reason):
        print("Writing closed and done")
        # save buffer
        self.buffer.seek(0)
        with open(self.fileName, 'wb') as f:
            shutil.copyfileobj(self.buffer, f, length=131072)

        self.time += time.clock()
        print("TIME TO GET:", self.time)


# Deprecated code
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
