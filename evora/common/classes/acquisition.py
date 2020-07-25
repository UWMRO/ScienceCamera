#!/usr/bin/python2
from __future__ import absolute_import, division, print_function

import threading
# Imports
import time

# allows widgets to be inserted into wxPython status bar probably won't work on wxPython 3.x
import gui_elements as gui  # get useful methods
import pandas as pd
import thread
import wx  # get wxPython
from Queue import Queue

import evora.common.logging.my_logger as my_logger
import evora.common.utils.fits as fits_utils
import evora.common.utils.logs as log_utils

__author__ = "Tristan J. Hillis"

# Comment on documentation:
# When reading the doc strings if "Pre:" is present then this stands for "precondition", or the conditions in order to invoke something.
# Oppositely, "Post:" stands for "postcondition" and states what is returned by the method.

"""
This set of classes handles everything in the imaging tab.
"""

# Global Variables
logger = my_logger.myLogger("acquisitionClasses.py", "client")


class EventQueue(Queue, object):
    def __init__(self, event):
        super(EventQueue, self).__init__()
        self.event = event

    def addItem(self, item):
        self.put(item)
        self.event.set()
        self.event.clear()


# Thread Image Queue Watcher
class ImageQueueWatcher(threading.Thread, object):
    """
    This class will watch the image queue in the class Exposure and retrieve the image files via
    the ftp server as they come into the Queue.  This makes it so the ftp is not saturated by requests.
    """
    def __init__(self, exposeClass):
        threading.Thread.__init__(self)
        self.exposeClass = exposeClass

    def run(self):
        while True:
            if self.exposeClass.imageQueue.qsize() == 0:
                self.exposeClass.imageAddedEvent.wait()
                pass
            while self.exposeClass.imageQueue.qsize() > 0:
                line = str(self.exposeClass.imageQueue.get()).split(";")
                # image_path = line[0]
                image_name = line[1]
                image_type = line[2]
                logString = line[3]
                if logString == "None":
                    logString = None

                if image_type != 'real':
                    self.exposeClass.ftpLayer.sendCommand("get %s %s %s %s" % (image_name, self.exposeClass.saveDir,
                                                                               self.exposeClass.currentImage + ".fits",
                                                                               image_type)).addCallback(self.transferCallback, logString=logString)
                else:
                    self.exposeClass.ftpLayer.sendCommand("get %s %s %s %s" %
                                                          (image_name, "/tmp/", image_name, image_type)) \
                        .addCallback(self.transferCallback, logString=logString)
                time.sleep(0.01)

    def transferCallback(self, msg, logString):
        self.exposeClass.display(msg, logString)


class ProgressTimer(object):
    """
    Synopsis
    --------
    This class abstracts away a threading.Timer object with updating a wxpython progress bar (wx.Gauge).

    IMPORTANT: Any method not run by the main thread should ONLY ever update the wx.Gauge with wx.CallAfter.
    """

    def __init__(self, exposureClass):
        self.timer = None

        self.exposureClass = exposureClass
        self.gauge = None

        self.interval = 0  # holds the time interval, in milliseconds

    def start(self, exposureTime):
        """ Pass an image exposure time, add a hard-coded readout time, and start the time with the
        total exposure time.  The wx.Gauge will need to be primed.

        Parameters
        ----------
        exposureTime : float
                       This is the time of the image exposure in seconds.

        Return
        ------
        None
        """
        if self.gauge is None:
            self.gauge = self.exposureClass.parent.parent.parent.expGauge
        exposureTime = float(exposureTime) + self._getReadoutTime()

        # Determine how fast timer should be.
        integer_ticks = 0
        if time == 0:
            integer_ticks = 1
            self.interval = 300
        elif time <= 0.5:  # 10 millisecond intervals
            integer_ticks = int(exposureTime / 10**-2)  # divide by 10 milliseconds
            self.interval = 10
        elif time <= 10:  # 50 millisecond intervals
            integer_ticks = int(exposureTime / (8 * 10**-2))
            self.interval = 80
        else:  # Any time greater than 10 seconds have 100 millisecond intervals
            integer_ticks = int(exposureTime / 10**-1)
            self.interval = 100
        self.gauge.SetRange(integer_ticks)

        # pass the time in and start
        self.timer = threading.Timer(self.interval / 10**3, self.update)
        if integer_ticks > 0:
            wx.CallAfter(self.gauge.SetValue, 1)  # do first tick
        self.timer.start()

        return None

    def stop(self):
        """ Stop the timer and reset the wx.Gauge to the beginning.

        Parameters
        ----------
        None

        Return
        ------
        None
        """
        self.timer.cancel()
        wx.CallAfter(self.gauge.SetValue, 0)

        return None

    def update(self):
        """ Update the wx.Gauge's value and do so with wx.CallAfter to be thread safe.

        Parameters
        ----------
        None

        Return
        ------
        None
        """
        # Update gauge with value until it hits max-1
        max = self.gauge.GetRange()
        current = self.gauge.GetValue()

        if current < max and max > 2:
            wx.CallAfter(self.gauge.SetValue, current + 1)
        else:  # do nothing when we reach the end
            self.gauge.Pulse()

        self.timer = threading.Timer(self.interval / 10**3, self.update)
        self.timer.start()

        return None

    def _getReadoutTime(self):
        """
        Reads the binning type and the readout speed to determine the overall
        readout time.
        """
        exposeType = self.exposureClass.parent.typeInstance.exposeType.GetStringSelection()
        times_2x2 = [0.14, 0.23, 0.42, 6.06]  # exposure times in seconds
        times_1x1 = [0.302, 0.61, 1.51, 23.0]
        times = None

        binning = self.exposureClass.parent.parent.parent.binning  # string (1 : 1x1, 2 : 2x2)
        if binning == '1':
            times = times_1x1
        else:
            times = times_2x2

        readout_speed = None
        if exposeType == "Real Time":
            readout_speed = 1
        else:
            readout_speed = self.exposureClass.parent.parent.parent.readoutIndex  # (0 : 5.0 MHz, 1 : 3.0 MHz, 2 : 1.0 MHz, 3 : 0.05 MHz)

        return times[readout_speed]


