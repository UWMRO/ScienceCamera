#!/usr/bin/python

import wx

# Frame class.
class Evora(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, "Evora Acquisition GUI", size = (825, 625))

        panel = wx.Panel(self)
        notebook = wx.Notebook(panel)

        # define the each tab
        page1 = TakeImage(notebook)
        page2 = OtherParams(notebook)
        page3 = Log(notebook)

        # add each tab to the notebook
        notebook.AddPage(page1, "Imaging")
        notebook.AddPage(page2, "Controls")
        notebook.AddPage(page3, "Log")

        # make instances of the tabs to access variables within them
        self.takeImage = notebook.GetPage(0)
        self.otherParams = notebook.GetPage(1)
        self.log = notebook.GetPage(2)

        # size panels
        sizer = wx.BoxSizer()
        sizer.Add(notebook, 1, wx.EXPAND)

        panel.SetSizer(sizer)
        panel.Layout()

class TakeImage(wx.Panel): ## first tab; with photo imaging
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        # Things to add: drop down menu for filters
        #                drop down menu for type of image
        #                add button to filter drop down menu
        #                add button for taking exposure
        #                add updating text for temperature in bottom left of GUI

        # Add functionalality here
        self.expTime = wx.StaticText(self, label="Exposure Time (s)")
        self.expValue = wx.TextCtrl(self, size=(75, -1), style=wx.TE_PROCESS_ENTER)
        #self.expValue.SetStyle(self, style=wx.TE_PROCESS_ENTER)
        self.expButton = wx.Button(self, label="Ok", size=(50, -1))

        # Set sizers so I have horizontal and vertical control
        self.topbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox = wx.BoxSizer(wx.HORIZONTAL)

        # Exposure Time with box to enter value
        self.vbox.AddSpacer(50)
        self.vbox.Add(self.expTime)
        self.vbox.AddSpacer(25)
        self.vbox.Add(self.expValue)
        self.vbox.AddSpacer(25)
        self.vbox.Add(self.expButton)



        self.topbox.AddSpacer(25)
        self.topbox.Add(self.vbox)

        self.Bind(wx.EVT_TEXT_ENTER, self.getExpVal, self.expValue)
        self.Bind(wx.EVT_BUTTON, self.getValsButton, self.)

        # comes last
        self.SetSizer(self.topbox)
        self.topbox.Fit(self)

    def getExpVal(self, e):
        self.exp = self.expValue.GetValue()
        print float(self.exp)

class OtherParams(wx.Panel): # second tab; with other parameters like setting the temperature to cool.
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.vbox = wx.BoxSizer(wx.VERTICAL)

        self.SetSizer(self.vbox)
        self.vbox.Fit(self)

class Log(wx.Panel): # third tab; with logging of each command
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.vbox = wx.BoxSizer(wx.VERTICAL)

        self.SetSizer(self.vbox)
        self.vbox.Fit(self)


if __name__ == "__main__":
    app = wx.PySimpleApp()
    app.frame = Evora()
    app.frame.Show()
    app.MainLoop()
