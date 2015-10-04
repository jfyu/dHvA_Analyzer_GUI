#!/usr/bin/env python
import wx
import numpy as np

import matplotlib
matplotlib.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
from matplotlib.pyplot import gcf, setp

class Knob:
    def setKnob(self, value):
        pass



class Param:
    """ This class handles all the parameters that are being controled. This allows a cleaner way to update/feedback to the other controls """
    def __init__(self, initialValue=None, minimum=0,maximum=1.):
        self.minimum=minimum
        self.maximum = maximum
        if initialValue != self.constrain(initialValue):
            raise ValueError('illegal initial value')
        self.value = initialValue
        self.knobs = []

    def attach(self, knob):
        self.knobs += [knob]

    def set(self, value, knob=None):
        self.value = value
        self.value = self.constrain(value)
        for feedbackKnob in self.knobs:
            if feedbackKnob != knob:
                feedbackKnob.setKnob(self.value)
        return self.value

    def constrain(self, value):
        if value <= self.minimum:
            value = self.minimum
        if value >= self.maximum:
            value = self.maximum
        return value

class dHvAFrame(wx.Frame):
    #"""this creates the frame for the whole program"""
    def __init__(self, *args, **kwargs):
        self.dirname=''
        #same initialization as wx.Frame
        wx.Frame.__init__(self,*args,**kwargs)

        #set up graph windows
        #self.graphWindow = graphWindow(self)

        #setting up the menu
        filemenu=wx.Menu()
        menuOpen = filemenu.Append(wx.ID_OPEN,"OPEN","Open a data file")
        menuExit = filemenu.Append(wx.ID_EXIT, "EXIT", "Terminate the Program")

        #Creating the menu bar
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu,"File")
        self.SetMenuBar(menuBar)

        
        #Events
        self.Bind(wx.EVT_MENU, self.OnOpen, menuOpen)
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)

        #set up controls. Dropdown menu for selecting data
        self.comboBox = wx.ComboBox(self,choices=['Ax','Bx'],style=wx.CB_DROPDOWN)
        
        self.Show()

    def OnExit(self,e):
        self.Close(True)  # Close the frame.

    def OnOpen(self,e):
     #""" Open a file"""
        dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", "*.*", wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetFilename()
            self.dirname = dlg.GetDirectory()
            f = open(os.path.join(self.dirname, self.filename), 'r')
            self.dataInput=f.read()#change to netcdf reading
            f.close()
        dlg.Destroy()

app=wx.App(False)
frame=dHvAFrame(parent = None,title='dHvA Analyser',size=(640,480))
app.MainLoop()
