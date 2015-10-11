#!/usr/bin/env python
import wx
import numpy as np
import matplotlib
matplotlib.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
from matplotlib.pyplot import gcf, setp
from matplotlib.figure import Figure
from mpldatacursor import datacursor
import dHvA_Util

class plotWindow(wx.Window):
    def __init__(self, *args, **kwargs):
        wx.Window.__init__(self,*args,**kwargs)
        self.figure=Figure()
        self.x = np.linspace(-10, 20,100)
        self.InY = np.sin(self.x)
        self.OutY = np.cos(self.x)
        self.sortedX = self.x
        self.sortedSignal = self.InY
        self.polyOrder = 3
        self.canvas = FigureCanvasWxAgg(self, -1, self.figure)
        self.draw()
    
    def draw(self):
        self.rawPlot = self.figure.add_subplot(221)
        if len(self.rawPlot.lines)>0:
            del self.rawPlot.lines[0]
            del self.rawPlot.lines[0] #delete the second one, since the first one is deleted, the index returns to 0
        self.rawPlot.plot(self.x,self.InY,linewidth=2,color='blue')
        self.rawPlot.plot(self.x,self.OutY,linewidth=2,color='red')
        self.rawPlot.relim()
        self.rawPlot.autoscale(True)
       
        self.PolyBG_Coeff = np.polyfit(self.sortedX,self.sortedSignal,self.polyOrder)
        self.PolyBG_Y = np.polyval(self.PolyBG_Coeff,self.sortedX)
        self.noBG_Y = self.sortedSignal-self.PolyBG_Y
        self.polyBGPlot = self.figure.add_subplot(222)
        if len(self.polyBGPlot.lines)>0:
            del self.polyBGPlot.lines[0]
            del self.polyBGPlot.lines[0]
            del self.polyBGPlot.lines[0]
        self.polyBGPlot.plot(self.sortedX,self.sortedSignal,linewidth=2,color='blue')
        self.polyBGPlot.plot(self.sortedX,self.PolyBG_Y,linewidth=2,color='red')
        self.polyBGPlot.plot(self.sortedX,self.noBG_Y,linewidth=2,color='green')
        self.polyBGPlot.relim()
        self.polyBGPlot.autoscale(True)
   
        
    def repaint(self):
        self.canvas.draw()

