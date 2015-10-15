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
        self.noBG_Y = self.InY
        self.polyOrder = 3
        self.decompLevel = 2
        self.waveletType = 'coif2'
        self.despikeOn = False
        self.smoothWinType = 'hamming'
        self.canvas = FigureCanvasWxAgg(self, -1, self.figure)
        self.draw()
    
    def draw(self):
       
        #plot raw data
        self.rawPlot = self.figure.add_subplot(221)
        if len(self.rawPlot.lines)>0:
            del self.rawPlot.lines[0]
            del self.rawPlot.lines[0] #delete the second one, since the first one is deleted, the index returns to 0
        self.rawPlot.plot(self.x,self.InY,linewidth=2,color='blue')
        self.rawPlot.plot(self.x,self.OutY,linewidth=2,color='red')
        self.rawPlot.relim()
        self.rawPlot.autoscale(True)
        self.rawPlot.set_title('Raw data')
        self.rawPlot.set_xlabel('Field (T)')
        self.rawPlot.legend(['In Phase Y','Out Phase Y'])

        #plot Polynomial BG
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
        self.polyBGPlot.set_title('Polynomial BG Removal')
        self.polyBGPlot.set_xlabel('Field (T)')
        self.polyBGPlot.legend(['Raw Data','Poly BG','Subtraction'])

        #plot despike
        self.despikePlot = self.figure.add_subplot(223)
        if len(self.despikePlot.lines)>0:
            del self.despikePlot.lines[0]
            del self.despikePlot.lines[0]
        self.despikePlot.plot(self.sortedX,self.noBG_Y,linewidth=2,color='blue')
        if self.despikeOn:
            self.despikeY = dHvA_Util.wavelet_filter(self.noBG_Y,self.decompLevel,self.waveletType)
        else:
            self.despikeY = self.noBG_Y
        self.despikePlot.plot(self.sortedX,self.despikeY,linewidth=2,color='red')
        self.despikePlot.relim()
        self.despikePlot.autoscale(True)
        self.despikePlot.set_title('Despike')
        self.despikePlot.set_xlabel('Field (T)')
        self.despikePlot.legend(['data','despiked data']) 
        self.figure.tight_layout()

        #plot FFT
        self.FFTPlot = self.figure.add_subplot(224)
        if len(self.FFTPlot.lines)>0:
            del self.FFTPlot.lines[0]
        #invert the field

        self.FFTPlot.set_xlabel('1/B (1/T)')
        self.FFTPlot.set_ylabel('Amplitude (a.u.)')
        self.FFTPlot.set_title('FFT')

    def repaint(self):
        self.canvas.draw()

