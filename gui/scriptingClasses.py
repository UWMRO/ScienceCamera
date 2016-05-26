#!/usr/bin/python

import wx
import AddLinearSpacer as als

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

    def onUpload(self, event):
        print "Upload your script"

    def parseCommand(self, command):
        """
        This method parses the command inputed by the user from the command promp text control box.
        If the command is good it will return a list with the command that is sent to the server
        followed by the necessary arguments.  If the command is bad then a string is sent back that
        will be displayed to the user about what went wrong.  For any help commands this is delt with 
        outside the parser.
        """
        scriptLine = command.split()

        command = None
        subcommand = None

        commandList = ['expose', 'filter', 'help', 'set']
        exposeSub = ['abort', 'bias', 'dark', 'flat', 'object', 'help']
        filterSub = ['home', 'slew', 'status', 'help']
        helpSub = ['expose', 'filter', 'set']
        setSub = ['binning', 'temp', 'warmup', 'help']
        
        
        runList = [] # first entry is the command to send the next entries depend on the command being sent
        try:
            command = scriptLine[0]
            subcommand = scriptLine[1]
        except IndexError:
            print "Command and/or subcommand not given"
        else:
            if command in commandList:
            #print "moving on to sub command"
                if command == "expose":

                    if subcommand in exposeSub:
            
                        if subcommand == 'abort':
                            runList.append("abort") # only command to send
                            print "abort mission"
                        elif subcommand in ['bias', 'dark', 'flat', 'object']:
                            print "exposing of this type"
                            time = None
                            baseString = None
                            try:
                                arg1 = scriptLine[2]
                                arg2 = scriptLine[3]
                                arg3 = scriptLine[4]
                            except IndexError:
                                print "No time, base, or exposure number string args"
                            else:

                                arg1 = arg1.split("=")
                                arg2 = arg2.split("=")
                                arg3 = arg3.split("=")
                                argDict = {}
                                # Makes sure that when args are split by equals that there are two entries and that the first one is
                                # either time or basename.
                                if((len(arg1) == 2 and (arg1[0] in ['time', 'basename', 'nexposure'])) and (len(arg2) == 2 and (arg2 in ['time', 'basename', 'nexposure'])) and (len(arg3) == 2 and (arg3[0] in ['time', 'basename', 'nexposure']))):
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
                                        
                                        
                                    else:
                                        print "specified time or number of exposure is not number"
                                else:
                                    print "time argument or basename or number of exposure  is wrong"
                            
                        else:
                            try:
                                helpArg = scriptLine[2]
                            except IndexError:
                                print "help argument was not given"
                            else:
                                runList.append(command)
                                runList.append(subcommand)
                                runList.append(helpArg)
                            print "choose an argument for help"
            
                        print "exposing with subcommand", subcommand
                    else:
                        print "not a recognized subcommand", subcommand

                if command == "set":
                    
                    if subcommand in setSub:
                        if subcommand in ['binning', 'temp', 'help']:
                            try:
                                arg1 = scriptLine[2]
                            except:
                                print "Didn't specify an arg"
                            else:
                            
                                if(subcommand == 'binning'):
                                    if(als.isInt(arg1)):
                                        if(int(arg1) == 1 or int(arg1) == 2):
                                            
                                            runList.append(command)
                                            runList.append(subcommand)
                                            runList.append(arg1)
                                        else:
                                            print "binning number out of range"
                                    else:
                                        print "binning value is not an int or number"
                                if(subcommand == 'temp'):
                                    if(als.isInt(arg1)):
                                        if(int(arg1) >= -80 and int(arg1) <= -10):
                                            runList.append("setTEC")
                                            runList.append(arg1)
                                        else:
                                            print "Temperature out of range"
                                    else:
                                        print "Temperature is not a number"
                                if(subcommand == 'help'):
                                    if arg1 in ['binning', 'temp', 'warmup']:
                                        runList.append(command)
                                        runList.append(subcommand)
                                        runList.append(arg1)
                                    else:
                                        print "not a known argument"
                        if(subcommand == 'warmup'):
                            runList.append(subcommand) # simple command of warming up
                        print "setting with subcommand", subcommand
                    else:
                        print "not a recognized subcommand", subcommand
            
                if command == "filter":
                    if subcommand in filterSub:
                        print "filtering with subcommand", subcommand
                    else:
                        print "not a recognized subcommand", subcommand

                if command == "help":
                    if subcommand in helpSub:
                        print "helping with subcommand", subcommand
                    else:
                        print "not a recognized subcommand", subcommand
        else:
            print "not a recognized command"
