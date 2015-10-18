#!/usr/bin/env python
import wx
import numpy as np
import matplotlib
matplotlib.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
from matplotlib.pyplot import gcf, setp
from matplotlib.figure import Figure
from mpldatacursor import datacursor,HighlightingDataCursor
import dHvA_Util
from scipy import signal

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
        self.smoothOn= False
        self.polyOn=False
        self.smoothWinType = 'hamming'
        self.interp_data,self.inv_x,self.delta_inv_x = dHvA_Util.inv_field(self.x,self.InY)
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
        self.rawPlot.legend(['In Phase','Out Phase'],fontsize=10)

        #plot Polynomial BG
        if self.polyOn:
            self.PolyBG_Coeff = np.polyfit(self.sortedX,self.sortedSignal,self.polyOrder)
            self.PolyBG_Y = np.polyval(self.PolyBG_Coeff,self.sortedX)
            self.noBG_Y = self.sortedSignal-self.PolyBG_Y
        else:
            self.noBG_Y = self.sortedSignal
            self.PolyBG_Y = np.zeros(len(self.sortedSignal))
        
                    
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
        self.polyBGPlot.legend(['Raw','Poly BG','no BG'],fontsize=10)
        #using datacursor makes the program load up really slow
        #HighlightingDataCursor(self.polyBGPlot.lines) 

        #plot despike
        self.despikePlot = self.figure.add_subplot(223)
        if len(self.despikePlot.lines)>0:
            del self.despikePlot.lines[0]
            del self.despikePlot.lines[0]
        #    del self.despikePlot.lines[0]
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
        self.despikePlot.legend(['data','despiked'],fontsize=10) 
        self.figure.tight_layout()

        #plot Smooth
        self.smoothPlot = self.figure.add_subplot(224)
        if len(self.smoothPlot.lines)>0:
            del self.smoothPlot.lines[0]
        #smooth and window the data
                    
#        self.DeltaFreqY = 1/self.delta_inv_x 
#        #padd the data
#        pad_mult = 10
#        zero_matrixY = np.zeros(len(self.windowed_dataY)*pad_mult/2)
#        self.pad_wind_dataY = np.append(self.windowed_dataY, zero_matrixY)
#        # pad_wind_data = np.append(zero_matrix, pad_wind_data)
#
#        self.FreqY, self.FFT_SignalY = dHvA_Util.take_fft(self.pad_wind_dataY, 20, self.DeltaFreqY)
#        self.smoothPlot.plot(self.FreqY,self.FFT_SignalY,linewidth=2,color='blue')
#
        #invert the field
        self.interp_data,self.inv_x,self.delta_inv_x = dHvA_Util.inv_field(self.sortedX,self.despikeY)

        if self.smoothOn:
            self.smoothY = dHvA_Util.smooth(self.interp_data,30,self.smoothWinType)
            window_func = eval('signal.'+self.smoothWinType)
            window_to_use = window_func(len(self.smoothY))
            self.windowed_dataY = window_to_use*self.smoothY
        else:
            self.smoothY = self.interp_data
            self.windowed_dataY = self.smoothY
        self.smoothPlot.plot(self.inv_x,self.windowed_dataY,linewidth=2,color='green')
        self.smoothPlot.set_xlabel('1/B (1/T)')
        self.smoothPlot.set_title('Smooth and Windowing')
        self.smoothPlot.relim()
        self.smoothPlot.autoscale(True)
        self.figure.tight_layout()
    def repaint(self):
        self.canvas.draw()

