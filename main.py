#!/usr/bin/env python
import wx
from dHvAFrame import *
app=wx.App(False)
frame=dHvAFrame(parent = None,title='dHvA Analyser',size=(640,480))
app.MainLoop()
