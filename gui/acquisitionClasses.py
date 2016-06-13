#!/usr/bin/python2

from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import time
import wx  # get wxPython
import AddLinearSpacer as als  # get useful methods
import numpy as np  # get NumPy

# allows widgets to be inserted into wxPython status bar probably won't work on wxPython 3.x
import EnhancedStatusBar
#import threading
import thread
import shutil
#from FilterMotor import filtermotor

#### Class that handles widgets related to exposure
class Exposure(wx.Panel):
    """
    Creates the group of widgets that handle related exposure controls
    """

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.protocol = None  # gives access to the server protocol
        self.parent = parent  # gives access to the higher classes
        self.active_threads = []  # list of the acitve threading threads
        self.startTimer = 0  # keeps track of the timer count in ints
        self.endTimer = 0  # keeps track of the max timer count as an int

        self.abort = False  # tells you if the abort button is active
        self.realDeferal = None
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

        self.expValue = wx.TextCtrl(self, id=2003, size=(45, -1))
        self.expButton = wx.Button(self, id=2004, label="Expose", size=(60, -1))
        self.stopExp = wx.Button(self, id=2005, label="Abort", size=(60, -1))
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
        self.timeToSend = 0
        self.nameToSend = ""

        ### Bindings
        self.Bind(wx.EVT_TEXT, self.nameText, id=2002)  # bind self.nameField
        self.Bind(wx.EVT_TEXT, self.onExpTime, id=2003)  # bind self.expValue
        self.Bind(wx.EVT_BUTTON, self.onExpose, id=2004)  # bind self.expButton
        self.Bind(wx.EVT_BUTTON, self.onStop, id=2005)  # bind self.stopExp
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
        if als.isNumber(self.timeToSend):
            if(float(self.timeToSend) < 0):
                dialog = wx.MessageDialog(None, "Exposure time can not be less than 0...will not expose", "", wx.OK | wx.ICON_ERROR)
                dialog.ShowModal()
                dialog.Destroy()

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
        
        
        if als.isNumber(self.timeToSend) and self.nameToSend is not "":
            #self.protocol.sendLine("Exposing with name " + str(self.nameToSend) + " and time " + str(self.timeToSend) + " s")
            
            line = self.getAttributesToSend().split()

            # Set the correct log function that only prints to the log tab
            self.logFunction = self.logExposure
            
            # get image type
            imType = int(line[0])
            itime = float(line[3])
            """
            overwrite = True
            if(als.checkForFile("/data/copyfile/" + self.currentImage)):
            """

            #self.expButton.SetLabel("Abort")
            if(imType == 1):  # single exposure
                self.expButton.Enable(False)
                self.stopExp.Enable(True)
                self.abort = True
                line = " ".join(line[1:])  # bring all the parameters together
                d = self.protocol.sendCommand("expose " + line)
                d.addCallback(self.expose_callback_thread)
                thread.start_new_thread(self.exposeTimer, (itime,))

            if(imType == 2):  # real time exposure
                self.expButton.Enable(False)
                self.stopExp.Enable(True)
                self.abort = True
                line = " ".join(line[1:])
                # start callback that looks for a path leading to a real image
                d = self.protocol.addDeferred("realSent")
                d.addCallback(self.displayRealImage_thread)

                d = self.protocol.sendCommand("real " + line)
                d.addCallback(self.realCallback)  # this will clear the image path queue

                # start timer
                thread.start_new_thread(self.exposeTimer, (itime,))

            if(imType == 3):  # series exposure
                dialog = wx.TextEntryDialog(None, "How many exposure?", "Entry", "1", wx.OK | wx.CANCEL)
                answer = dialog.ShowModal()
                dialog.Destroy()
                if answer == wx.ID_OK:
                    self.seriesImageNumber = dialog.GetValue()
                    if(als.isInt(self.seriesImageNumber)):
                        print("Number of image to be taken:", int(self.seriesImageNumber))
                        self.expButton.Enable(False)
                        self.stopExp.Enable(True)
                        self.abort = True

                        line[2] = self.seriesImageNumber
                        line = " ".join(line[1:])
                        
                        # set up all callbacks for series
                        for i in range(int(self.seriesImageNumber)):
                            d = self.protocol.addDeferred("seriesSent" + str(i+1))
                            d.addCallback(self.displaySeriesImage_thread)

                        d = self.protocol.sendCommand("series " + str(line))
                        d.addCallback(self.seriesCallback)
                        
                        # start timer
                        thread.start_new_thread(self.exposeTimer, (itime,))

                    else:
                        dialog = wx.MessageDialog(None, "Entry was not a valid integer!", "", wx.OK | wx.ICON_ERROR)
                        dialog.ShowModal()
                        dialog.Destroy()
            

    def exposeTimer(self, time):
        # get exposure time 
        expTime = float(time) + 0.2
        
        # get the max range for progress bar
        self.endTimer = int(expTime / (10.0*10**-3)) # timer will update every 10 ms
        
        # set exposure progress bar range
        self.parent.parent.parent.expGauge.SetRange(self.endTimer)

        # start timer
        self.timer.Start(10) # 10 millisecond intervals

    def onExposeTimer(self, event):
        if(self.startTimer == self.endTimer - 1):
            self.timer.Stop()
            self.startTimer = 0
        else:
            # get gauge value
            val = self.parent.parent.parent.expGauge.GetValue()
            wx.CallAfter(self.parent.parent.parent.expGauge.SetValue, (val + 1))
            self.startTimer += 1

    def expose_callback_thread(self, msg):
        thread.start_new_thread(self.exposeCallback, (msg,))

    def exposeCallback(self, msg):
        ### May need to thread to a different method if to slow
        results = msg.split(",")

        # immediatly reset button
        self.abort = False
        self.expButton.Enable(True)
        if(self.stopExp.IsEnabled()):
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

        print(self.parent.parent.parent.imageOpen)
        print("opened window")

        if(success == 1):
            # get name of image and path
            filePath = results[1].split("/")
            name = filePath[-1].rstrip()
            path = ""
            for i in filePath[:-1]:
                path += i + "/"
            # get time sent to server
            time = float(results[2])
                
            print(path, name)

            # get data
            data = als.getData(path+name)
            stats_list = als.calcStats(data)

            # change the gui with thread safety
            wx.CallAfter(self.safePlot, data, stats_list)

            # copy file to different folder
            self.copyImage(path, name)

            # log the status
            logstr = self.currentImage + "exposed with %.2f sec" % time
            self.log(self.logFunction, logstr)
        else:
            print("Successfully Aborted")
            pass

    def safePlot(self, data, stats_list):
        if(not self.parent.parent.parent.imageOpen):
            # create new window
            self.parent.parent.parent.openImage("manual open")
        else:
            self.parent.parent.parent.window.panel.clear()
            self.parent.parent.parent.window.resetWidgets()

        self.parent.parent.parent.window.panel.updatePassedStats(stats_list)
        self.parent.parent.parent.window.panel.plotImage(data, 6.0, 'gray')
        self.parent.parent.parent.window.panel.updateScreenStats()
        self.parent.parent.parent.window.panel.refresh()

    def displayRealImage_thread(self, msg):
        thread.start_new_thread(self.displayRealImage, (msg,))

    def displayRealImage(self, msg):
        path = msg
        # no abort then display the image
        if self.abort:
            # add a new deffered object
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

            thread.start_new_thread(self.exposeTimer, (self.timeToSend,))

    def displayRealImage_callback_thread(self, msg):
        print("From real image callback thread:", repr(msg))
        msg = msg.rstrip()
        thread.start_new_thread(self.displayRealImage_callback, (msg,))

    def displayRealImage_callback(self, msg):
        path = msg  # path to image (/tmp/image_date.fits)

        if(msg != "None"):
                        # get data
            data = als.getData(path)
            stats_list = als.calcStats(data)
            # change the gui with thread safety
            wx.CallAfter(self.safePlot, data, stats_list)

    def realCallback(self, msg):
        self.protocol.removeDeferred("realSent")
        print("Completed real time series with exit:", msg)

    def displaySeriesImage_thread(self, msg):
        print("From real image callback thread:", repr(msg))
        msg = msg.rstrip()
        thread.start_new_thread(self.displaySeriesImage, (msg,))

    def displaySeriesImage(self, msg):
        msg = msg.split(",")

        imNum = int(msg[0])
        print(type(imNum))
        time = float(msg[1])
        path = msg[2]

        fullPath = path.split("/")
        name = fullPath[-1].rstrip()
        directory = ""
        for i in fullPath[:-1]:
            directory += i + "/"

        print("Got:", msg)
        # no abort then display the image
        if(imNum <= int(self.seriesImageNumber)):
            print("Entered to display series image")

            if(self.timer.IsRunning()):
                self.timer.Stop()

            self.parent.parent.parent.expGauge.SetValue(self.endTimer)

            # get stats
            data = als.getData(path)
            stats_list = als.calcStats(data)
            # change the gui with thread safety
            wx.CallAfter(self.safePlot, data, stats_list)
            
            # copy image over (counter looks like "_XXX.fits")
            print("current image name:", self.currentImage)
            print(self.checkForImageCounter(self.currentImage))
            if(not self.checkForImageCounter(self.currentImage)):
                self.currentImage += "_001"
                print("entered")
            else:
                self.iterateImageCounter(self.currentImage)
            #print(self.iterateImageCounter)
            self.copyImage(directory, name)

            logstr = self.currentImage + "exposed with %.2f sec" % time
            self.log(self.logFunction, logstr)

            self.parent.parent.parent.expGauge.SetValue(0)
            self.startTimer = 0

            if(self.seriesImageNumber is not None):
                if(imNum < int(self.seriesImageNumber)):
                    thread.start_new_thread(self.exposeTimer, (time,))

    def seriesCallback(self, msg):
        msg = msg.split(",")
        exitNumber = int(msg[1])  # server will send which count the series loop ended on
        if(exitNumber <= int(self.seriesImageNumber)):
            for i in range(exitNumber, int(self.seriesImageNumber) + 1):
                key = "seriesSent" + str(i)
                self.protocol.removeDeferred(key)
        # reset series image number
        #self.seriesImageNumber = None
        print(self.protocol._deferreds)
        
        self.abort = False
        self.expButton.Enable(True)
        if(self.stopExp.IsEnabled()):
            self.stopExp.Enable(False)
        # stop timer if running
        if(self.timer.IsRunning()):
            self.timer.Stop()

        # finish out the gauge
        self.parent.parent.parent.expGauge.SetValue(self.endTimer)

        # restart gauge and the timer count
        self.parent.parent.parent.expGauge.SetValue(0)
        self.startTimer = 0

        print("Completed real time series with exit:", msg)

    def abort_callback(self, msg):
        self.parent.parent.parent.expGauge.SetValue(0)  # redundancy to clear the exposure gauge
        logstr = "aborted acquisitioning"
        self.log(self.logFunction, logstr)
        print("Aborted", msg)

    def openData(self, path, name):
        print("opening")
        self.parent.parent.parent.expGauge.SetValue(0)
        
        print(self.parent.parent.parent.imageOpen)
        # open image window 
        if(not self.parent.parent.parent.imageOpen):
            # create new window
            self.parent.parent.parent.openImage("manual open")
        print("opened window")

        self.parent.parent.parent.window.panel.clear()
        data = self.parent.parent.parent.window.panel.getData(path+name)
        print("got data")
        self.parent.parent.parent.window.panel.plotImage(data, 6.0, 'gray')
        print("plotted")
        self.parent.parent.parent.window.panel.updateScreenStats()
        self.parent.parent.parent.window.panel.refresh()

    def getAttributesToSend(self):
        # get binning type
        binning = self.parent.parent.parent.binning

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
        
        # set the global current image name
        #name = str(self.nameToSend)
        self.currentImage = self.nameToSend

        #line = "expose" # this is given beforet the command is sent off
        line = str(exposeType)
        line += " " + str(imageType).lower()
        line += " " + str(expNum) # This is the exposure number.  Should have dialog come up for when set to series to take in the number of exposures 
        line += " " + str(self.timeToSend)
        line += " " + str(binning)

        return line

    def logExposure(self, logmsg):
        print("logging from exposure class")
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
        print("entered log")
        logfunc(logmsg)


    def copyImage(self, path, serverImName):
        """
        Pre: Takes in the diretory path to the original image file name as "path" as well as the 
             name of the orignal image as serverImName as strings.
        Post: The orignally created image is copied into a hard coded directory with the global
              current image name.  In the case of series images this current image name will be iterated.
              Returns nothing.
        """
        shutil.copyfile(path + serverImName, "/data/copydata/" + self.currentImage + ".fits")

    def checkForImageCounter(self, name):
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
            if(als.isInt(name[-1])):
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
        if(count < 10):
            temp[-1] = "00" + str(count)
        elif(count < 100):
            temp[-1] = "0" + str(count)
        else:
            temp[-1] = str(count)
        self.currentImage = "_".join(temp[:])
        print("Iterated to: " + self.currentImage)
        

    def onStop(self, event):
        """
        Executes when the stop button is pressed.  Sends a command to Evora to stop exposing.
        """
        d = self.protocol.sendCommand("abort")
        d.addCallback(self.abort_callback)
        
        if(self.timer.IsRunning()):
            self.timer.Stop()
        self.parent.parent.parent.expGauge.SetValue(0)
            
        self.expButton.Enable(True)
        self.stopExp.Enable(False)
        self.abort = False

        print("Stop Exposure")

    def joinThreads(self):
        for t in self.active_threads:
            t.join()

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
        image that is exposed.n
        """
        index = self.imageType.GetSelection()
        print(self.imageType.GetStringSelection())

    def onExposeType(self, event):
        """
        When a new exposure type is selected this will write that type to the header on the next
        image that is exposed.
        """
        index = self.exposeType.GetSelection()
        print(self.exposeType.GetStringSelection())


class TempControl(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.protocol = None
        self.parent = parent
        self.isConnected = False

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
        self.tempToSend = self.tempValue.GetValue()

    def onCool(self, event):
        if als.isNumber(self.tempToSend):
            if(float(self.tempToSend) >= -80.0 and float(self.tempToSend) <= -10.0):
                print(float(self.tempToSend))
                if self.parent.exposureInstance.abort:
                    dialog = wx.MessageDialog(None, "Do you want to changing temperature during exposure?", "", wx.OK | wx.CANCEL|wx.ICON_QUESTION)
                    answer = dialog.ShowModal()
                    dialog.Destroy()

                    if answer == wx.ID_OK:
                        d = self.protocol.sendCommand("setTEC " + str(int(self.tempToSend)))
                        d.addCallback(self.cooling_callback)
                        if(not self.stopCool.IsEnabled()):
                            self.stopCool.Enable(True)
                else:
                    d = self.protocol.sendCommand("setTEC " + str(int(self.tempToSend)))
                    d.addCallback(self.cooling_callback)
                    if(not self.stopCool.IsEnabled()):
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
        print("Cooling to:", msg)

    def onStopCooling(self, event):
        """
        When the stop cooling button is pressed this sends a command to Evora to warmup.
        """
        self.stopCool.Enable(False)
        d = self.protocol.sendCommand("warmup")
        d.addCallback(self.stopCooling_callback)

    def stopCooling_callback(self, msg):
        print("Warmed with exit:", msg)
        

    def changeTemp(self, value, statusbar):
        """
        Changes the temperature status in the status bar.
        """
        bitmap = wx.StaticBitmap(statusbar, size=(50,50))
        bitmap.SetBitmap(wx.ArtProvider.GetBitmap("ID_YES"))
        statusbar.AddWidget(bitmap, pos=0, horizontalalignment=EnhancedStatusBar.ESB_ALIGN_LEFT)

    def watchTemp(self):
        
        # create an infinite while loop
        while self.isConnected:
            d = self.protocol.sendCommand("temp")
            d.addCallback(self.callbackTemp_thread)
            #  put thread to sleep; on wake up repeats
            time.sleep(10)

    def callbackTemp_thread(self, msg):
        thread.start_new_thread(self.callbackTemp, (msg,))

    def callbackTemp(self, msg):
        #print msg
        #print threading.current_thread().name
        temp = msg.split(",")[2]  #  parser sends stats on temperture where I grab that temp
        temp = str(int(round(float(temp))))
        mode = int(msg.split(",")[0])
        targetTemp = msg.split(",")[3]
        
        #self.parent.parent.parent.stats.SetStatusText("Current Temp:            " + temp + " C", 0)
        wx.CallAfter(self.parent.parent.parent.stats.SetStatusText, "Current Temp:            " + temp + " C", 0)
        
        ## based on temp change bitmap color
        # 20037 is NotReached
        # 20035 is NotStabalized
        # 20036 is Stabalized
        # 20034 is Off  
        if(mode != 20034 and not self.stopCool.IsEnabled()):
            self.stopCool.Enable(True)

        if(mode == 20034 and float(temp) >= 0):
            bitmap = wx.StaticBitmap(self.parent.parent.parent.stats, -1, wx.Bitmap('greenCirc.png'), size=(90,17))
        if(mode == 20037 or (mode == 20034 and float(temp) < 0)):
            bitmap = wx.StaticBitmap(self.parent.parent.parent.stats, -1, wx.Bitmap('redCirc.png'), size=(90,17))
        if(mode == 20035):
            bitmap = wx.StaticBitmap(self.parent.parent.parent.stats, -1, wx.Bitmap('yellowCirc.png'), size=(90,17))
        if(mode == 20036):
            bitmap = wx.StaticBitmap(self.parent.parent.parent.stats, -1, wx.Bitmap('blueCirc.png'), size=(90,17))
        
        #self.parent.parent.parent.stats.AddWidget(bitmap, pos=0, horizontalalignment=EnhancedStatusBar.ESB_ALIGN_RIGHT)
        wx.CallAfter(self.parent.parent.parent.stats.AddWidget, bitmap, pos=0, horizontalalignment=EnhancedStatusBar.ESB_ALIGN_RIGHT)
 

class FilterControl(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        # global variables
        self.protocol = None

        ### Main sizers
        self.vertSizer = wx.BoxSizer(wx.VERTICAL)

        ### Additional Sub-sizers
        self.filterSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.subVert = wx.BoxSizer(wx.VERTICAL)
        self.statusVert = wx.BoxSizer(wx.VERTICAL)

        ## Variables
        self.filterNum, self.filterName = np.genfromtxt("filters.txt", dtype='str', usecols=[0,1], unpack=True)
        self.filterName = self.filterName.tolist()
        self.filterNum = self.filterNum.astype(int).tolist()
        self.filterMap = {}
        for i in range(len(self.filterName)):
            self.filterMap[self.filterName[i]] = self.filterNum[i]
        print(self.filterMap)
        ##

        #### Widgets
        self.filterBox = wx.StaticBox(self, id=2040, label = "Filter Controls", size=(100,100), style=wx.ALIGN_CENTER)
        self.filBoxSizer = wx.StaticBoxSizer(self.filterBox, wx.VERTICAL)

        self.statusBox = wx.StaticBox(self, id=2041, label = "Filter Status", size=(150,150), style=wx.ALIGN_CENTER)
        self.statusBoxSizer = wx.StaticBoxSizer(self.statusBox, wx.VERTICAL)

        self.filterText = wx.StaticText(self, id=2042, label="Filter Type")
        self.filterMenu = wx.ComboBox(self, id=2043, choices=self.filterName, size=(50, -1), style=wx.CB_READONLY)
        self.filterButton = wx.Button(self, id=2044, label = "Rotate To")
        self.statusBox = wx.TextCtrl(self, id=2045, style=wx.TE_READONLY|wx.TE_MULTILINE, size=(200,100))


        #### Line Up Smaller Sub Sizers

        self.filterSizer.Add(self.filterText, flag=wx.ALIGN_CENTER)
        als.AddLinearSpacer(self.filterSizer, 15)
        self.filterSizer.Add(self.filterMenu, flag=wx.ALIGN_CENTER)

        self.subVert.Add(self.filterSizer)
        als.AddLinearSpacer(self.subVert, 10)
        self.subVert.Add(self.filterButton, flag=wx.ALIGN_CENTER)


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
        ##

        self.SetSizer(self.vertSizer)
        self.vertSizer.Fit(self)

    def onFilterSelection(self, event):
        self.filterSelection = self.filterMenu.GetValue()
        try:
            self.currFilterNum = self.filterNum[self.filterSelection]
        except KeyError:
            print("not a filter")
        

    def onRotate(self, event):
        """
        This method is called when the "Rotate To" button is pressed.  It is send a command to the Evora Server
        that will slew the filter appropriately.
        """ 
        if self.filterSelection is "":
            print("No filter selected")
        else:
            print(type(self.filterSelection))
            # send command to rotate to the specified position

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
        print(self.filterMap)
        
        # update GUI drop down filter menu
        for i in newName:
            self.filterMenu.Append(i)
