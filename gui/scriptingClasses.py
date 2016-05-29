#!/usr/bin/python

import wx
import AddLinearSpacer as als
import thread

class ScriptStatus(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        ## Main Sizer
        self.vertSizer = wx.BoxSizer(wx.VERTICAL)

        ## Widgets
        self.statusBox = wx.StaticBox(self, label = "Script Activity", size = (400,150))
        self.statusBoxSizer = wx.StaticBoxSizer(self.statusBox, wx.VERTICAL)

        self.activityText = wx.TextCtrl(self, style=wx.TE_READONLY|wx.TE_MULTILINE, size=(400,150))

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

        ## subsizers
        self.subVert = wx.BoxSizer(wx.VERTICAL)
        self.buttonSizer = wx.BoxSizer(wx.HORIZONTAL)

        ## Widgets
        self.commandFrame = wx.StaticBox(self, id=3000, label = "Command Prompt", size=(200, 50))
        self.commandFrameSizer = wx.StaticBoxSizer(self.commandFrame, wx.VERTICAL)

        self.button = wx.Button(self, id=3001, label="OK")
        self.upButton = wx.Button(self, id=3002, label="Upload")
        self.commandBox = wx.TextCtrl(self, id=3003, size=(200, -1))

        # adjust subsizers
        self.buttonSizer.Add(self.button, flag=wx.ALIGN_CENTER)
        als.AddLinearSpacer(self.buttonSizer, 10)
        self.buttonSizer.Add(self.upButton, flag=wx.ALIGN_CENTER)

        self.subVert.Add(self.commandBox, flag=wx.ALIGN_CENTER)
        als.AddLinearSpacer(self.subVert, 15)
        self.subVert.Add(self.buttonSizer, flag=wx.ALIGN_CENTER)


        self.commandFrameSizer.Add(self.subVert, flag=wx.ALIGN_CENTER)



        # adjust main sizers
        self.vertSizer.Add(self.commandFrameSizer, flag=wx.ALIGN_CENTER)

        ## Variables
        self.command = ""

        ## Bindings
        self.Bind(wx.EVT_TEXT, self.getCommand, id=3003)
        self.Bind(wx.EVT_BUTTON, self.onOk, id=3001)
        self.Bind(wx.EVT_BUTTON, self.onUpload, id=3002)
        ##

        self.SetSizer(self.vertSizer)
        self.vertSizer.Fit(self)

    def getCommand(self, event):
        self.command = self.commandBox.GetValue()

    def onOk(self, event):
        if self.command is "":
            print "No command"
        else:
            print self.command
            runList = self.parseCommand(self.command) # parses user command
            self.executeCommand(runList) # executes user command
            

    def onUpload(self, event):
        print "Upload your script"

    def executeCommand(self, runList):
        """
        This will take the known order of runList from the command and then send it to the server
        while also displaying pertanent information.
        """
        val = self.parent.scriptStatus.activityText.GetValue()
        self.parent.scriptStatus.activityText.SetValue(val + str(runList) + "\n")
        self.parent.scriptStatus.activityText.SetInsertionPointEnd()
        print val

        if(type(runList) == list):
            print runList
            print "sending command"

            # surround in str to get rid of unicode, otherwise fails at sending
            sendCommand = str(runList[0])
            if(sendCommand == 'series'):
                imtype = str(runList[1])
                nexposure = str(runList[2])
                exposeClass = self.parent.parent.parent.takeImage.exposureInstance

                # example runList (['series', 'bias', int(nexposure), 'basename'])
                if(imtype == 'bias'):
                    d = self.protocol.addDeferred("seriesSent")
                    d.addCallback(exposeClass.displaySeriesImage_thread)

                    d = self.protocol.sendCommand(sendCommand + " " + imtype + " " + nexposure + " 0 " + str(self.parent.parent.parent.binning))
                    d.addCallback(exposeClass.seriesCallback)
                        
                    # start timer
                    thread.start_new_thread(exposeClass.exposeTimer, (0,))


        else:
            print "something went wrong"
            print runList
        pass

    def parseCommand(self, command):
        """
        This method parses the command inputed by the user from the command promp text control box.
        If the command is good it will return a list with the command that is sent to the server
        followed by the necessary arguments.  If the command is bad then a string is sent back that
        will be displayed to the user about what went wrong.  For any help commands this is delt with 
        outside the parser.
        """
        scriptLine = command.split()
        print scriptLine

        command = None
        subcommand = None

        commandList = ['expose', 'filter', 'help', 'set']
        exposeSub = ['abort', 'bias', 'dark', 'flat', 'object', 'help']
        filterSub = ['home', 'status', 'help']
        helpSub = ['expose', 'filter', 'set']
        setSub = ['binning', 'filter', 'temp', 'warmup', 'help']
        
        
        runList = [] # first entry is the command to send the next entries depend on the command being sent
        try:
            command = scriptLine[0]
            subcommand = scriptLine[1]
        except IndexError:
            print "Command and/or subcommand not given"
        else:
            if command in commandList:
            #print "moving on to sub command"

                # Possible commands (the order of time=X.X, basename=somename, and nexposure=XX is ambiguous)
                # expose abort
                # expose bias basename=bias nexposure=XX
                # expose dark time=X.X basename=dark nexposure=XX
                # expose flat time=X.X basename=flat nexposure=XX
                # expose object time=X.X basename=object nexposure=XX
                # expose help abort
                # expose help bias
                # expose help dark
                # expose help flat 
                # expose help object
                if command == "expose":

                    if subcommand in exposeSub:
            
                        if subcommand == 'abort':
                            runList.append("abort") # only command to send
                            print "abort mission"
                            return runList
                        elif(subcommand == 'bias'):
                            print "exposing of this type"
                            try:
                                arg1 = scriptLine[2]
                                arg2 = scriptLine[3]
                            except IndexError:
                                print "No basename or nexposure args"
                            else:
                                if(len(scriptLine[0:]) > 4):
                                    return "too many arguments"
                                arg1 = arg1.split("=")
                                arg2 = arg2.split("=")
                                argDict = {}
                                print arg1, arg2
                                
                                if((len(arg1) == 2 and (arg1[0] in ['basename', 'nexposure'])) and (len(arg2) == 2 and (arg2[0] in ['basename', 'nexposure']))):
                                    # map arguements to be able to call them in order
                                    argDict[arg1[0]] = arg1[1]
                                    argDict[arg2[0]] = arg2[1]
                                    
                                    if(als.isInt(argDict['nexposure'])):
                                        # final stop; everything has been checked so now we build up the list to return
                                        runList.append('series')
                                        runList.append(subcommand)
                                        runList.append(int(argDict['nexposure']))
                                        runList.append(argDict['basename'])
                                        print "The specified number of exposures is", float(argDict['nexposure'])
                                        return runList
                                        
                                    else:
                                        return "specified time or number of exposure is not number"
                                else:
                                    return "basename or number of exposures is wrong"

                                
                        elif subcommand in ['dark', 'flat', 'object']:
                            print "exposing of this type"
                            try:
                                arg1 = scriptLine[2]
                                arg2 = scriptLine[3]
                                arg3 = scriptLine[4]
                            except IndexError:
                                return "No time, basename, or exposure number string args"
                            else:
                                if(len(scriptLine[0:]) > 5):
                                    return "too many arugments"

                                arg1 = arg1.split("=")
                                arg2 = arg2.split("=")
                                arg3 = arg3.split("=")
                                argDict = {}
                                print arg1, arg2, arg3
                                # Makes sure that when args are split by equals that there are two entries and that the first one is
                                # either time or basename.
                                if((len(arg1) == 2 and (arg1[0] in ['time', 'basename', 'nexposure'])) and (len(arg2) == 2 and (arg2[0] in ['time', 'basename', 'nexposure'])) and (len(arg3) == 2 and (arg3[0] in ['time', 'basename', 'nexposure']))):
                                    # map arguments to be able to call them in order
                                    argDict[arg1[0]] = arg1[1]
                                    argDict[arg2[0]] = arg2[1]
                                    argDict[arg3[0]] = arg3[1]
                                    
                    
                                    if(als.isNumber(argDict['time']) and als.isInt(argDict['nexposure'])):
                                        # final stop; everything has been checked so now we build up the list to return
                                        runList.append('series')
                                        runList.append(subcommand)
                                        runList.append(int(argDict['nexposure']))
                                        runList.append(float(argDict['time']))
                                        runList.append(argDict['basename'])
                                        print "The specified time is", float(argDict['time'])
                                        print "The specified number of exposures is", float(argDict['nexposure'])
                                        return runList
                                        
                                    else:
                                        return "specified time or number of exposure is not number"
                                else:
                                    return "time argument or basename or number of exposure  is wrong"
                            
                        else:
                            try:
                                helpArg = scriptLine[2]
                            except IndexError:
                                return "help argument was not given"
                            else:
                                if(len(scriptLine[0:]) > 3):
                                    return "there are too many arguments"
                                runList.append(command)
                                runList.append(subcommand)
                                runList.append(helpArg)
                                return runList
                    else:
                        return "not a recognized subcommand", subcommand

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
                            return "Didn't specify an arg"
                        else:
                            if(len(scriptLine[0:]) > 3):
                               return "there are too many arguments given"

                            if(subcommand == 'binning'):
                                if(als.isInt(arg1)):
                                    if(int(arg1) == 1 or int(arg1) == 2):
                                            
                                        runList.append(command)
                                        runList.append(subcommand)
                                        runList.append(arg1)
                                        return runList
                                    else:
                                        return "binning number out of range"
                                else:
                                    return "binning value is not an int or number"
                            if(subcommand == 'temp'):
                                if(als.isInt(arg1)):
                                    if(int(arg1) >= -80 and int(arg1) <= -10):
                                        runList.append("setTEC")
                                        runList.append(arg1)
                                        return runList
                                    else:
                                        return "Temperature out of range"
                                elif(arg1 == 'warmup'):
                                    runList.append("warmup") # command for sending warmup
                                    return runList
                                else:
                                    return "Temperature is not a number"
                            if(subcommand == 'filter'):
                                if(als.isInt(arg1)):
                                    if(int(arg1) >= 1 and int(arg1) <= 6): # 6 filter positions: (1, 2, 3, 4, 5, 6)
                                        runList.append(command)
                                        runList.appedn(subcommand)
                                        runList.append(arg1)
                                        return runList
                                    else:
                                        return "filter position out of range"
                                else:
                                    return "filter position specified is not a number"
                            if(subcommand == 'help'):
                                if arg1 in ['binning', 'temp']:
                                    runList.append(command)
                                    runList.append(subcommand)
                                    runList.append(arg1)
                                    return runList
                                else:
                                    return "not a known argument"
                    else:
                        return "not a recognized subcommand", subcommand
            
                # possible commands
                # filter home  # will slew filter to home
                # filter status # will give details on the state of connection
                # filter help (filter or home) # gives details on how to run the command and what it does
                if command == "filter":
                    if subcommand in filterSub: # home, status, help

                        if(subcommand == 'home'):
                            runList.append(command)
                            runList.append(subcommand)
                            return runList
                        if(subcommand == 'status'):
                            runList.append(command)
                            runList.append(subcommand)
                            return runList
                        if(subcommand == 'help'):
                            try:
                                arg1 = scriptLine[2]
                            except IndexError:
                                return "no third argument specified"
                            else:
                                if(len(scriptLine[0:]) > 3):  # make sure there aren't anymore args given than needed
                                    return "extra argument given"
                                if(arg1 == 'home'):
                                    print "slews to filter"
                                if(arg1 == 'status'):
                                    print "gives the status of the filter"
                                runList.append(command)
                                runList.append(subcommand)
                                runList.append(arg1)
                                return runList
                                   
                    else:
                        return "not a recognized subcommand", subcommand

                # possible commands 
                # help expose
                # help set
                # help filter
                if command == "help":
                    if subcommand in helpSub:
                        if(subcommand == 'expose'):
                            return "What are the expose options?"
                        if(subcommand == 'set'):
                            return "What are the set options?"
                        if(subcommand == 'filter'):
                            return "What are the filter options?"
                    else:
                        return "not a recognized subcommand", subcommand
            else:
                return "not a recognized command"
