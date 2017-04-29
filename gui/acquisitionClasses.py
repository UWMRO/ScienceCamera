#!/usr/bin/python2
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

## Imports
import time
import thread
import threading
import shutil
import os
import wx  # get wxPython
from twisted.protocols.ftp import FTPFileListProtocol

import numpy as np  # get NumPy

# allows widgets to be inserted into wxPython status bar probably won't work on wxPython 3.x
import EnhancedStatusBar
import AddLinearSpacer as als  # get useful methods
import MyLogger

__author__ = "Tristan J. Hillis"

# Comment on documentation:
# When reading the doc strings if "Pre:" is present then this stands for "precondition", or the conditions in order to invoke something.
# Oppositely, "Post:" stands for "postcondition" and states what is returned by the method.

"""
This set of classes handles everything in the imaging tab.
"""

# Global Variables
logger = MyLogger.myLogger("acquisitionClasses.py", "client")

#### Class that handles widgets related to exposure
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
        self.ftp = None # Gives access to FTP client protocol
        self.parent = parent  # gives access to the higher classes
        self.startTimer = 0  # keeps track of the timer count in ints
        self.endTimer = 0  # keeps track of the max timer count as an int
        self.saveDir = "/home/mro/data/raw/"  # Default directory to save images to.

        self.abort = False  # tells you if the abort button is active (i.e. True if you can abort and False if not)
        self.seriesImageNumber = None  # initialize a series image number
        self.currentImage = None  # initializes to keep track of the current image name class wide
        self.logFunction = None  # keeps an instance of the function that will be used to log the status

        ### Main sizers
        self.vertSizer = wx.BoxSizer(wx.VERTICAL)
        self.horzSizer = wx.BoxSizer(wx.HORIZONTAL)
        #####

        ### Additional sub sizers
        self.exposeSizer = wx.BoxSizer(wx.HORIZONTAL)  # used for spacing expTime and expValue
        self.buttonSizer = wx.BoxSizer(wx.HORIZONTAL)  # used for spacing expose and stop buttons
        self.nameSizer = wx.BoxSizer(wx.VERTICAL)  # use for spacing name text and text ctrl
        #####

        #### Widgets
        self.expTime = wx.StaticText(self, id=2000, label="Exposure Time (s)")
        self.name = wx.StaticText(self, id=2001, label="Save Name")
        self.nameField = wx.TextCtrl(self, id=2002, size=(150, -1))

        self.expValue = wx.TextCtrl(self, id=2003, size=(45, -1), value="0", style=wx.TE_READONLY)
        
        self.expButton = wx.Button(self, id=2004, label="Expose", size=(60, -1))
        self.stopExp = wx.Button(self, id=2005, label="Abort", size=(60, -1))
        self.setDirButton = wx.Button(self, id=2006, label="Set Dir.", size=(60, -1))
        self.stopExp.Enable(False)

        self.expBox = wx.StaticBox(self, id=2006, label="Exposure Controls", size=(100, 100), style=wx.ALIGN_CENTER)
        self.expBoxSizer = wx.StaticBoxSizer(self.expBox, wx.VERTICAL)

        self.timer = wx.Timer(self, id=2007)
        self.sampleTimer = wx.Timer(self, id=2008)
        self.sampleTime = None
        #####

        ##### Line up smaller sub sizers
        als.AddLinearSpacer(self.exposeSizer, 15)
        self.exposeSizer.Add(self.expTime, flag=wx.ALIGN_CENTER)
        als.AddLinearSpacer(self.exposeSizer, 15)
        self.exposeSizer.Add(self.expValue, flag=wx.ALIGN_CENTER)
        als.AddLinearSpacer(self.exposeSizer, 15)

        self.buttonSizer.Add(self.setDirButton, flag=wx.ALIGN_CENTER)
        als.AddLinearSpacer(self.buttonSizer, 10)
        self.buttonSizer.Add(self.expButton, flag=wx.ALIGN_CENTER)
        als.AddLinearSpacer(self.buttonSizer, 10)
        self.buttonSizer.Add(self.stopExp, flag=wx.ALIGN_CENTER)

        self.nameSizer.Add(self.name, flag=wx.ALIGN_CENTER)
        als.AddLinearSpacer(self.nameSizer, 8)
        self.nameSizer.Add(self.nameField, flag=wx.ALIGN_CENTER)
        ####

        #### Line up larger chuncks with main sizer
        als.AddLinearSpacer(self.expBoxSizer, 10)
        self.expBoxSizer.Add(self.nameSizer, flag=wx.ALIGN_CENTER)
        als.AddLinearSpacer(self.expBoxSizer, 5)
        self.expBoxSizer.Add(self.exposeSizer, flag=wx.ALIGN_CENTER)
        als.AddLinearSpacer(self.expBoxSizer, 5)
        self.expBoxSizer.Add(self.buttonSizer, flag=wx.ALIGN_CENTER)
        als.AddLinearSpacer(self.expBoxSizer, 5)

        self.vertSizer.Add(self.expBoxSizer, flag=wx.ALIGN_CENTER)
        ####

        ### Global variables
        self.timeToSend = 0  # Tracks the time that will be sent to the camera
        self.nameToSend = "" # tracks the name to send

        ### Bindings
        self.Bind(wx.EVT_TEXT, self.nameText, id=2002)  # bind self.nameField
        self.Bind(wx.EVT_TEXT, self.onExpTime, id=2003)  # bind self.expValue
        self.Bind(wx.EVT_BUTTON, self.onExpose, id=2004)  # bind self.expButton
        self.Bind(wx.EVT_BUTTON, self.onStop, id=2005)  # bind self.stopExp
        self.Bind(wx.EVT_BUTTON, self.onSetDir, id=2006) # bind self.setDirButton
        self.Bind(wx.EVT_TIMER, self.onExposeTimer, id=2007)
        ###

        self.SetSizer(self.vertSizer)
        self.vertSizer.Fit(self)

    def nameText(self, event):
        """
        Executes on the even that anything new is type into the name text box and sets it to
        the global variable self.nameToSend for sending to Evora.
        """
        self.nameToSend = self.nameField.GetValue()

    def onExpTime(self, event):
        """
        Executes when there is a new string typed into the exposure time field.  It then
        passes it to the global variable self.timeToSend for sending to Evora.
        """
        self.timeToSend = self.expValue.GetValue()

    def onExpose(self, event):
        """
        Executes when the expose button is pressed. It checks that the variable
        self.exposeToSend is a float. It it passes then this value is sent to Evora.  If it
        fails a dialog box tells the user the varible is not a number and will not send it
        to Evora.
        """
        lessThanZero = True
        if als.isNumber(self.timeToSend):
            if(float(self.timeToSend) < 0):
                dialog = wx.MessageDialog(None, "Exposure time can not be less than 0...will not expose", "", wx.OK | wx.ICON_ERROR)
                dialog.ShowModal()
                dialog.Destroy()
                lessThanZero = False

        else:
            dialog = wx.MessageDialog(None, "Exposure time not a number...will not expose.",
                                      "", wx.OK | wx.ICON_ERROR)
            dialog.ShowModal()
            dialog.Destroy()

        if self.nameToSend is "":
            dialog = wx.MessageDialog(None, "No name was given...will not expose", "",
                                      wx.OK | wx.ICON_ERROR)
            dialog.ShowModal()
            dialog.Destroy()
        else:
            pass

        # if statement here is more for redundancy.  The above MessageDialogs let the user their input is incorrect,
        # else they will enter this if statement just fine.
        if als.isNumber(self.timeToSend) and self.nameToSend is not "" and lessThanZero:
            
            line = self.getAttributesToSend().split()

            # Set the correct log function that only prints to the log tab
            self.logFunction = self.logExposure
            
            # get image type
            imType = int(line[0])
            itime = float(line[3])

            #self.expButton.SetLabel("Abort")
            if imType == 1:  # single exposure
                line = " ".join(line[1:])  # bring all the parameters together
                overwrite = None

                if als.checkForFile(self.saveDir + self.currentImage + ".fits"):
                    dialog = wx.MessageDialog(None, "File already exists do you want to overwrite?", "", wx.OK | wx.CANCEL|wx.ICON_QUESTION)
                    overwrite = dialog.ShowModal()
                    dialog.Destroy()
                    
                if overwrite is None or overwrite == wx.ID_OK:
                    self.expButton.Enable(False)
                    self.stopExp.Enable(True)
                    self.abort = True
                    command = "expose " + line
                    logString = als.getLogString(command, 'pre')
                    self.log(self.logFunction, logString)

                    d = self.protocol.sendCommand(command)
                    d.addCallback(self.expose_callback_thread)
                    self.exposeTimer(itime)
                    #thread.start_new_thread(self.exposeTimer, (itime,))

            if imType == 2:  # real time exposure
                self.expButton.Enable(False)
                self.stopExp.Enable(True)
                self.abort = True
                line = " ".join(line[1:])
                
                # start callback that looks for a path leading to a real image
                d = self.protocol.addDeferred("realSent")
                d.addCallback(self.displayRealImage_thread)

                command = "real " + line
                logString = als.getLogString(command, 'pre')
                self.log(self.logFunction, logString)

                d = self.protocol.sendCommand(command)
                d.addCallback(self.realCallback)  # this will clear the image path queue

                # start timer
                self.exposeTimer(itime)
                #thread.start_new_thread(self.exposeTimer, (itime,))

            if imType == 3:  # series exposure
                dialog = wx.TextEntryDialog(None, "How many exposure?", "Entry", "1", wx.OK | wx.CANCEL)
                answer = dialog.ShowModal()
                dialog.Destroy()

                if answer == wx.ID_OK:
                    self.seriesImageNumber = dialog.GetValue()
                    
                    if als.isInt(self.seriesImageNumber):
                        logger.debug("Number of image to be taken: " + str(int(self.seriesImageNumber)))
                        line[2] = self.seriesImageNumber
                        line = " ".join(line[1:])
                        
                        # check for overwrite
                        overwrite = None
                        if (self.checkForImageCounter(self.currentImage) and als.checkForFile(self.saveDir + self.currentImage + ".fits"))\
                           or (not self.checkForImageCounter(self.currentImage) and als.checkForFile(self.saveDir + self.currentImage + "_001.fits")):
                            
                            dialog = wx.MessageDialog(None, "File already exists do you want to overwrite?", "", wx.OK | wx.CANCEL|wx.ICON_QUESTION)
                            overwrite = dialog.ShowModal()
                            dialog.Destroy()
                            
                        if(overwrite is None or overwrite == wx.ID_OK): # Overwrite existing file
                            self.expButton.Enable(False)
                            self.stopExp.Enable(True)
                            self.abort = True

                            # set up all callbacks for series
                            for i in range(int(self.seriesImageNumber)):
                                d = self.protocol.addDeferred("seriesSent" + str(i+1))
                                d.addCallback(self.displaySeriesImage_thread)

                            command = "series " + str(line)
                            logString = als.getLogString(command, 'pre')
                            self.log(self.logFunction, logString)

                            d = self.protocol.sendCommand(command)
                            d.addCallback(self.seriesCallback)

                            # start timer
                            self.exposeTimer(itime)
                            #thread.start_new_thread(self.exposeTimer, (itime,))

                    else:
                        dialog = wx.MessageDialog(None, "Entry was not a valid integer!", "", wx.OK | wx.ICON_ERROR)
                        dialog.ShowModal()
                        dialog.Destroy()

    def exposeTimer(self, time):
        """
        This function, given some time, will start the wxPython Timer object and will set it to call
        onExposeTimer every 10 milliseconds.
        """
        exposeTimes = [0.0886, 0.154, 0.343, 5.8]  # exposure times in seconds
        if(self.parent.typeInstance.exposeType.GetSelection() != 1):  # check if exposure type is real time
            expTime = float(time) + exposeTimes[self.parent.parent.parent.readoutIndex]  # trailing digit is readout time
        else:  # real time has a set read time
            expTime = float(time) + exposeTimes[1]  # trailing digit is readout time
        
        # get the max range for progress bar
        self.endTimer = int(expTime / (50.0*10**-3)) # timer will update every 10 ms
        
        # set exposure progress bar range
        self.parent.parent.parent.expGauge.SetRange(self.endTimer)

        # start timer
        wx.CallAfter(self.timer.Start, 50) # 50 millisecond intervals

    def onExposeTimer(self, event):
        """
        This is called by the wxPython Timer object and updates the exposure gauge by an integer
        value every 10 milliseconds.
        """
        if self.startTimer == self.endTimer:
            self.timer.Stop()
            self.startTimer = 0

        else:
            # get gauge value
            val = self.parent.parent.parent.expGauge.GetValue()
            wx.CallAfter(self.parent.parent.parent.expGauge.SetValue, val+1)
            self.startTimer += 1

    def expose_callback_thread(self, msg):
        """
        Used to execute the method self.exposeCallback in another thread.
        """
        thread.start_new_thread(self.exposeCallback, (msg,))

    def exposeCallback(self, msg):
        """
        Called when the client recieves the "expose" keyword from the server indicating the exposure is complete.
        Stops exposure gauge and resets it, disables the stop button and re-enables the exposure button,
        and if the image was successfully taken then it plots it.
        """
        ### May need to thread to a different method if to slow
        results = msg.split(",")

        # immediatly reset button
        self.abort = False
        self.expButton.Enable(True)
        
        if self.stopExp.IsEnabled():
            self.stopExp.Enable(False)

        ## complete progress bar for image acquisition
        # check to see if timer is still going and stop it (callback might come in early)
        if(self.timer.IsRunning()):
            self.timer.Stop()
        
        # finish out gauge and then reset it
        self.parent.parent.parent.expGauge.SetValue(self.endTimer)

        # get success;
        success = int(results[0])  # 1 for true 0 for false
        #print success

        # at the end of the callback reset the gauge (signifies a reset for exposure)
        self.parent.parent.parent.expGauge.SetValue(0)
        self.startTimer = 0

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
            time = float(results[2])

            logger.debug(path + name)

            savedImage, d = self.copyImage2(path, name)
            print("Saved Image is:", savedImage)

            d.addCallback(self.display, savedImage=savedImage, msg=msg)
            
            # get data
            #data = als.getData(path+name)
            #data = als.getData(savedImage)
            #stats_list = als.calcStats(data)

            # change the gui with thread safety
            # plots the image
            #wx.CallAfter(self.safePlot, data, stats_list)

            # copy file to different folder
            #self.copyImage(path, name)

            # log the status
            #self.logFunction = self.logExposure
            #logString = als.getLogString("expose " + msg + "," + self.currentImage, 'post')
            #self.log(self.logFunction, logString)
            
        else:
            logger.info("Successfully Aborted")

    def display(self, results, savedImage, msg):
        data = als.getData(savedImage)
        stats_list = als.calcStats(data)

        # change the gui with thread safety
        # plots the image
        wx.CallAfter(self.safePlot, data, stats_list)

        # copy file to different folder
        #self.copyImage(path, name)

        # log the status
        self.logFunction = self.logExposure
        logString = als.getLogString("expose " + msg + "," + self.currentImage, 'post')
        self.log(self.logFunction, logString)
                
    def safePlot(self, data, stats_list):
        """
        Used in conjunction with wx.CallAfter to update the embedded Matplotlib in the image window.
        If the image window is closed it will open it and then plot, otherwise it is simply plotted.
        """
        if not self.parent.parent.parent.imageOpen: # Open image window if closed.
            # create new window
            self.parent.parent.parent.openImage("manual open")

        else: # If image window open then clear the axis of the previous image
            self.parent.parent.parent.window.panel.clear()

        plotInstance = self.parent.parent.parent.window
        sliderVal = plotInstance.currSliderValue / 10

        plotInstance.panel.updatePassedStats(stats_list)
        plotInstance.panel.plotImage(data, sliderVal, plotInstance.currMap)
        plotInstance.panel.updateScreenStats()
        plotInstance.panel.refresh()

    def displayRealImage_thread(self, msg):
        """
        Used to excute the displaying of the real image when the client recieves there is a real
        image waiting to be plotted.
        """
        thread.start_new_thread(self.displayRealImage, (msg,))

    def displayRealImage(self, msg):
        """
        Called when client recieves that there is an image to be displayed from real time series.
        """
        path = msg
        
        # no abort then display the image
        if self.abort:  # means that abort can be called.
            # add a new deffered object to set up for another incoming image
            d = self.protocol.addDeferred("realSent")
            d.addCallback(self.displayRealImage_thread)

            if(self.timer.IsRunning()):
                self.timer.Stop()
            self.parent.parent.parent.expGauge.SetValue(self.endTimer)

            # get stats
            data = als.getData(path)
            stats_list = als.calcStats(data)
            
            # change the gui with thread safety
            wx.CallAfter(self.safePlot, data, stats_list)

            self.parent.parent.parent.expGauge.SetValue(0)
            self.startTimer = 0

            self.exposeTimer(self.timeToSend)
            #thread.start_new_thread(self.exposeTimer, (self.timeToSend,))
            
    def realCallback(self, msg):
        """
        Called when the camera has been aborted during a real time series exposure.
        """
        self.protocol.removeDeferred("realSent")  # Remove floating deffered object
        
        self.logFunction = self.logExposure
        logString = als.getLogString("real " + msg, 'post')
        self.log(self.logFunction, logString)

        logger.debug("Completed real time series with exit: " + msg)

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

        if(self.timer.IsRunning()):
            self.timer.Stop()
        self.parent.parent.parent.expGauge.SetValue(self.endTimer)
        # no abort then display the image
        if(imNum <= int(self.seriesImageNumber)):
            logger.info("Entered to display series image")



            # get stats
            data = als.getData(path)
            stats_list = als.calcStats(data)
            
            # change the gui with thread safety
            wx.CallAfter(self.safePlot, data, stats_list)
            
            # copy image over (counter looks like "_XXX.fits")
            logger.debug("current image name: " + self.currentImage)
            logger.debug(str(self.checkForImageCounter(self.currentImage)))
            
            if not self.checkForImageCounter(self.currentImage):
                self.currentImage += "_001"
                logger.debug("entered")
                
            else:
                if imNum > 1: 
                    self.iterateImageCounter(self.currentImage)

            self.copyImage(directory, name)

            self.logFunction = self.logExposure
            dataMsg = ",".join(msg)
            logString = als.getLogString("seriesSent " + dataMsg + "," + self.currentImage, 'post')
            self.log(self.logFunction, logString)



            if self.seriesImageNumber is not None:
                if imNum < int(self.seriesImageNumber):
                    self.exposeTimer(time)
                    #thread.start_new_thread(self.exposeTimer, (time,))
                    
        self.parent.parent.parent.expGauge.SetValue(0)
        self.startTimer = 0
                    
    def seriesCallback(self, msg):
        msg = msg.split(",")
        exitNumber = int(msg[1])  # server will send which count the series loop ended on
        if exitNumber <= int(self.seriesImageNumber):
            for i in range(exitNumber, int(self.seriesImageNumber) + 1):
                key = "seriesSent" + str(i)
                self.protocol.removeDeferred(key)

        # reset series image number
        #self.seriesImageNumber = None
        logger.debug(str(self.protocol._deferreds))
        
        self.abort = False
        self.expButton.Enable(True)
        if self.stopExp.IsEnabled():
            self.stopExp.Enable(False)
            
        # stop timer if running
        if self.timer.IsRunning():
            self.timer.Stop()

        # finish out the gauge
        self.parent.parent.parent.expGauge.SetValue(self.endTimer)

        # restart gauge and the timer count
        self.parent.parent.parent.expGauge.SetValue(0)
        self.startTimer = 0

        dataMsg = ",".join(msg)
        self.logFunction = self.logExposure
        logString = als.getLogString("series " + dataMsg, 'post')
        self.log(self.logFunction, logString)
        logger.debug("Completed real time series with exit: " + str(msg))

    def abort_callback(self, msg):
        self.parent.parent.parent.expGauge.SetValue(0)  # redundancy to clear the exposure gauge
        self.logFunction = self.logExposure
        logString = als.getLogString("abort " + msg, 'post')
        self.log(self.logFunction, logString)
        logger.debug("Aborted " + msg)

    """
    def openData(self, path, name):
        
        Deprecated
        
        print(als.printStamp() + "opening")
        self.parent.parent.parent.expGauge.SetValue(0)
        
        print(als.printStamp() + str(self.parent.parent.parent.imageOpen))
        # open image window 
        if(not self.parent.parent.parent.imageOpen):
            # create new window
            self.parent.parent.parent.openImage("manual open")
        print(als.printStamp() + "opened window")

        self.parent.parent.parent.window.panel.clear()
        data = self.parent.parent.parent.window.panel.getData(path+name)
        print(als.printStamp() + "got data")
        self.parent.parent.parent.window.panel.plotImage(data, 6.0, 'gray')
        print(als.printStamp() + "plotted")
        self.parent.parent.parent.window.panel.updateScreenStats()
        self.parent.parent.parent.window.panel.refresh()
    """

    def getAttributesToSend(self):
        """
        Method that will gather part of the command line to send to the server for exposing.
        """
        # get binning type
        binning = self.parent.parent.parent.binning
        readoutIndex = self.parent.parent.parent.readoutIndex

        # get exposure type
        exposeType = self.parent.typeInstance.exposeType.GetStringSelection()
        #print exposeType
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

        #line = "expose" # this is given before the command is sent off
        line = str(exposeType)
        line += " " + str(imageType).lower()
        line += " " + str(expNum) # This is the exposure number.  Should have dialog come up for when set to series to take in the number of exposures 
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

    def copyImage2(self, path, serverImName):
        """
        Pre: Takes in the diretory path to the original image file name as "path" as well as the 
             name of the orignal image as serverImName as strings.
        Post: The orignally created image is copied into a hard coded directory with the global
              current image name.  In the case of series images this current image name will be iterated.
              Returns nothing.
        """
        #fileList = FTPFileListProtocol()
        fullImagePath = self.saveDir+self.currentImage+".fits"
        print("Image to grab SaveImName:", serverImName)
        #self.ftp.list(".", fileList).addCallbacks(self.printFiles, self.ftpFail, callbackArgs=(fileList,))
        d = self.ftp.retrieveFile(serverImName, als.FileWriter(self.saveDir, self.currentImage+".fits"), offset=0).addCallbacks(self.ftpDone, self.ftpFail)
        return fullImagePath, d
        #shutil.copyfile(path + serverImName, self.saveDir + self.currentImage + ".fits")

    def printFiles(self, results, fileList):
        #print("MESSAGE:", results)
        for file in fileList.files:
            print('    %s: %d bytes, %s' \
              % (file['filename'], file['size'], file['date']))
        print('Total: %d files' % (len(fileList.files)))

    
    def ftpDone(self, msg):
        print("DONE Retrieving:", msg)
        
    def ftpFail(self, error):
        print("Failed retrieving file. Error was:")
        print(error)
        
    def copyImage(self, path, serverImName):
        """
        Pre: Takes in the diretory path to the original image file name as "path" as well as the 
             name of the orignal image as serverImName as strings.
        Post: The orignally created image is copied into a hard coded directory with the global
              current image name.  In the case of series images this current image name will be iterated.
              Returns nothing.
        """
        shutil.copyfile(path + serverImName, self.saveDir + self.currentImage + ".fits")

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
            name.split("_")
            if als.isInt(name[-1]):
                return True
            else:
                return False
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
        dialog = wx.TextEntryDialog(None, "Point to new directory.  Currently set to %s" % self.saveDir,
                                    "Set Save Directory", "%s" % self.saveDir, wx.OK | wx.CANCEL)
        answer = dialog.ShowModal()
        dialog.Destroy()
        
        if answer == wx.ID_OK:
            setTo = str(dialog.GetValue())
            
            if os.path.isdir(setTo):
                dialog = wx.MessageDialog(None, "Found directory!", "", wx.OK | wx.ICON_INFORMATION)
                dialog.ShowModal()
                dialog.Destroy()
                self.saveDir = setTo
                
                if self.saveDir[-1] != '/':
                    self.saveDir += "/"
                logger.debug("Directory: " + self.saveDir)
            else:
                dialog = wx.MessageDialog(None, "Directory not found please take a moment to create it and try again.",
                                          "", wx.OK | wx.ICON_INFORMATION)
                dialog.ShowModal()
                dialog.Destroy()

    def onStop(self, event):
        """
        Executes when the stop button is pressed.  Sends a command to Evora to stop exposing.
        """
        self.logFunction = self.logExposure
        logString = als.getLogString("abort", 'pre')
        self.log(self.logFunction, logString)

        d = self.protocol.sendCommand("abort")
        d.addCallback(self.abort_callback)
        
        if(self.timer.IsRunning()):
            self.timer.Stop()
            
        self.parent.parent.parent.expGauge.SetValue(0)
            
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
        self.exposeClass = self.parent.exposureInstance # give access to Exposure class variables

        ### Main Sizers
        self.vertSizer = wx.BoxSizer(wx.VERTICAL)
        self.horzSizer = wx.BoxSizer(wx.HORIZONTAL)

        #### Additianl Sub Sizers
        self.radioSizer = wx.BoxSizer(wx.HORIZONTAL)

        ### Widgets (specifially radio boxes)
        self.imageType = wx.RadioBox(self, id=2010, label="Image Type", size=wx.DefaultSize, \
                         choices=["Bias", "Flat", "Dark", "Object"], style=wx.RA_HORIZONTAL)
        self.exposeType = wx.RadioBox(self, id=2011, label = "Exposure Type", size=wx.DefaultSize, \
                          choices=["Single", "Real Time", "Series"], style=wx.RA_HORIZONTAL)

        ### Line up sub-chunks
        self.radioSizer.Add(self.imageType)
        als.AddLinearSpacer(self.radioSizer, 50)
        self.radioSizer.Add(self.exposeType)

        #### Line up big chuncks
        self.vertSizer.Add(self.radioSizer)

        ####

        ### Bindings
        self.Bind(wx.EVT_RADIOBOX, self.onImageType, id=2010)
        self.Bind(wx.EVT_RADIOBOX, self.onExposeType, id=2011)
        ###

        self.SetSizer(self.vertSizer)
        self.vertSizer.Fit(self)

    def onImageType(self, event):
        """
        When a new image type is selected this will write that type to the header on the next
        image that is exposed.
        """
        index = self.imageType.GetSelection()
        
        if index == 0:
            self.exposeClass.expValue.SetWindowStyle(wx.TE_READONLY)
            self.exposeClass.expValue.SetValue("0")
            
        else:
            self.exposeClass.expValue.SetWindowStyle(wx.TE_RICH)
            self.exposeClass.expValue.SetValue("")

        logger.info(self.imageType.GetStringSelection())

    def onExposeType(self, event):
        """
        When a new exposure type is selected this will write that type to the header on the next
        image that is exposed.
        """
        index = self.exposeType.GetSelection()
        
        if index == 1:
            self.exposeClass.nameField.SetWindowStyle(wx.TE_READONLY)
            self.exposeClass.nameField.SetValue("No name needed")
        else:
            
            self.exposeClass.nameField.SetWindowStyle(wx.TE_RICH)
            self.exposeClass.nameField.SetValue("")

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

        ### Main sizers
        self.vertSizer = wx.BoxSizer(wx.VERTICAL)
        self.horzSizer = wx.BoxSizer(wx.HORIZONTAL)

        #####

        ### Additional sub sizers
        self.tempSizer = wx.BoxSizer(wx.HORIZONTAL) # used for spacing tempText and tempValue
        self.buttonSizer = wx.BoxSizer(wx.HORIZONTAL) # used for spacing expose and stop buttons
        #####

        #### Widgets
        self.tempText = wx.StaticText(self, id=2030, label="Temperature (C)")
        self.tempValue = wx.TextCtrl(self, id=2031, size=(45, -1), style=wx.TE_PROCESS_ENTER)
        self.tempButton = wx.Button(self, id=2032, label="Cool", size=(60, -1))
        self.stopCool = wx.Button(self, id=2033, label="Stop", size=(60,-1))
        self.stopCool.Enable(False)
        self.tempBox = wx.StaticBox(self, id=2034, label="Temperature Controls", size=(100,100), style=wx.ALIGN_CENTER)
        self.tempBoxSizer = wx.StaticBoxSizer(self.tempBox, wx.VERTICAL)
        #####

        ##### Line up smaller sub sizers

        als.AddLinearSpacer(self.tempSizer, 10)
        self.tempSizer.Add(self.tempText, flag=wx.ALIGN_CENTER)
        als.AddLinearSpacer(self.tempSizer, 10)
        self.tempSizer.Add(self.tempValue, flag=wx.ALIGN_CENTER)
        als.AddLinearSpacer(self.tempSizer, 25)

        self.buttonSizer.Add(self.tempButton, flag=wx.ALIGN_CENTER)
        als.AddLinearSpacer(self.buttonSizer, 10)
        self.buttonSizer.Add(self.stopCool, 1, flag=wx.ALIGN_CENTER)


        ####

        #### Line up larger chunks with main sizer
        als.AddLinearSpacer(self.tempBoxSizer, 5)
        self.tempBoxSizer.Add(self.tempSizer, flag=wx.ALIGN_CENTER)
        als.AddLinearSpacer(self.tempBoxSizer, 5)
        self.tempBoxSizer.Add(self.buttonSizer, flag=wx.ALIGN_CENTER)
        als.AddLinearSpacer(self.tempBoxSizer, 15)
        self.vertSizer.Add(self.tempBoxSizer, flag=wx.ALIGN_CENTER)
        ####

        ### Variables
        self.tempToSend = ""

        ## Bindings
        self.Bind(wx.EVT_TEXT, self.getTemp, id=2031)
        self.Bind(wx.EVT_BUTTON, self.onCool, id=2032)
        self.Bind(wx.EVT_BUTTON, self.onStopCooling, id=2033)
        ##


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
        if als.isNumber(self.tempToSend): # Is temp a float?
            
            if float(self.tempToSend) >= -100.0 and float(self.tempToSend) <= -10.0: # Is it within the hardware bounds?

                logger.info(str(float(self.tempToSend)))
                self.logFunction = self.logTemp
                command = "setTEC " + str(int(self.tempToSend))
                
                if self.parent.exposureInstance.abort:
                    dialog = wx.MessageDialog(None, "Do you want to change temperature during exposure?", "", wx.OK | wx.CANCEL|wx.ICON_QUESTION)
                    answer = dialog.ShowModal()
                    dialog.Destroy()

                    if answer == wx.ID_OK:
                        
                        self.logFunction = self.logTemp
                        logString = als.getLogString(command, 'pre')
                        self.log(self.logFunction, logString)

                        d = self.protocol.sendCommand(command)
                        d.addCallback(self.cooling_callback)
                        
                        if not self.stopCool.IsEnabled():
                            self.stopCool.Enable(True)

                else:
                    
                    self.logFunction = self.logTemp
                    logString = als.getLogString(command, 'pre')
                    self.log(self.logFunction, logString)

                    d = self.protocol.sendCommand(command)
                    d.addCallback(self.cooling_callback)
                    
                    if not self.stopCool.IsEnabled():
                        self.stopCool.Enable(True)

            else:
                dialog = wx.MessageDialog(None, "Temperature is not within the bounds.", "", wx.OK|wx.ICON_ERROR)
                dialog.ShowModal()
                dialog.Destroy()

        else:
            dialog = wx.MessageDialog(None, "Temperature specified is not a number.", "", wx.OK|wx.ICON_ERROR)
            dialog.ShowModal()
            dialog.Destroy()

    def cooling_callback(self, msg):
        """
        Executes when the camera TEC temperature has been set.
        """
        self.logFunction = self.logTemp
        logString = als.getLogString("setTEC " + msg, 'post')
        self.log(self.logFunction, logString)
        logger.debug("Cooling to: " + msg)

    def onStopCooling(self, event):
        """
        When the stop cooling button is pressed this sends a command to Evora to warmup.
        """
        self.logFunction = self.logTemp
        logString = als.getLogString("warmup", 'pre')
        self.log(self.logFunction, logString)

        self.stopCool.Enable(False)
        d = self.protocol.sendCommand("warmup")
        d.addCallback(self.stopCooling_callback)

    def stopCooling_callback(self, msg):
        """
        Called when the server has completed its warmup routine.
        """
        self.logFunction = self.logTemp
        logString = als.getLogString("warmup " + msg, 'post')
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
        #print msg
        #print threading.current_thread().name
        temp = msg.split(",")[2]  #  parser sends stats on temperture where I grab that temp
        self.currTemp = float(temp)
        temp = str(int(round(float(temp))))
        mode = int(msg.split(",")[0])
        targetTemp = msg.split(",")[3]

        #self.parent.parent.parent.stats.SetStatusText("Current Temp:            " + temp + " C", 0)
        wx.CallAfter(self.parent.parent.parent.stats.SetStatusText, "      Temp: " + temp + " C", 0)
        
        ## based on temp change bitmap color
        # 20037 is NotReached
        # 20035 is NotStabalized
        # 20036 is Stabalized
        # 20034 is Off  
        
        if mode != 20034 and not self.stopCool.IsEnabled():
            logger.info("Enter")
            self.stopCool.Enable(True)
        #if self.prevMode is None or self.prevMode != mode:
            #print("MAKING NEW BITMAP")
        if mode == 20034 and float(temp) >= 0:
            bitmap = wx.StaticBitmap(self.parent.parent.parent.stats, -1, wx.Bitmap('greenCirc.png'))
        if mode == 20037 or (mode == 20034 and float(temp) < 0):
            bitmap = wx.StaticBitmap(self.parent.parent.parent.stats, -1, wx.Bitmap('redCirc.png'))
        if mode == 20035:
            bitmap = wx.StaticBitmap(self.parent.parent.parent.stats, -1, wx.Bitmap('yellowCirc.png'))
        if mode == 20036:
            bitmap = wx.StaticBitmap(self.parent.parent.parent.stats, -1, wx.Bitmap('blueCirc.png'))
        
        self.parent.parent.parent.stats.AddWidget(bitmap, pos=0, horizontalalignment=EnhancedStatusBar.ESB_ALIGN_LEFT,
                                                      verticalalignment=EnhancedStatusBar.ESB_ALIGN_BOTTOM)
         #   self.prevMode = mode
        
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

        self.watchFilterTime = 10  # every second when moving filter position
        self.targetFilter = None  # keep track globally of the target filter

        ### Main sizers
        self.vertSizer = wx.BoxSizer(wx.VERTICAL)

        ### Additional Sub-sizers
        self.filterSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.subVert = wx.BoxSizer(wx.VERTICAL)
        self.statusVert = wx.BoxSizer(wx.VERTICAL)
        self.buttonSizer = wx.BoxSizer(wx.HORIZONTAL)

        ## Variables
        self.filterNum, self.filterName = np.genfromtxt("filters.txt", dtype='str', usecols=[0,1], unpack=True)
        self.filterName = self.filterName.tolist()
        self.filterNum = self.filterNum.astype(int).tolist()
        self.filterMap = {}
        for i in range(len(self.filterName)):
            self.filterMap[self.filterName[i]] = self.filterNum[i]
        ##

        #### Widgets
        self.filterBox = wx.StaticBox(self, id=2040, label="Filter Controls", size=(100,100), style=wx.ALIGN_CENTER)
        self.filBoxSizer = wx.StaticBoxSizer(self.filterBox, wx.VERTICAL)

        self.statusBox = wx.StaticBox(self, id=2041, label="Filter Status", size=(150,150), style=wx.ALIGN_CENTER)
        self.statusBoxSizer = wx.StaticBoxSizer(self.statusBox, wx.VERTICAL)

        self.filterText = wx.StaticText(self, id=2042, label="Filter Type")
        self.filterMenu = wx.ComboBox(self, id=2043, choices=self.filterName, size=(60, -1), style=wx.CB_READONLY)
        self.filterButton = wx.Button(self, id=2044, label="Rotate", size=(70, -1))
        self.homeButton = wx.Button(self, id=2046, label="Home", size=(70,-1))
        self.statusBox = wx.TextCtrl(self, id=2045, style=wx.TE_READONLY|wx.TE_MULTILINE, size=(200,100))
        self.enableButtons(False)

        #### Line Up Smaller Sub Sizers

        self.filterSizer.Add(self.filterText, flag=wx.ALIGN_CENTER)
        als.AddLinearSpacer(self.filterSizer, 15)
        self.filterSizer.Add(self.filterMenu, flag=wx.ALIGN_CENTER)

        self.buttonSizer.Add(self.homeButton, flag=wx.ALIGN_CENTER)
        als.AddLinearSpacer(self.buttonSizer, 10)
        self.buttonSizer.Add(self.filterButton, flag=wx.ALIGN_CENTER)

        self.subVert.Add(self.filterSizer)
        als.AddLinearSpacer(self.subVert, 10)
        self.subVert.Add(self.buttonSizer, flag=wx.ALIGN_CENTER)


        self.filBoxSizer.Add((200, 10))
        self.filBoxSizer.Add(self.subVert, flag=wx.ALIGN_CENTER)
        self.filBoxSizer.Add((0,30))

        self.statusBoxSizer.Add(self.statusBox, flag=wx.ALIGN_CENTER)

        #### Line up larger chunks with main sizers
        self.vertSizer.Add(self.filBoxSizer)
        als.AddLinearSpacer(self.vertSizer, 15)
        self.vertSizer.Add(self.statusBoxSizer)

        ## Variables
        self.filterSelection = ""
        self.currFilterNum = None
        ##

        ## Bindings
        self.Bind(wx.EVT_COMBOBOX, self.onFilterSelection, id=2043)
        self.Bind(wx.EVT_BUTTON, self.onRotate, id=2044)
        self.Bind(wx.EVT_BUTTON, self.onHome, id=2046)
        ##

        self.SetSizer(self.vertSizer)
        self.vertSizer.Fit(self)

    def onFilterSelection(self, event):
        """
        Sets global filter selection when the user selects from the drop down menu.
        """
        self.filterSelection = self.filterMenu.GetValue()

        logger.debug("selection: " + self.filterSelection)

    def onRotate(self, event):
        """
        This method is called when the "Rotate To" button is pressed.  It is send a command to the Evora Server
        that will slew the filter appropriately.
        """ 
        if self.filterSelection is "":
            logger.info("No filter selected")
            
        else:
            logger.debug(str(type(self.filterSelection)))
            
            # send command to rotate to the specified position
            # find position
            pos = None
            for i in range(len(self.filterName)):
                if(str(self.filterSelection) == self.filterName[i]):
                    pos = self.filterNum[i]
            logger.debug("index: " + str(pos))

            self.targetFilter = pos
            self.watchFilterTime = 1.5 # set to one seconds
            self.watch = True

            self.logFunction = self.logFilter
            logString = als.getLogString("filter move " + str(self.filterName[pos]), 'pre')
            self.log(self.logFunction, logString)

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

        logString = als.getLogString("filter move " + msg, 'post')

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
        logString = als.getLogString("filter findPos None", 'post')
        self.log(self.logFunction, logString)

    def onHome(self, event):
        """
        Starts the homing sequence for the filter.
        """
        self.logFunction = self.logFilter
        logString = als.getLogString("filter home", 'pre')
        self.log(self.logFunction, logString)
        
        d = self.protocol2.sendCommand("home")
        d.addCallback(self.homingCallback)
        logger.info("homing...")

        self.enableButtons(False)

    def homingCallback(self, msg):
        self.logFunction = self.logFilter
        logString = als.getLogString("filter home " + msg, 'post')
        self.log(self.logFunction, logString)

        logger.debug("Done homing: " + msg)

        self.logFunction = self.logFilter
        logString = als.getLogString("filter getFilter", 'pre')
        self.log(self.logFunction, logString)

        d = self.protocol2.sendCommand("getFilter")
        d.addCallback(self.getFilterCallback)
        
        self.enableButtons(True)

    def getFilterCallback(self, msg):
        pos = int(msg)
        logger.debug("position: " + str(pos))
        filter = self.filterName[pos]

        self.logFunction = self.logFilter
        if self.targetFilter is not None and self.targetFilter != pos:
            logString = als.getLogString("filter getFilter report " + filter, 'post')
            self.log(self.logFunction, logString)
            
        # set drop down menu to the correct filter
        elif self.targetFilter == pos and self.adjusting:  # Kill the getFilter sequence when adjusting
            self.watch = False
            self.logFunction = self.logFilter
            logString = als.getLogString("filter getFilter finding " + filter + "," + str(pos), 'post')
            self.log(self.logFunction, logString)
            
            self.filterMenu.SetSelection(pos)
            self.filterSelection = str(self.filterMenu.GetValue())
            self.targetFilter = None
            
        else:
            self.watch = False
            self.logFunction = self.logFilter
            logString = als.getLogString("filter getFilter set " + filter + "," + str(pos), 'post')
            self.log(self.logFunction, logString)
            
            self.filterMenu.SetSelection(pos)
            self.filterSelection = str(self.filterMenu.GetValue())
            self.targetFilter = None
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

    def refreshList(self):
        """
        When "Refresh" is clicked in the filter sub-menu of the file menu this function is called.
        This method reads the filters.txt file and updates the GUI filter drop down menu while also resetting
        the internal variables that are used.  It returns nothing.
        """
        # clear the current GUI drop down filter menu
        self.filterMenu.Clear()

        # grab new filters in the assumed to be changed file
        newNum, newName = np.genfromtxt('filters.txt', dtype='str', usecols=[0,1], unpack=True)

        # update variables
        self.filterName = newName.tolist()
        self.filterNum = newNum.astype(int).tolist()
        self.filterMap = {}
        for i in range(len(newNum)):
            self.filterMap[newName[i]] = newNum[i]
        logger.debug(str(self.filterMap))
        
        # update GUI drop down filter menu
        for i in newName:
            self.filterMenu.Append(i)

    def sendToStatus(self, string):
        wx.CallAfter(self.threadSafeFilterStatus, string)

    def threadSafeFilterStatus(self, string):
        val = self.statusBox.GetValue()
        self.statusBox.SetValue(val + string + "\n")
        self.statusBox.SetInsertionPointEnd()

    def enableButtons(self, bool):
        self.filterButton.Enable(bool)
        self.homeButton.Enable(bool)

    def logFilter(self, logmsg):
        logger.info("logging from exposure class")
        self.sendToStatus(logmsg)
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