# Class that handles widgets related to exposure
class Exposure(wx.Panel):
    """
    Creates the group of widgets that handle related exposure controls
    """
    def __init__(self, parent):
        """
        Initializes the whole GUI.
        """
        wx.Panel.__init__(self, parent)

        self.protocol = None  # gives access to the Evora client protocol
        self.ftp = None  # Gives access to FTP client protocol
        self.ftpLayer = None
        self.parent = parent  # gives access to the higher classes

        self.saveDir = "/home/mro/data/"  # Default directory to save images to.

        self.abort = False  # tells you if the abort button is active (i.e. True if you can abort and False if not)
        self.seriesImageNumber = None  # initialize a series image number
        self.currentImage = None  # initializes to keep track of the current image name class wide
        self.logFunction = None  # keeps an instance of the function that will be used to log the status

        self.realSentCount = 0

        self.timer = ProgressTimer(self)

        # Main sizers
        self.vertSizer = wx.BoxSizer(wx.VERTICAL)
        self.horzSizer = wx.BoxSizer(wx.HORIZONTAL)

        # Additional sub sizers
        self.exposeSizer = wx.BoxSizer(wx.HORIZONTAL)  # used for spacing expTime and expValue
        self.buttonSizer = wx.BoxSizer(wx.HORIZONTAL)  # used for spacing expose and stop buttons
        self.nameSizer = wx.BoxSizer(wx.VERTICAL)  # use for spacing name text and text ctrl

        # Widgets
        self.expTime = wx.StaticText(self, id=2000, label="Exposure Time (s)")
        self.name = wx.StaticText(self, id=2001, label="Save Name")
        self.nameField = wx.TextCtrl(self, id=2002, size=(200, -1))

        self.expValue = wx.TextCtrl(self, id=2003, size=(50, -1), value="0", style=wx.TE_READONLY)

        self.expButton = wx.Button(self, id=2004, label="Expose", size=(80, -1))
        self.stopExp = wx.Button(self, id=2005, label="Abort", size=(75, -1))
        self.setDirButton = wx.Button(self, id=2006, label="Set Dir.", size=(75, -1))
        self.stopExp.Enable(False)

        self.expBox = wx.StaticBox(self, id=2006, label="Exposure Controls", size=(200, 100), style=wx.ALIGN_CENTER)
        self.expBoxSizer = wx.StaticBoxSizer(self.expBox, wx.VERTICAL)

        # Line up smaller sub sizers
        gui.AddLinearSpacer(self.exposeSizer, 15)
        self.exposeSizer.Add(self.expTime, flag=wx.ALIGN_CENTER)
        gui.AddLinearSpacer(self.exposeSizer, 15)
        self.exposeSizer.Add(self.expValue, flag=wx.ALIGN_CENTER)
        gui.AddLinearSpacer(self.exposeSizer, 15)

        self.buttonSizer.Add(self.setDirButton, flag=wx.ALIGN_CENTER)
        gui.AddLinearSpacer(self.buttonSizer, 10)
        self.buttonSizer.Add(self.expButton, flag=wx.ALIGN_CENTER)
        gui.AddLinearSpacer(self.buttonSizer, 10)
        self.buttonSizer.Add(self.stopExp, flag=wx.ALIGN_CENTER)

        self.nameSizer.Add(self.name, flag=wx.ALIGN_CENTER)
        gui.AddLinearSpacer(self.nameSizer, 8)
        self.nameSizer.Add(self.nameField, flag=wx.ALIGN_CENTER)

        # Line up larger chuncks with main sizer
        gui.AddLinearSpacer(self.expBoxSizer, 10)
        self.expBoxSizer.Add(self.nameSizer, flag=wx.ALIGN_CENTER)
        gui.AddLinearSpacer(self.expBoxSizer, 5)
        self.expBoxSizer.Add(self.exposeSizer, flag=wx.ALIGN_CENTER)
        gui.AddLinearSpacer(self.expBoxSizer, 5)
        self.expBoxSizer.Add(self.buttonSizer, flag=wx.ALIGN_CENTER)
        gui.AddLinearSpacer(self.expBoxSizer, 5)

        self.vertSizer.Add(self.expBoxSizer, flag=wx.ALIGN_CENTER)

        # Global variables
        self.timeToSend = 0  # Tracks the time that will be sent to the camera
        self.nameToSend = ""  # tracks the name to send

        # Bindings
        self.Bind(wx.EVT_TEXT, self.nameText, id=2002)  # bind self.nameField
        self.Bind(wx.EVT_TEXT, self.onExpTime, id=2003)  # bind self.expValue
        self.Bind(wx.EVT_BUTTON, self.onExpose, id=2004)  # bind self.expButton
        self.Bind(wx.EVT_BUTTON, self.onStop, id=2005)  # bind self.stopExp
        self.Bind(wx.EVT_BUTTON, self.onSetDir, id=2006)  # bind self.setDirButton

        self.SetSizer(self.vertSizer)
        self.vertSizer.Fit(self)

        # Setup work for Image Queue
        self.imageAddedEvent = threading.Event()
        self.imageQueue = EventQueue(self.imageAddedEvent)
        self.imageThread = ImageQueueWatcher(self)
        self.imageThread.daemon = True
        self.imageThread.start()

    def nameText(self, event):
        """
        Executes on the event that anything new is type into the name text box and sets it to
        the global variable self.nameToSend for sending to Evora.
        """
        if " " in self.nameField.GetValue():
            self.nameField.SetValue(self.nameField.GetValue().replace(" ", "_"))
        self.nameToSend = self.nameField.GetValue()
        self.expButton.SetDefault()

    def onExpTime(self, event):
        """
        Executes when there is a new string typed into the exposure time field.  It then
        passes it to the global variable self.timeToSend for sending to Evora.
        """
        self.timeToSend = self.expValue.GetValue()
        self.expButton.SetDefault()

    def onExpose(self, event):
        """
        Executes when the expose button is pressed. It checks that the variable
        self.exposeToSend is a float. It it passes then this value is sent to Evora.  If it
        fails a dialog box tells the user the varible is not a number and will not send it
        to Evora.
        """
        lessThanZero = True
        if self.timeToSend.isnumeric():
            if float(self.timeToSend) < 0:
                dialog = wx.MessageDialog(None, "Exposure time can not be less than 0...will not expose", "", wx.OK | wx.ICON_ERROR)
                dialog.ShowModal()
                dialog.Destroy()
                lessThanZero = False

        else:
            dialog = wx.MessageDialog(None, "Exposure time not a number...will not expose.",
                                      "", wx.OK | wx.ICON_ERROR)
            dialog.ShowModal()
            dialog.Destroy()

        if str(self.nameToSend) == "":
            dialog = wx.MessageDialog(None, "No name was given...will not expose", "",
                                      wx.OK | wx.ICON_ERROR)
            dialog.ShowModal()
            dialog.Destroy()
        else:
            pass

        # if statement here is more for redundancy.  The above MessageDialogs let the user their input is incorrect,
        # else they will enter this if statement just fine.
        if self.timeToSend.isnumeric() and self.nameToSend != "" and lessThanZero:

            line = self.getAttributesToSend().split()

            # Set the correct log function that only prints to the log tab
            self.logFunction = self.logExposure

            # get image type
            imType = int(line[0])
            itime = float(line[3])

            if imType == 1:  # single exposure
                line = " ".join(line[1:])  # bring all the parameters together
                overwrite = None

                if fits_utils.check_for_file(self.saveDir + self.currentImage + ".fits"):
                    dialog = wx.MessageDialog(None, "File already exists do you want to overwrite?", "", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
                    overwrite = dialog.ShowModal()
                    dialog.Destroy()

                if overwrite is None or overwrite == wx.ID_OK:
                    self.expButton.Enable(False)
                    self.stopExp.Enable(True)
                    self.abort = True
                    command = "expose " + line
                    logString = log_utils.get_log_str(command, 'pre')
                    self.log(self.logFunction, logString)

                    d = self.protocol.sendCommand(command)
                    d.addCallback(self.exposeCallback)
                    self.timer.start(itime)

            if imType == 2:  # real time exposure
                self.expButton.Enable(False)
                self.stopExp.Enable(True)
                self.abort = True
                line = " ".join(line[1:])

                # start callback that looks for a path leading to a real image
                d = self.protocol.addDeferred("realSent")
                d.addCallback(self.displayRealImage)

                command = "real " + line
                logString = log_utils.get_log_str(command, 'pre')
                self.log(self.logFunction, logString)

                self.ftpLayer.sendCommand("cwd tmp/").addCallback(self.startRealTime, command=command, itime=itime)

            if imType == 3:  # series exposure
                dialog = wx.TextEntryDialog(None, "How many exposure?", "Entry", "1", wx.OK | wx.CANCEL)
                answer = dialog.ShowModal()
                dialog.Destroy()

                if answer == wx.ID_OK:
                    self.seriesImageNumber = dialog.GetValue()

                    if self.seriesImageNumber.isdigit():
                        logger.debug("Number of image to be taken: " + str(int(self.seriesImageNumber)))
                        line[2] = self.seriesImageNumber
                        line = " ".join(line[1:])  # join as line to send to server

                        # check for overwrite
                        overwrite = None
                        if (self.checkForImageCounter(self.currentImage) and fits_utils.check_for_file(self.saveDir + self.currentImage + ".fits"))\
                                or (not self.checkForImageCounter(self.currentImage) and fits_utils.check_for_file(self.saveDir + self.currentImage + "_001.fits")):

                            dialog = wx.MessageDialog(None, "File already exists do you want to overwrite?", "", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
                            overwrite = dialog.ShowModal()
                            dialog.Destroy()

                        if overwrite is None or overwrite == wx.ID_OK:  # Overwrite existing file
                            self.expButton.Enable(False)
                            self.stopExp.Enable(True)
                            self.abort = True

                            # set up all callbacks for series
                            for i in range(int(self.seriesImageNumber)):
                                d = self.protocol.addDeferred("seriesSent" + str(i + 1))
                                d.addCallback(self.displaySeriesImage)

                            command = "series " + str(line)
                            logString = log_utils.get_log_str(command, 'pre')
                            self.log(self.logFunction, logString)

                            d = self.protocol.sendCommand(command)
                            d.addCallback(self.seriesCallback)

                            # start timer
                            if self.timer._getReadoutTime() + itime > 1.0:
                                self.timer.start(itime)
                            else:
                                self.timer.start(0)

                    else:
                        dialog = wx.MessageDialog(None, "Entry was not a valid integer!", "", wx.OK | wx.ICON_ERROR)
                        dialog.ShowModal()
                        dialog.Destroy()

    def startRealTime(self, msg, command, itime):
        # send command to start realtime exposure
        d = self.protocol.sendCommand(command)
        d.addCallback(self.realCallback)  # this will clear the image path queue

        # start timer
        if itime < 2.5:
            self.timer.start(0)
        else:
            self.timer.start(itime)

    def exposeCallback(self, msg):
        """
        Called when the client recieves the "expose" keyword from the server indicating the exposure is complete.
        Stops exposure gauge and resets it, disables the stop button and re-enables the exposure button,
        and if the image was successfully taken then it plots it.
        """
        # May need to thread to a different method if to slow
        results = msg.split(",")

        # immediatly reset button
        self.abort = False
        self.expButton.Enable(True)

        if self.stopExp.IsEnabled():
            self.stopExp.Enable(False)

        # complete progress bar for image acquisition
        # check to see if timer is still going and stop it (callback might come in early)
        self.timer.stop()

        # get success;
        success = int(results[0])  # 1 for true 0 for false

        logger.debug(str(self.parent.parent.parent.imageOpen))
        logger.info("opened window from exposeCallback method")

        if success == 1:
            # get name of image and path
            filePath = results[1].split("/")
            name = filePath[-1].rstrip()
            path = ""
            for i in filePath[:-1]:
                path += i + "/"

            # get time sent to server
            # time = float(results[2])

            logger.debug(path + name)

            # log the status
            self.logFunction = self.logExposure
            logString = log_utils.get_log_str("expose " + msg + "," + self.currentImage, 'post')

            line = "%s;%s;single;%s" % (path, name, logString)
            self.imageQueue.addItem(line)

        else:
            logger.info("Successfully Aborted")

    def display(self, savedImage, logString):
        data = fits_utils.getdata(savedImage)
        stats_list = fits_utils.calcstats(data)

        imageName = None
        if "/tmp/" not in savedImage:
            imageName = savedImage.split("/")[-1]

        # change the gui with thread safety
        # plots the image
        wx.CallAfter(self.safePlot, data, stats_list, imageName)

        if logString is not None:
            self.log(self.logFunction, logString)

    def safePlot(self, data, stats_list, imageName):
        """
        Used in conjunction with wx.CallAfter to update the embedded Matplotlib in the image window.
        If the image window is closed it will open it and then plot, otherwise it is simply plotted.
        """
        if not self.parent.parent.parent.imageOpen:  # Open image window if closed.
            # create new window
            self.parent.parent.parent.openImage("manual open")

        else:  # If image window open then clear the axis of the previous image
            self.parent.parent.parent.window.panel.clear()

        plotInstance = self.parent.parent.parent.window
        sliderVal = plotInstance.currSliderValue / 10

        plotInstance.panel.updatePassedStats(stats_list)
        plotInstance.panel.plotImage(data, sliderVal, plotInstance.currMap)
        plotInstance.panel.updateScreenStats(imageName)
        plotInstance.panel.refresh()

    def displayRealImage(self, msg):
        """
        Called when client recieves that there is an image to be displayed from real time series.
        """
        path = msg

        # no abort then display the image
        if self.abort:  # means that abort can be called.
            # add a new deffered object to set up for another incoming image
            d = self.protocol.addDeferred("realSent")
            d.addCallback(self.displayRealImage)

            # get stats
            path = path.split("/")
            name = path[-1]
            path = "/".join(path[:-1]) + "/"

            line = "%s;%s;real;%s" % (path, name, str(None))
            self.imageQueue.addItem(line)

            if float(self.timeToSend) >= 2.5:
                self.timer.stop()
                self.timer.start(self.timeToSend)

    def realCallback(self, msg):
        """
        Called when the camera has been aborted during a real time series exposure.
        """
        self.protocol.removeDeferred("realSent")  # Remove floating deffered object

        # release ImageQueueWatcher if it is stuck waiting for an image to display and empty Queue
        self.imageQueue.empty()

        self.timer.stop()

        self.logFunction = self.logExposure
        logString = log_utils.get_log_str("real " + msg, 'post')
        self.log(self.logFunction, logString)

        logger.debug("Completed real time series with exit: " + msg)

        d = self.ftpLayer.sendCommand("cdup")
        d.addCallback(self.done)

    def done(self, msg):
        print(msg)

    def displaySeriesImage_thread(self, msg):
        """
        Executes displaySeriesImage in anther thread when the callback is executed via the main thread.
        """
        logger.debug("From series image callback thread: " + repr(msg))
        msg = msg.rstrip()
        thread.start_new_thread(self.displaySeriesImage, (msg,))

    def displaySeriesImage(self, msg):
        """
        Called when the server sends that an image is ready to display.
        """
        print("ENTERED DISPLAY SERIES IMAGE", msg)
        msg = msg.split(",")

        imNum = int(msg[0])
        logger.debug(str(type(imNum)))
        time = float(msg[1])
        path = msg[2]

        fullPath = path.split("/")
        name = fullPath[-1].rstrip()
        directory = ""
        for i in fullPath[:-1]:
            directory += i + "/"
        # self.timer_2.stop()
        # no abort then display the image
        if imNum <= int(self.seriesImageNumber):
            logger.info("Entered to display series image")

            # copy image over (counter looks like "_XXX.fits")
            logger.debug("current image name: " + self.currentImage)
            logger.debug(str(self.checkForImageCounter(self.currentImage)))

            if not self.checkForImageCounter(self.currentImage):
                self.currentImage += "_001"
                logger.debug("entered")

            else:
                if imNum > 1:
                    self.iterateImageCounter(self.currentImage)

            self.logFunction = self.logExposure
            dataMsg = ",".join(msg)
            logString = log_utils.get_log_str("seriesSent " + dataMsg + "," + self.currentImage, 'post')

            line = "%s;%s;series;%s" % (path, name, logString)
            self.imageQueue.addItem(line)

            if self.seriesImageNumber is not None:
                print("MAKES IT THIS FAR")
                if imNum < int(self.seriesImageNumber):
                    print("KEEP GOING")
                    if time + self.timer._getReadoutTime() >= 1.0:
                        print("MADE IT")
                        self.timer.stop()
                        self.timer.start(time)

    def seriesCallback(self, msg):
        msg = msg.split(",")
        exitNumber = int(msg[1])  # server will send which count the series loop ended on
        if exitNumber <= int(self.seriesImageNumber):
            for i in range(exitNumber, int(self.seriesImageNumber) + 1):
                key = "seriesSent" + str(i)
                self.protocol.removeDeferred(key)

        # reset series image number
        logger.debug(str(self.protocol._deferreds))

        self.abort = False
        self.expButton.Enable(True)
        if self.stopExp.IsEnabled():
            self.stopExp.Enable(False)

        self.timer.stop()
        self.imageQueue.empty()

        dataMsg = ",".join(msg)
        self.logFunction = self.logExposure
        logString = log_utils.get_log_str("series " + dataMsg, 'post')
        self.log(self.logFunction, logString)
        logger.debug("Completed real time series with exit: " + str(msg))

    def abort_callback(self, msg):
        # self.parent.parent.parent.expGauge.SetValue(0)  # redundancy to clear the exposure gauge
        self.logFunction = self.logExposure
        logString = log_utils.get_log_str("abort " + msg, 'post')
        self.log(self.logFunction, logString)
        logger.debug("Aborted " + msg)

    def getAttributesToSend(self):
        """
        Method that will gather part of the command line to send to the server for exposing.
        """
        # get binning type
        binning = self.parent.parent.parent.binning
        readoutIndex = self.parent.parent.parent.readoutIndex

        # get exposure type
        exposeType = self.parent.typeInstance.exposeType.GetStringSelection()
        # print exposeType
        if exposeType == "Single":
            exposeType = 1
        if exposeType == "Real Time":
            exposeType = 2
        if exposeType == "Series":
            exposeType = 3

        # get image type
        imageType = self.parent.typeInstance.imageType.GetStringSelection()

        expNum = 1

        filterInstance = self.parent.filterInstance
        filter = str(filterInstance.filterSelection)
        logger.debug("from attributes filter is: " + filter)

        # set the global current image name
        self.currentImage = self.nameToSend

        # line = "expose" # this is given before the command is sent off
        line = str(exposeType)
        line += " " + str(imageType).lower()
        line += " " + str(expNum)  # This is the exposure number.  Should have dialog come up for when set to series to take in the number of exposures
        line += " " + str(self.timeToSend)
        line += " " + str(binning)
        line += " " + str(readoutIndex)
        line += " " + filter
        return line

    def logExposure(self, logmsg):
        """
        Controls the visible logging in the GUI for the imaging tab.
        """
        logger.info("logging from exposure class")
        logInstance = self.parent.parent.parent.log.logInstance
        wx.CallAfter(logInstance.threadSafeLogStatus, logmsg)

    def log(self, logfunc, logmsg):
        """
        Pre: Before an exposure is set the correct log function to call is set to self.logFunction.
        For example, setting self.logFunction to self.logScript will log on the scripting status
        and the log tab versus self.logExposure.  Also passed in is the logmsg that you want to
        print.
        Post: This method will run the logfunc to print the log message to the correct status
        boxes; it returns nothing.
        """
        logger.info("entered log")
        logfunc(logmsg)

    def checkForImageCounter(self, name):
        """
        Note: This method is only ever entered if there actually is a name as well as there will never
              be a .fits at the end.
        Pre: Takes in an image name as a string and sees if the standard iterator is on the end of the image
             name.
        Post: Returns a boolean of whether the standard iterator is on the end of the image name.  That
              standard format follows like *_XXX.fits where XXX goes from 001 an up.
        """
        if "_" in name:
            name = name.split("_")
            return len(name[-1]) >= 3 and (name[-1]).isdigit()
        else:
            return False

    def iterateImageCounter(self, name):
        """
        Note: This method is only invoked if the current image name has been checked to have a counter.
        Pre: Takes in an image name with a counter.
        Post: Gets the counter and iterates it, and then edits self.currentImage to have an iterated count string
              in the standard format.
        """
        temp = name.split('_')
        count = int(temp[-1])
        count += 1

        if count < 10:
            temp[-1] = "00" + str(count)
        elif count < 100:
            temp[-1] = "0" + str(count)
        else:
            temp[-1] = str(count)

        self.currentImage = "_".join(temp[:])
        logger.debug("Iterated to: " + self.currentImage)

    def onSetDir(self, event):
        """
        Called when set directory button is pressed.  Asks for a path to the directory for copying images to.
        If the dir. does not exist it will warn the user and ask them to make it rather than setting anything.
        If the dir. does exist then future images will be saved into it.
        """
        # dialog = wx.TextEntryDialog(None, "Point to new directory.  Currently set to %s" % self.saveDir,
        #                           "Set Save Directory", "%s" % self.saveDir, wx.OK | wx.CANCEL)
        dialog = wx.DirDialog(self, "Choose a save directory", defaultPath="/home/mro/data")
        answer = dialog.ShowModal()
        dialog.Destroy()

        if answer == wx.ID_OK:
            setTo = str(dialog.GetPath()) + "/"
            self.saveDir = setTo
            self.parent.saveDirectoryText.SetLabel(u"Saving \u2192 %s" % self.saveDir)
            self.parent.Layout()  # This recenters the static text
            logger.debug("Directory: " + self.saveDir)

    def onStop(self, event):
        """
        Executes when the stop button is pressed.  Sends a command to Evora to stop exposing.
        """
        self.logFunction = self.logExposure
        logString = log_utils.get_log_str("abort", 'pre')
        self.log(self.logFunction, logString)

        d = self.protocol.sendCommand("abort")
        d.addCallback(self.abort_callback)

        self.timer.stop()
        self.imageQueue.empty()

        self.expButton.Enable(True)
        self.stopExp.Enable(False)
        self.abort = False

        logger.info("Stop Exposure")


# Class that handles Radio boxes for image types and exposure types
class TypeSelection(wx.Panel):
    """
    Creates the panel that holds the image and exposure type selections.
    """
    def __init__(self, parent):
        """
        Initializes radio boxes that hold the different selections concerning with images and
        exposure.
        """
        wx.Panel.__init__(self, parent)

        # Global Variables
        self.parent = parent
        self.exposeClass = self.parent.exposureInstance  # give access to Exposure class variables
        self.tempTime = None
        self.tempName = None

        # Main Sizers
        self.vertSizer = wx.BoxSizer(wx.VERTICAL)
        self.horzSizer = wx.BoxSizer(wx.HORIZONTAL)

        # Additianl Sub Sizers
        self.radioSizer = wx.BoxSizer(wx.HORIZONTAL)

        # Widgets (specifially radio boxes)
        self.imageType = wx.RadioBox(self, id=2010, label="Image Type", size=wx.DefaultSize,
                                     choices=["Bias", "Flat", "Dark", "Object"], style=wx.RA_HORIZONTAL)
        self.exposeType = wx.RadioBox(self, id=2011, label="Exposure Type", size=wx.DefaultSize,
                                      choices=["Single", "Real Time", "Series"], style=wx.RA_HORIZONTAL)

        # Line up sub-chunks
        self.radioSizer.Add(self.imageType)
        gui.AddLinearSpacer(self.radioSizer, 50)
        self.radioSizer.Add(self.exposeType)

        # Line up big chuncks
        self.vertSizer.Add(self.radioSizer)

        # Bindings
        self.Bind(wx.EVT_RADIOBOX, self.onImageType, id=2010)
        self.Bind(wx.EVT_RADIOBOX, self.onExposeType, id=2011)

        self.SetSizer(self.vertSizer)
        self.vertSizer.Fit(self)

    def onImageType(self, event):
        """
        When a new image type is selected this will write that type to the header on the next
        image that is exposed.
        """
        index = self.imageType.GetSelection()

        if index == 0:
            self.tempTime = self.exposeClass.timeToSend
            self.exposeClass.expValue.SetWindowStyle(wx.TE_READONLY)
            self.exposeClass.expValue.SetValue("0")
        else:
            if self.exposeClass.timeToSend == "0" and self.tempTime is not None:
                self.exposeClass.timeToSend = self.tempTime

            self.exposeClass.expValue.SetWindowStyle(wx.TE_RICH)
            self.exposeClass.expValue.SetValue(str(self.exposeClass.timeToSend))

        logger.info(self.imageType.GetStringSelection())

    def onExposeType(self, event):
        """
        When a new exposure type is selected this will write that type to the header on the next
        image that is exposed.
        """
        index = self.exposeType.GetSelection()

        if index == 1:
            self.tempName = self.exposeClass.nameToSend  # store the user name that will be restored later
            self.exposeClass.nameField.SetWindowStyle(wx.TE_READONLY)
            self.exposeClass.nameField.SetValue("No name needed")

        else:
            if self.tempName is not None and self.exposeClass.nameToSend == "No name needed":
                self.exposeClass.nameToSend = self.tempName

            self.exposeClass.nameField.SetWindowStyle(wx.TE_RICH)
            self.exposeClass.nameField.SetValue(self.exposeClass.nameToSend)
        logger.info(self.exposeType.GetStringSelection())


class TempControl(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.protocol = None
        self.parent = parent
        self.isConnected = False
        self.logFunction = None
        self.currTemp = None
        self.prevMode = None
        self.current_mode = None

        # Main sizers
        self.vertSizer = wx.BoxSizer(wx.VERTICAL)
        self.horzSizer = wx.BoxSizer(wx.HORIZONTAL)

        # Additional sub sizers
        self.tempSizer = wx.BoxSizer(wx.HORIZONTAL)  # used for spacing tempText and tempValue
        self.buttonSizer = wx.BoxSizer(wx.HORIZONTAL)  # used for spacing expose and stop buttons

        # Widgets
        self.tempText = wx.StaticText(self, id=2030, label="Temperature (C)")
        self.tempValue = wx.TextCtrl(self, id=2031, size=(45, -1), style=wx.TE_PROCESS_ENTER)
        self.tempButton = wx.Button(self, id=2032, label="Cool", size=(60, -1))
        self.stopCool = wx.Button(self, id=2033, label="Stop", size=(60, -1))
        self.stopCool.Enable(False)
        self.tempBox = wx.StaticBox(self, id=2034, label="Temperature Controls", size=(100, 100), style=wx.ALIGN_CENTER)
        self.tempBoxSizer = wx.StaticBoxSizer(self.tempBox, wx.VERTICAL)

        # Line up smaller sub sizers
        gui.AddLinearSpacer(self.tempSizer, 10)
        self.tempSizer.Add(self.tempText, flag=wx.ALIGN_CENTER)
        gui.AddLinearSpacer(self.tempSizer, 10)
        self.tempSizer.Add(self.tempValue, flag=wx.ALIGN_CENTER)
        gui.AddLinearSpacer(self.tempSizer, 25)

        self.buttonSizer.Add(self.tempButton, flag=wx.ALIGN_CENTER)
        gui.AddLinearSpacer(self.buttonSizer, 10)
        self.buttonSizer.Add(self.stopCool, 1, flag=wx.ALIGN_CENTER)

        # Line up larger chunks with main sizer
        gui.AddLinearSpacer(self.tempBoxSizer, 5)
        self.tempBoxSizer.Add(self.tempSizer, flag=wx.ALIGN_CENTER)
        gui.AddLinearSpacer(self.tempBoxSizer, 5)
        self.tempBoxSizer.Add(self.buttonSizer, flag=wx.ALIGN_CENTER)
        gui.AddLinearSpacer(self.tempBoxSizer, 15)
        self.vertSizer.Add(self.tempBoxSizer, flag=wx.ALIGN_CENTER)

        # Variables
        self.tempToSend = ""

        # Bindings
        self.Bind(wx.EVT_TEXT, self.getTemp, id=2031)
        self.Bind(wx.EVT_BUTTON, self.onCool, id=2032)
        self.Bind(wx.EVT_BUTTON, self.onStopCooling, id=2033)

        self.SetSizer(self.vertSizer)
        self.vertSizer.Fit(self)

    def getTemp(self, event):
        """
        Called when someone is typing in the temperature text control box.
        """
        self.tempToSend = self.tempValue.GetValue()

    def onCool(self, event):
        """
        When the cool button is pressed this will check if the entered temperature meets certain requirements, then
        it will send the command to the Evora server to set the TEC cooler.
        """
        if self.tempToSend.isnumeric():  # Is temp a float?

            if float(self.tempToSend) >= -100.0 and float(self.tempToSend) <= -10.0:  # Is it within the hardware bounds?

                logger.info(str(float(self.tempToSend)))
                self.logFunction = self.logTemp
                command = "setTEC " + str(int(self.tempToSend))

                if self.parent.exposureInstance.abort:
                    dialog = wx.MessageDialog(None, "Do you want to change temperature during exposure?", "", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
                    answer = dialog.ShowModal()
                    dialog.Destroy()

                    if answer == wx.ID_OK:
                        self.logFunction = self.logTemp
                        logString = log_utils.get_log_str(command, 'pre')
                        self.log(self.logFunction, logString)

                        d = self.protocol.sendCommand(command)
                        d.addCallback(self.cooling_callback)

                        if not self.stopCool.IsEnabled():
                            self.stopCool.Enable(True)

                else:
                    self.logFunction = self.logTemp
                    logString = log_utils.get_log_str(command, 'pre')
                    self.log(self.logFunction, logString)

                    d = self.protocol.sendCommand(command)
                    d.addCallback(self.cooling_callback)

                    if not self.stopCool.IsEnabled():
                        self.stopCool.Enable(True)

            else:
                dialog = wx.MessageDialog(None, "Temperature is not within the bounds.", "", wx.OK | wx.ICON_ERROR)
                dialog.ShowModal()
                dialog.Destroy()

        else:
            dialog = wx.MessageDialog(None, "Temperature specified is not a number.", "", wx.OK | wx.ICON_ERROR)
            dialog.ShowModal()
            dialog.Destroy()

    def cooling_callback(self, msg):
        """
        Executes when the camera TEC temperature has been set.
        """
        self.logFunction = self.logTemp
        logString = log_utils.get_log_str("setTEC " + msg, 'post')
        self.log(self.logFunction, logString)
        logger.debug("Cooling to: " + msg)

    def onStopCooling(self, event):
        """
        When the stop cooling button is pressed this sends a command to Evora to warmup.
        """
        self.logFunction = self.logTemp
        logString = log_utils.get_log_str("warmup", 'pre')
        self.log(self.logFunction, logString)

        self.stopCool.Enable(False)
        d = self.protocol.sendCommand("warmup")
        d.addCallback(self.stopCooling_callback)

    def stopCooling_callback(self, msg):
        """
        Called when the server has completed its warmup routine.
        """
        self.logFunction = self.logTemp
        logString = log_utils.get_log_str("warmup " + msg, 'post')
        self.log(self.logFunction, logString)

        logger.info("Warmed with exit: " + msg)

    def watchTemp(self):
        """
        Run as a demon thread in the background when the GUI connects to the camera.
        Asks server for temperature every 10 seconds and sets a callback function.
        """
        # create an infinite while loop
        while self.isConnected:
            d = self.protocol.sendCommand("temp")
            d.addCallback(self.callbackTemp)
            #  put thread to sleep; on wake up repeats
            time.sleep(10)

    def callbackTemp(self, msg):
        """
        Executes when the server sends the temperature back upon request.
        Displays a bitmap in the status bar to indicate the TEC status.
        """
        # print msg
        # print threading.current_thread().name
        temp = msg.split(",")[2]  # parser sends stats on temperture where I grab that temp
        self.currTemp = float(temp)
        temp = str(int(round(float(temp))))
        mode = int(msg.split(",")[0])
        targetTemp = msg.split(",")[3]
        # if self.current_mode is not None:
        #     self.current_mode = mode

        # self.parent.parent.parent.stats.SetStatusText("Current Temp:            " + temp + " C", 0)
        wx.CallAfter(self.parent.parent.parent.stats.SetStatusText, "              " + temp + " C", 0)

        # based on temp change bitmap color
        # 20037 is NotReached
        # 20035 is NotStabalized
        # 20036 is Stabalized
        # 20034 is Off

        if mode != self.current_mode or (float(targetTemp) > 0 and float(targetTemp) - float(temp) > 15):
            print("UPDATING COLORS")
            self.current_mode = mode
            bmp_ctrl = None
            if mode != 20034 and not self.stopCool.IsEnabled():
                logger.info("Enter")
                self.stopCool.Enable(True)
            # if self.prevMode is None or self.prevMode != mode:
            # print("MAKING NEW BITMAP")
            if mode == 20034 and float(temp) >= 0:
                # bitmap = wx.StaticBitmap(self.parent.parent.parent.stats, -1, wx.Bitmap('img/greenCirc.png'))
                bmp = wx.Bitmap("client/gui/img/greenBar.bmp")
                bmp.SetWidth(40)
                bmp_ctrl = wx.StaticBitmap(self.parent.parent.parent.stats, -1, bmp)
                # self.parent.parent.parent.stats.AddWidget(bmp_ctrl, pos=0, horizontalalignment=EnhancedStatusBar.ESB_ALIGN_LEFT)

            if mode == 20037 or (mode == 20034 and float(temp) < 0):
                # bitmap = wx.StaticBitmap(self.parent.parent.parent.stats, -1, wx.Bitmap('img/redCirc.png'))
                bmp = wx.Bitmap("client/gui/img/redBar.bmp")
                bmp.SetWidth(40)
                bmp_ctrl = wx.StaticBitmap(self.parent.parent.parent.stats, -1, bmp)
                # self.parent.parent.parent.stats.AddWidget(bmp_ctrl, pos=0, horizontalalignment=EnhancedStatusBar.ESB_ALIGN_LEFT)

            if mode == 20035:
                # bitmap = wx.StaticBitmap(self.parent.parent.parent.stats, -1, wx.Bitmap('img/yellowCirc.png'))
                bmp = wx.Bitmap("client/gui/img/yellowBar.bmp")
                bmp.SetWidth(40)
                bmp_ctrl = wx.StaticBitmap(self.parent.parent.parent.stats, -1, bmp)
                # self.parent.parent.parent.stats.AddWidget(bmp_ctrl, pos=0, horizontalalignment=EnhancedStatusBar.ESB_ALIGN_LEFT)

            if mode == 20036:
                # bitmap = wx.StaticBitmap(self.parent.parent.parent.stats, -1, wx.Bitmap('img/blueCirc.png'))
                bmp = wx.Bitmap("client/gui/img/blueBar.bmp")
                bmp.SetWidth(40)
                bmp_ctrl = wx.StaticBitmap(self.parent.parent.parent.stats, -1, bmp)
                # self.parent.parent.parent.stats.AddWidget(bmp_ctrl, pos=0, horizontalalignment=EnhancedStatusBar.ESB_ALIGN_LEFT)

            # self.parent.parent.parent.stats.AddWidget(bitmap, pos=0, horizontalalignment=EnhancedStatusBar.ESB_ALIGN_LEFT,
            #                                              verticalalignment=EnhancedStatusBar.ESB_ALIGN_BOTTOM)
            # self.prevMode = mode
            self.parent.parent.parent.stats.AddWidget(bmp_ctrl, pos=0, horizontalalignment=EnhancedStatusBar.ESB_ALIGN_LEFT)  # noqa: F821

    def logTemp(self, logmsg):
        """
        Handles displaying log information to the user.
        """
        logger.info("logging from temperature class")
        logInstance = self.parent.parent.parent.log.logInstance
        wx.CallAfter(logInstance.threadSafeLogStatus, logmsg)

    def log(self, logfunc, logmsg):
        """
        Pre: Before an exposure is set the correct log function to call is set to self.logFunction.
        For example, setting self.logFunction to self.logScript will log on the scripting status
        and the log tab versus self.logExposure.  Also passed in is the logmsg that you want to
        print.
        Post: This method will run the logfunc to print the log message to the correct status
        boxes; it returns nothing.
        """
        logger.info("entered log")
        logfunc(logmsg)


class FilterControl(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        # global variables
        self.parent = parent
        self.protocol2 = None
        self.logFunction = None
        self.filterConnection = False
        self.watch = False
        self.adjusting = False
        self.currentFilter = None

        self.statusBar = None
        self.loadingDots = ""

        self.watchFilterTime = 10  # every second when moving filter position
        self.targetFilter = None  # keep track globally of the target filter

        # Main sizers
        self.vertSizer = wx.BoxSizer(wx.VERTICAL)

        # Additional Sub-sizers
        self.filterSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.subVert = wx.BoxSizer(wx.VERTICAL)
        self.statusVert = wx.BoxSizer(wx.VERTICAL)
        self.buttonSizer = wx.BoxSizer(wx.HORIZONTAL)

        # Variables
        filters = pd.read_csv("client/currentFilters.txt")
        self.filterNum, self.filterName = filters['position'].values, filters['filter'].values.tolist()
        # self.filterName = self.filterName.tolist()
        # self.filterNum = self.filterNum.astype(int).tolist()
        self.filterMap = {}
        for i in range(len(self.filterName)):
            self.filterMap[self.filterName[i]] = self.filterNum[i]

        # Widgets
        self.filterBox = wx.StaticBox(self, id=2040, label="Filter Controls", size=(100, 100), style=wx.ALIGN_CENTER)
        self.filBoxSizer = wx.StaticBoxSizer(self.filterBox, wx.VERTICAL)

        # self.statusBox = wx.StaticBox(self, id=2041, label="Filter Status", size=(150,150), style=wx.ALIGN_CENTER)
        # self.statusBoxSizer = wx.StaticBoxSizer(self.statusBox, wx.VERTICAL)

        self.filterText = wx.StaticText(self, id=2042, label="Filter Type")
        self.filterMenu = wx.ComboBox(self, id=2043, choices=self.filterName, size=(60, -1), style=wx.CB_READONLY)
        self.filterButton = wx.Button(self, id=2044, label="Rotate", size=(70, -1))
        self.homeButton = wx.Button(self, id=2046, label="Home", size=(70, -1))
        # self.statusBox = wx.TextCtrl(self, id=2045, style=wx.TE_READONLY|wx.TE_MULTILINE, size=(200,100))
        self.enableButtons(False)
        self.loadingDotsTimer = wx.Timer(self, id=2047)

        # Line Up Smaller Sub Sizers
        self.filterSizer.Add(self.filterText, flag=wx.ALIGN_CENTER)
        gui.AddLinearSpacer(self.filterSizer, 15)
        self.filterSizer.Add(self.filterMenu, flag=wx.ALIGN_CENTER)

        self.buttonSizer.Add(self.homeButton, flag=wx.ALIGN_CENTER)
        gui.AddLinearSpacer(self.buttonSizer, 10)
        self.buttonSizer.Add(self.filterButton, flag=wx.ALIGN_CENTER)

        self.subVert.Add(self.filterSizer)
        gui.AddLinearSpacer(self.subVert, 10)
        self.subVert.Add(self.buttonSizer, flag=wx.ALIGN_CENTER)

        self.filBoxSizer.Add((200, 10))
        self.filBoxSizer.Add(self.subVert, flag=wx.ALIGN_CENTER)
        self.filBoxSizer.Add((0, 30))

        # self.statusBoxSizer.Add(self.statusBox, flag=wx.ALIGN_CENTER)

        # Line up larger chunks with main sizers
        self.vertSizer.Add(self.filBoxSizer)
        # gui.AddLinearSpacer(self.vertSizer, 15)
        # self.vertSizer.Add(self.statusBoxSizer)

        # Variables
        self.filterSelection = ""
        self.currFilterNum = None

        # Bindings
        self.Bind(wx.EVT_COMBOBOX, self.onFilterSelection, id=2043)
        self.Bind(wx.EVT_BUTTON, self.onRotate, id=2044)
        self.Bind(wx.EVT_BUTTON, self.onHome, id=2046)
        self.Bind(wx.EVT_TIMER, self.loadingDot, id=2047)

        self.SetSizer(self.vertSizer)
        self.vertSizer.Fit(self)

    def loadingDot(self, event):
        maxDots = 4

        def numberOfDots(string):
            num = 0
            for s in string[::-1]:
                if s == ".":
                    num += 1
            return num

        statusBar = self.parent.parent.parent.stats
        s = statusBar.GetStatusText(3)
        dotNum = numberOfDots(s)
        if dotNum < maxDots:
            s += "."
        else:
            s = s[:-maxDots]

        statusBar.SetStatusText(s, 3)

    def onFilterSelection(self, event):
        """
        Sets global filter selection when the user selects from the drop down menu.
        """
        self.filterSelection = self.filterMenu.GetValue()
        print(self.currentFilter)
        if self.filterSelection != self.currentFilter and self.filterButton.IsEnabled():
            gui.SetButtonColor(self.filterButton, 'white', 'green')
            # self.filterButton.SetBackgroundColour('green')
            # self.filterButton.SetForegroundColour('white')
        else:
            gui.SetButtonColor(self.filterButton, None, None)
            # self.filterButton.SetBackgroundColour(None)
            # self.filterButton.SetForegroundColour(None)

        logger.debug("selection: " + self.filterSelection)

    def onRotate(self, event):
        """
        This method is called when the "Rotate To" button is pressed.  It is send a command to the Evora Server
        that will slew the filter appropriately.
        """
        if self.filterSelection == "":
            logger.info("No filter selected")

        else:
            logger.debug(str(type(self.filterSelection)))

            # send command to rotate to the specified position
            # find position
            pos = None
            for i in range(len(self.filterName)):
                if str(self.filterSelection) == self.filterName[i]:
                    pos = self.filterNum[i]
            logger.debug("index: " + str(pos))

            self.targetFilter = pos
            self.watchFilterTime = 1.5  # set to one seconds
            self.watch = True

            self.logFunction = self.logFilter
            logString = log_utils.get_log_str("filter move " + str(self.filterName[pos]), 'pre')
            self.log(self.logFunction, logString)

            self.loadingDotsTimer.Start(350)
            d = self.protocol2.addDeferred("findPos")
            d.addCallback(self.findPosCallback)

            d = self.protocol2.sendCommand("move " + str(pos))
            d.addCallback(self.rotateCallback)
            thread.start_new_thread(self.filterWatch, ())

            self.enableButtons(False)

    def rotateCallback(self, msg):
        """
        Called when filter has started slewing, and activates the process of tracking where the filter is at.
        """
        self.logFunction = self.logFilter

        logger.debug(msg)

        logString = log_utils.get_log_str("filter move " + msg, 'post')

        logger.debug("in rotate callback " + logString)

        self.log(self.logFunction, logString)

        logger.info("Completed rotation...")

        self.enableButtons(True)
        self.protocol2.removeDeferred('findPos')  # If deffered does not get activated remove it.

    def findPosCallback(self, msg):
        """
        Reports the current position to the user through text boxes.
        """
        self.adjusting = True

        self.logFunction = self.logFilter
        logString = log_utils.get_log_str("filter findPos None", 'post')
        self.log(self.logFunction, logString)

    def onHome(self, event):
        """
        Starts the homing sequence for the filter.
        """
        self.logFunction = self.logFilter
        logString = log_utils.get_log_str("filter home", 'pre')
        self.log(self.logFunction, logString)

        d = self.protocol2.sendCommand("home")
        d.addCallback(self.homingCallback)
        logger.info("homing...")

        self.statusBar.SetStatusText("Filter:  HOMING", 3)
        self.loadingDotsTimer.Start(350)

        self.enableButtons(False)

    def homingCallback(self, msg):
        self.logFunction = self.logFilter
        logString = log_utils.get_log_str("filter home " + msg, 'post')
        self.log(self.logFunction, logString)

        logger.debug("Done homing: " + msg)

        self.logFunction = self.logFilter
        logString = log_utils.get_log_str("filter getFilter", 'pre')
        self.log(self.logFunction, logString)

        self.loadingDotsTimer.Stop()
        if int(msg) == 1:
            d = self.protocol2.sendCommand("getFilter")
            d.addCallback(self.getFilterCallback)
        else:
            self.statusBar.SetStatusText("Filter: FAILED", 3)

        self.enableButtons(True)

    def getFilterCallback(self, msg):
        pos = int(msg)
        if pos > 5:
            self.statusBar.SetStatusText("Filter: FAILED", 3)
            return
        logger.debug("position: " + str(pos))
        filter = self.filterName[pos]

        self.logFunction = self.logFilter
        if self.targetFilter is not None and self.targetFilter != pos:
            # logString = log_utils.get_log_str("filter getFilter report " + filter, 'post')
            # self.log(self.logFunction, logString)

            # self.statusBar.SetStatusText("Filter:  %s" % (filter+self.loadingDots), 3)
            wx.CallAfter(self.statusBar.SetStatusText, "Filter:    %s" % filter, 3)

        # set drop down menu to the correct filter
        elif self.targetFilter == pos and self.adjusting:  # Kill the getFilter sequence when adjusting
            self.watch = False
            self.logFunction = self.logFilter
            # logString = log_utils.get_log_str("filter getFilter finding " + filter + "," + str(pos), 'post')
            # self.log(self.logFunction, logString)

            self.filterMenu.SetSelection(pos)
            self.filterSelection = str(self.filterMenu.GetValue())
            self.targetFilter = None

            # self.statusBar.SetStatusText("Filter:  %s" % (filter+self.loadingDots), 3)
            wx.CallAfter(self.statusBar.SetStatusText, "Filter:    %s" % filter, 3)

        else:
            self.watch = False
            self.logFunction = self.logFilter
            # logString = log_utils.get_log_str("filter getFilter set " + filter + "," + str(pos), 'post')
            # self.log(self.logFunction, logString)

            self.filterMenu.SetSelection(pos)
            self.filterSelection = str(self.filterMenu.GetValue())
            self.targetFilter = None
            self.loadingDotsTimer.Stop()

            self.currentFilter = filter
            gui.SetButtonColor(self.filterButton, None, None)

            # self.statusBar.SetStatusText("Filter:   %s" % filter, 3)
            wx.CallAfter(self.statusBar.SetStatusText, "Filter:     %s" % filter, 3)
        logger.debug("Filter position is " + filter)

    def getFilterCallback_thread(self, msg):
        """
        This is to release the main thread from completing the callback chain.
        """
        thread.start_new_thread(self.getFilterCallback, (msg,))

    def filterWatch(self):
        """
        Pre: No input.
        Post: Updates filter position every so often and displays in status box.
        """
        while self.watch:
            d = self.protocol2.sendCommand("getFilter")
            d.addCallback(self.getFilterCallback_thread)
            time.sleep(self.watchFilterTime)

    def populateFilterList(self, file):
        try:
            # test to see if it imports
            filters = pd.read_csv(".currentFilters.txt")
            # newNum, newName = filters['position'].values.tolist(), filters['filter'].values.tolist()
            print("Testing suff")
            if (True in filters['position'].isnull()) or (True in filters['filter'].isnull()):
                print("Stop")
                return False

            print("Don't do it")
            f = open(file, 'r')
            curr_list = open(".currentFilters.txt", 'w')
            for line in f:
                curr_list.write(line)

            curr_list.close()
            f.close()
            return True
        except KeyError:
            return False

    def refreshList(self):
        """
        When "Refresh" is clicked in the filter sub-menu of the file menu this function is called.
        This method reads the filters.txt file and updates the GUI filter drop down menu while also resetting
        the internal variables that are used.  It returns nothing.
        """
        # clear the current GUI drop down filter menu
        self.filterMenu.Clear()

        # grab new filters in the assumed to be changed file
        filters = pd.read_csv(".currentFilters.txt")
        newNum, newName = filters['position'].values.tolist(), filters['filter'].values.tolist()

        # update variables
        self.filterName = newName
        self.filterNum = newNum
        self.filterMap = {}
        for i in range(len(newNum)):
            self.filterMap[newName[i]] = newNum[i]
        logger.debug(str(self.filterMap))

        # update GUI drop down filter menu
        for i in newName:
            self.filterMenu.Append(i)

    def enableButtons(self, bool):
        self.filterButton.Enable(bool)
        self.homeButton.Enable(bool)

    def logFilter(self, logmsg):
        logger.info("logging from exposure class")
        # self.sendToStatus(logmsg)
        logInstance = self.parent.parent.parent.log.logInstance
        wx.CallAfter(logInstance.threadSafeLogStatus, logmsg)

    def log(self, logfunc, logmsg):
        """
        Pre: Before an exposure is set the correct log function to call is set to self.logFunction.
        For example, setting self.logFunction to self.logScript will log on the scripting status
        and the log tab versus self.logExposure.  Also passed in is the logmsg that you want to
        print.
        Post: This method will run the logfunc to print the log message to the correct status
        boxes; it returns nothing.
        """
        logger.info("entered log in filter classes")
        logfunc(logmsg)
