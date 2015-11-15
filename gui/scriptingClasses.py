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
