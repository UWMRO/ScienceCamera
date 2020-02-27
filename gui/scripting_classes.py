#!/usr/bin/python2

from __future__ import print_function, division, absolute_import

import wx
import thread
import fits_utils
import gui_elements as gui
import log_utils


class ScriptStatus(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        # Main Sizer
        self.vertSizer = wx.BoxSizer(wx.VERTICAL)

        # Widgets
        self.statusBox = wx.StaticBox(self, label="Script Activity", size=(400, 150))
        self.statusBoxSizer = wx.StaticBoxSizer(self.statusBox, wx.VERTICAL)

        self.activityText = wx.TextCtrl(self, style=wx.TE_READONLY | wx.TE_MULTILINE,
                                        size=(400, 150))

        # adjust subsizers
        self.statusBoxSizer.Add(self.activityText, flag=wx.ALIGN_CENTER)

        # adjust main sizers
        self.vertSizer.Add(self.statusBoxSizer, flag=wx.ALIGN_CENTER)

        self.SetSizer(self.vertSizer)
        self.vertSizer.Fit(self)


class ScriptCommands(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        # Global variables
        self.parent = parent
        self.protocol = None

        # Main Sizer
        self.vertSizer = wx.BoxSizer(wx.VERTICAL)

        # subsizers
        self.subVert = wx.BoxSizer(wx.VERTICAL)
        self.buttonSizer = wx.BoxSizer(wx.HORIZONTAL)

        # Widgets
        self.commandFrame = wx.StaticBox(self, id=3000, label="Command Prompt", size=(350, 50))
        self.commandFrameSizer = wx.StaticBoxSizer(self.commandFrame, wx.VERTICAL)

        self.button = wx.Button(self, id=3001, label="OK")  # for entering command prompt
        self.upButton = wx.Button(self, id=3002, label="Upload")
        self.button.Enable(False)
        self.upButton.Enable(False)
        self.commandBox = wx.TextCtrl(self, id=3003, size=(350, -1), style=wx.TE_PROCESS_ENTER | wx.TE_READONLY)

        # adjust subsizers
        self.buttonSizer.Add(self.button, flag=wx.ALIGN_CENTER)
        gui.AddLinearSpacer(self.buttonSizer, 10)
        self.buttonSizer.Add(self.upButton, flag=wx.ALIGN_CENTER)

        self.subVert.Add(self.commandBox, flag=wx.ALIGN_CENTER)
        gui.AddLinearSpacer(self.subVert, 15)
        self.subVert.Add(self.buttonSizer, flag=wx.ALIGN_CENTER)

        self.commandFrameSizer.Add(self.subVert, flag=wx.ALIGN_CENTER)

        # adjust main sizers
        self.vertSizer.Add(self.commandFrameSizer, flag=wx.ALIGN_CENTER)

        # Variables
        self.command = ""

        # Bindings
        self.Bind(wx.EVT_TEXT, self.getCommand, id=3003)
        # self.Bind(wx.EVT_TEXT_ENTER, self.onOk, id=3003)
        self.Bind(wx.EVT_BUTTON, self.onOk, id=3001)
        self.Bind(wx.EVT_BUTTON, self.onUpload, id=3002)
        ##

        self.SetSizer(self.vertSizer)
        self.vertSizer.Fit(self)

    def getCommand(self, event):
        self.command = self.commandBox.GetValue()
        self.button.SetDefault()

    def onOk(self, event):
        """
        Once a command has been inputed to the command prompt
        """
        self.button.SetFocus()
        if self.command is "":
            print("No command")
        else:
            # print(self.command)
            runList = self.parseCommand(self.command)  # parses user command
            self.executeCommand(runList)  # executes user command

    def onUpload(self, event):
        print("Upload your script")

    def sendToStatus(self, string):
        send = log_utils.time_stamp()
        send += " " + string
        wx.CallAfter(self.threadSafeScriptingStatus, send)

    def threadSafeScriptingStatus(self, string):
        val = self.parent.scriptStatus.activityText.GetValue()
        self.parent.scriptStatus.activityText.SetValue(val + string + "\n")
        self.parent.scriptStatus.activityText.SetInsertionPointEnd()

    def logScript(self, logmsg):
        """
        Pre: Pass in a message to be logged.
        Post: Sends log message to status box as well as logs to file.
        """
        print("logging from scripting class")
        self.sendToStatus(logmsg)
        logInstance = self.parent.parent.parent.log.logInstance
        wx.CallAfter(logInstance.threadSafeLogStatus, logmsg)

    def executeCommand(self, runList):
        """
        This will take the known order of runList from the command and then send it to the server
        while also displaying pertanent information.  It will essentially be reusing methods,
        whenever possible from the acquisitionClasses.py file.
        Returns: Nothing is returned through this method.
        """

        val = self.parent.scriptStatus.activityText.GetValue()
        print(val)

        if type(runList) == list:
            self.parent.scriptStatus.activityText.SetValue(val + str(runList) + "\n")
            self.parent.scriptStatus.activityText.SetInsertionPointEnd()

            print(runList)
            print("sending command")

            # surround in str to get rid of unicode, otherwise fails at sending
            sendCommand = str(runList[0])
            if sendCommand == 'series':
                imtype = str(runList[1])
                number = str(runList[2])

                exposeClass = self.parent.parent.parent.takeImage.exposureInstance
                exposeClass.seriesImageNumber = int(number)
                exposeClass.logFunction = self.logScript  # point to the correct log function that prints to log tab and script status

                # example runList (['series', 'bias', int(number), 'basename'])
                if imtype == 'bias':

                    basename = str(runList[3])
                    exposeClass.currentImage = basename
                    overwrite = None
                    if fits_utils.check_for_file("/data/copyfile/" + self.currentImage + "_001.fits"):
                        dialog = wx.MessageDialog(None, "Do you want to change temperature during exposure?", "", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
                        overwrite = dialog.ShowModal()
                        dialog.Destroy()

                    if overwrite is not None or overwrite == wx.ID_OK:
                        d = self.protocol.addDeferred("seriesSent")
                        d.addCallback(exposeClass.displaySeriesImage_thread)

                        d = self.protocol.sendCommand(sendCommand + " " + imtype + " " + number +
                                                      " 0 " + str(self.parent.parent.parent.binning))
                        d.addCallback(exposeClass.seriesCallback)

                        # start timer
                        thread.start_new_thread(exposeClass.exposeTimer, (0,))

                if imtype in ['flat', 'object', 'dark']:
                    exposeClass.expButton.Enable(False)
                    exposeClass.stopExp.Enable(True)
                    exposeClass.abort = True

                    itime = str(runList[3])
                    basename = str(runList[4])
                    exposeClass.currentImage = basename

                    overwrite = None
                    if fits_utils.check_for_file("/data/copyfile/" + self.currentImage + "_001.fits"):
                        dialog = wx.MessageDialog(None, "Do you want to change temperature during exposure?", "", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
                        overwrite = dialog.ShowModal()
                        dialog.Destroy()

                    if overwrite is not None or overwrite == wx.ID_OK:
                        for i in range(int(number)):
                            d = self.protocol.addDeferred("seriesSent" + str(i+1))
                            d.addCallback(exposeClass.displaySeriesImage_thread)

                        d = self.protocol.sendCommand(sendCommand + " " + imtype + " " + number + " " + itime + " " + str(self.parent.parent.parent.binning))
                        d.addCallback(exposeClass.seriesCallback)
                        # start timer
                        thread.start_new_thread(exposeClass.exposeTimer, (float(itime),))

            if sendCommand == 'abort':
                exposeClass = self.parent.parent.parent.takeImage.exposureInstance
                exposeClass.onStop(None)

            if sendCommand == 'expose' and runList[1] == 'help':
                # report on all the help options
                helpString = ""
                if runList[2] == 'abort':
                    helpString += "\"expose abort\" is used to stop the current exposure.  This can be "\
                                + "an exposure started through the imaging or scripting tab. Invoke with "\
                                + "\"expose abort\"."
                if runList[2] == 'bias':
                    helpString += "\"expose bias\" is used to take a number of biases in one command. Invoke this "\
                               + "command with \"expose bias arg1 arg2\", where arg1 and arg2, in no particular "\
                               + "order, are time=XX in seconds and basename=imagename."
                if runList[2] == 'dark':
                    helpString += "\"expose dark\" is used to take a number of darks in one command. Invoke this "\
                               + "command with \"expose dark arg1 arg2 arg3\", where arg1, arg2, and arg3, in no particular "\
                               + "order, are time=XX in seconds, number=XX as an int, and basename=imagename."
                if runList[2] == 'flat':
                    helpString += "\"expose flat\" is used to take a number of darks in one command. Invoke this "\
                               + "command with \"expose flat arg1 arg2 arg3\", where arg1, arg2, and arg3, in no particular "\
                               + "order, are time=XX in seconds, number=XX as an int, and basename=imagename."
                if runList[2] == 'object':
                    helpString += "\"expose object\" is used to take a number of darks in one command. Invoke this "\
                               + "command with \"expose object arg1 arg2 arg3\", where arg1, arg2, and arg3, in no particular "\
                               + "order, are time=XX in seconds, number=XX as an int, and basename=imagename."
                self.sendToStatus(helpString)

            # Deal with set commands
            # command: set temp XX
            if sendCommand == 'setTEC':
                temp = int(runList[1])
                tempClass = self.parent.parent.parent.takeImage.tempInstance
                tempClass.tempToSend = temp
                tempClass.onCool(None)

            # command: set temp warmup
            if sendCommand == 'warmup':
                tempClass = self.parent.parent.parent.takeImage.tempInstance
                tempClass.onStopCooling(None)

            # command: set filter X
            if sendCommand == 'set':
                if runList[1] == 'filter':
                    pos = int(runList[2])

            # command: set binning X
            if sendCommand == 'set':
                if runList[1] == 'binning':
                    topInstance = self.parent.parent.parent
                    bin = str(runList[2])
                    if bin == '1':
                        topInstance.on1x1(None)
                        file = topInstance.menuBar.GetMenu(0)
                        file.FindItemById(1120).Check(check=True)
                    else:
                        topInstance.on2x2(None)
                        file = topInstance.menuBar.GetMenu(0)
                        file.FindItemById(1121).Check(check=True)

            # command: set help binning
            #          set help temp
            #          set help filter
            if sendCommand == 'set':
                if runList[1] == 'help':
                    if runList[2] == 'binning':
                        helpBinning = "\"set binning\" is used to set the binning type of the CCD. To invoke use the following "\
                                      + "command: \"set binning arg1\", where arg1 is the binning type of 1 or 2."
                        self.sendToStatus(helpBinning)
                    if runList[2] == 'temp':
                        helpTemp = "\"set temp\" is used to set the temperature of the CCD. To invoke use the following "\
                                   + "command: \"set temp arg1\", where arg1 is an int between -80 to -10 "\
                                   + "or warmup."
                        self.sendToStatus(helpTemp)
                    if runList[2] == 'filter':
                        helpFilter = "\"set filter\" is used to set the filter wheel position. To invoke use the following "\
                                     + "command: \"set filter arg1\", where arg1 is an int between 1 and 6."
                        self.sendToStatus(helpFilter)
            # command: help expose
            #          help set
            #          help filter
            if sendCommand == 'help':
                if runList[1] == 'expose':
                    helpExpose = "\"expose\" command is explicitely for taking several images in one command. "
                    helpExpose += "This is invoked by typing \"expose imageType\" where imageType is either "
                    helpExpose += "bias, dark, flat, or object. Use \"expose help\" followed by image type to "
                    helpExpose += "see what arguments are needed (e.g. \"expose help bias\")."
                    self.sendToStatus(helpExpose)

                if runList[1] == 'set':
                    helpSet = "\"set\" command is used to set the camera attributes of binning, temperature, and "
                    helpSet += "filter position.  Use \"set help\" followed by one of the attributes (binning, temp, "
                    helpSet += "filter) to get info on the need arguements (e.g. \"set help temp\")."
                    self.sendToStatus(helpSet)
                if runList[1] == 'filter':
                    helpFilter = "\"filter\" command is used to control the filter attributes."
                    self.sendToStatus(helpFilter)
        else:
            print("something went wrong")
            print(runList)
            dialog = wx.MessageDialog(None, runList, "", wx.OK | wx.ICON_ERROR)
            dialog.ShowModal()
            dialog.Destroy()
        self.commandBox.SetFocus()

    def parseCommand(self, command):
        """
        This method parses the command inputed by the user from the command promp text control box.
        If the command is good it will return a list with the command that is sent to the server
        followed by the necessary arguments.  If the command is bad then a string is sent back that
        will be displayed to the user about what went wrong.  For any help commands this is delt with
        outside the parser.
        """
        scriptLine = command.split()
        print(scriptLine)

        command = None
        subcommand = None

        commandList = ['expose', 'filter', 'help', 'set']
        exposeSub = ['abort', 'bias', 'dark', 'flat', 'object', 'help']
        filterSub = ['home', 'status', 'help']
        helpSub = ['expose', 'filter', 'set']
        setSub = ['binning', 'filter', 'temp', 'warmup', 'help']

        runList = []  # first entry is the command to send the next entries depend on the command being sent
        try:
            command = scriptLine[0]
            subcommand = scriptLine[1]
        except IndexError:
            return "ERROR: command and/or subcommand not given..."
        else:
            if command in commandList:

                # Possible commands (the order of time=X.X, basename=somename, and number=XX is ambiguous)
                # expose abort
                # expose bias basename=bias number=XX
                # expose dark time=X.X basename=dark number=XX
                # expose flat time=X.X basename=flat number=XX
                # expose object time=X.X basename=object number=XX
                # expose help abort
                # expose help bias
                # expose help dark
                # expose help flat
                # expose help object
                if command == "expose":

                    if subcommand in exposeSub:
                        if subcommand == 'abort':
                            runList.append("abort")  # only command to send
                            return(runList)
                        elif subcommand == 'bias':
                            print("exposing of this type")
                            try:
                                arg1 = scriptLine[2]
                                arg2 = scriptLine[3]
                            except IndexError:
                                return "ERROR: no basename or number arguements..."
                            else:
                                if len(scriptLine[0:]) > 4:
                                    return "ERROR: too many arguments given in \"expose bias\"..."
                                arg1 = arg1.split("=")
                                arg2 = arg2.split("=")
                                argDict = {}
                                print(arg1, arg2)

                                if ((len(arg1) == 2 and (arg1[0] in ['basename', 'number'])) and
                                   (len(arg2) == 2 and (arg2[0] in ['basename', 'number']))):
                                    # map arguements to be able to call them in order
                                    argDict[arg1[0]] = arg1[1]
                                    argDict[arg2[0]] = arg2[1]

                                    if argDict['number'].isdigit():
                                        if int(argDict['number']) > 0:
                                            if argDict['basename'].strip() is not "":
                                                # final stop; everything has been checked so now we build up the list to return
                                                runList.append('series')
                                                runList.append(subcommand)
                                                runList.append(int(argDict['number']))
                                                runList.append(argDict['basename'])
                                                print("The specified number of exposures is", float(argDict['number']))
                                                return runList  # [series, bias, number, basename]
                                            else:
                                                return "ERROR: basename specified is empty..."
                                        else:
                                            return "ERROR: number of exposures needs to be above 0..."
                                    else:
                                        return "ERROR: specified number of exposures is not number..."
                                else:
                                    return "SyntaxError: basename or number of exposures is incorrectly specified..."

                        elif subcommand in ['dark', 'flat', 'object']:
                            print("exposing of this type")
                            try:
                                arg1 = scriptLine[2]
                                arg2 = scriptLine[3]
                                arg3 = scriptLine[4]
                            except IndexError:
                                return "ERROR: no time, basename, and/or exposure number given..."
                            else:
                                if len(scriptLine[0:]) > 5:
                                    return "ERROR: too many arugments given in \"expose (dark/flat/object)\""

                                arg1 = arg1.split("=")
                                arg2 = arg2.split("=")
                                arg3 = arg3.split("=")
                                argDict = {}
                                print(arg1, arg2, arg3)
                                # Makes sure that when args are split by equals that there are two entries and that the first one is
                                # either time or basename.
                                if ((len(arg1) == 2 and (arg1[0] in ['time', 'basename', 'number'])) and
                                   (len(arg2) == 2 and (arg2[0] in ['time', 'basename', 'number'])) and
                                   (len(arg3) == 2 and (arg3[0] in ['time', 'basename', 'number']))):
                                    # map arguments to be able to call them in order
                                    argDict[arg1[0]] = arg1[1]
                                    argDict[arg2[0]] = arg2[1]
                                    argDict[arg3[0]] = arg3[1]

                                    if argDict['time'].isnumeric() and argDict['number'].isdigit():
                                        # final stop; everything has been checked so now we build up the list to return
                                        if float(argDict['time']) >= 0 or int(argDict['number']) > 0:
                                            if argDict['basename'].strip() is not "":
                                                runList.append('series')
                                                runList.append(subcommand)
                                                runList.append(int(argDict['number']))
                                                runList.append(float(argDict['time']))
                                                runList.append(argDict['basename'])
                                                print("The specified time is", float(argDict['time']))
                                                print("The specified number of exposures is", float(argDict['number']))
                                                return runList  # [series, dark/flat/object, number, time, basename]
                                            else:
                                                return "ERROR: specified basename is empty..."
                                        else:
                                            return "ERROR: specified time is negative or the number of images is not 1 or more..."

                                    else:
                                        return "ERROR: specified time and/or number of exposures not a number..."
                                else:
                                    return "SyntaxError: time argument, basename, and/or number of exposures is wrong..."
                        else:
                            try:
                                helpArg = scriptLine[2]
                            except IndexError:
                                return "ERROR: argument after \"help\" not given..."
                            else:
                                if len(scriptLine[0:]) > 3:
                                    return "ERROR: too many arguments after \"help\"..."
                                runList.append(command)
                                runList.append(subcommand)
                                runList.append(helpArg)
                                return runList
                    else:
                        return "ERROR: not a recognized subcommand...", subcommand

                # possible commands (only one arg):
                # set binning (1 or 2)
                # set filter (1, 2, 3, 4, 5, or 6)
                # set temp (-80 to -10)
                # set help (binning, filter temp)
                if command == "set":

                    if subcommand in setSub:
                        try:
                            arg1 = scriptLine[2]
                        except IndexError:
                            return "ERROR: didn't specify an argument after \"subcommand\"..."
                        else:
                            if len(scriptLine[0:]) > 3:
                                return "ERROR: there are too many arguments specified..."

                            if subcommand == 'binning':
                                if arg1.isdigit():
                                    if int(arg1) == 1 or int(arg1) == 2:

                                        runList.append(command)
                                        runList.append(subcommand)
                                        runList.append(arg1)
                                        return runList  # [set, binning, 1]
                                    else:
                                        return "ValueError: binning value is out of range, must be 1 or 2..."
                                else:
                                    return "SyntaxError: binning value is not an int..."
                            if subcommand == 'temp':
                                if arg1.isdigit():
                                    if int(arg1) >= -80 and int(arg1) <= -10:
                                        runList.append("setTEC")
                                        runList.append(arg1)
                                        return runList
                                    else:
                                        return "ValueError: temperature out of range of -80 to -10..."
                                elif arg1 == 'warmup':
                                    runList.append("warmup")  # command for sending warmup
                                    return runList
                                else:
                                    return "SyntaxError: temperature is not a number..."
                            if subcommand == 'filter':
                                if arg1.isdigit():
                                    if int(arg1) >= 1 and int(arg1) <= 6:  # 6 filter positions: (1, 2, 3, 4, 5, 6)
                                        runList.append(command)
                                        runList.appedn(subcommand)
                                        runList.append(arg1)
                                        return runList
                                    else:
                                        return "ValueError: filter position out of range, must specify int from 1 to 6..."
                                else:
                                    return "SyntaxError: filter position given is not an int..."
                            if subcommand == 'help':
                                if arg1 in ['binning', 'temp']:
                                    runList.append(command)
                                    runList.append(subcommand)
                                    runList.append(arg1)
                                    return runList
                                else:
                                    return "ERROR: %s after \"help\" is not recognized..." % arg1
                    else:
                        return "ERROR: %s is not a recognized subcommand..." % subcommand

                # possible commands
                # filter home  # will slew filter to home
                # filter status # will give details on the state of connection
                # filter help (filter or home) # gives details on how to run the command and what it does
                if command == "filter":
                    if subcommand in filterSub:  # home, status, help

                        if subcommand == 'home':
                            runList.append(command)
                            runList.append(subcommand)
                            return runList
                        if subcommand == 'status':
                            runList.append(command)
                            runList.append(subcommand)
                            return runList
                        if subcommand == 'help':
                            try:
                                arg1 = scriptLine[2]
                            except IndexError:
                                return "ERROR: no argument after \"filter help\" specified..."
                            else:
                                if len(scriptLine[0:]) > 3:  # make sure there aren't anymore args given than needed
                                    return "ERROR: extra argument after \"help\" given..."
                                if arg1 == 'home':
                                    print("slews to filter")
                                if arg1 == 'status':
                                    print("gives the status of the filter")
                                runList.append(command)
                                runList.append(subcommand)
                                runList.append(arg1)
                                return runList
                    else:
                        return "ERROR: %s is not a recognized subcommand..." % subcommand

                # possible commands
                # help expose
                # help set
                # help filter
                if command == "help":
                    if subcommand in helpSub:
                        runList.append(command)
                        runList.append(subcommand)
                        return runList
                    else:
                        return "ERROR: %s is not a recognized subcommand..." % subcommand
            else:
                return "ERROR: %s is not a recognized command..." % command
