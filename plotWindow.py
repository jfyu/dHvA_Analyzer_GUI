#!/usr/bin/env python
import wx
import numpy as np
import matplotlib
matplotlib.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
#from matplotlib.pyplot import gcf, setp
from matplotlib.figure import Figure
#from mpldatacursor import datacursor,HighlightingDataCursor
import dHvA_Util
from scipy import signal

class plotWindow(wx.Window):
    def __init__(self, *args, **kwargs):
        wx.Window.__init__(self,*args,**kwargs)
        self.figure=Figure()
        
        #starting variables
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
        self.smoothOn= True
        self.polyOn= True
        self.smoothWinType = 'hamming'
        self.interp_data,self.inv_x,self.delta_inv_x = dHvA_Util.inv_field(self.x,self.InY)
        
        self.canvas = FigureCanvasWxAgg(self, -1, self.figure)
        
        #toolbar
        self.toolbar = NavigationToolbar2Wx(self.canvas)
        self.toolbar.Realize()
        tw, th = self.toolbar.GetSizeTuple()
        fw, fh = self.canvas.GetSizeTuple()
        self.toolbar.SetSize(wx.Size(fw, th))
        self.toolbar.update()
        self.toolbar.Show()

        #sizers
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas,1,wx.EXPAND)
        self.sizer.Add(self.toolbar,0,wx.GROW)
        self.SetSizer(self.sizer)
        self.sizer.Fit(self)
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
        self.rawPlot.legend(['In Phase','Out Phase'],fontsize=10,fancybox=True,framealpha=0.5)

        #plot Polynomial BG

        #sort the signals
        self.sortedX, self.sortedSignal = dHvA_Util.sort_array(self.x, self.InY)

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
        self.polyBGPlot.legend(['Raw','Poly BG','no BG'],fontsize=10,fancybox=True,framealpha=0.5)
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
        self.despikePlot.legend(['data','despiked'],fontsize=10,fancybox=True,framealpha=0.5) 
        self.figure.tight_layout()

        #plot Smooth
        self.smoothPlot = self.figure.add_subplot(224)
        if len(self.smoothPlot.lines)>0:
            del self.smoothPlot.lines[0]
            #del self.smoothPlot.lines[0]
        
        #smooth and window the data
        #invert the field
        self.interp_data,self.inv_x,self.delta_inv_x = dHvA_Util.inv_field(self.despikeY,self.sortedX)
        #self.inv_x,self.interp_data,self.delta_inv_x = dHvA_Util.inv_field(self.sortedX,self.despikeY)
        if self.smoothOn:
            self.smoothY = dHvA_Util.smooth(self.interp_data,30,self.smoothWinType)
            window_func = eval('signal.'+self.smoothWinType)
            window_to_use = window_func(len(self.smoothY))
            self.windowed_dataY = window_to_use*self.smoothY
            print self.smoothWinType
        else:
            pass
            #self.smoothY = self.interp_data
            #self.windowed_dataY = self.interp_data
        self.smoothPlot.plot(self.inv_x,self.windowed_dataY,linewidth=2,color='green')
        #self.smoothPlot.plot(self.inv_x,self.smoothY,linewidth=2,color='red')
        self.smoothPlot.set_xlabel('1/B (1/T)')
        self.smoothPlot.set_title('Smooth and Windowing')
        #self.smoothPlot.set_xlim([0.06,0.078])
        self.smoothPlot.relim()
        self.smoothPlot.autoscale(True)
        self.figure.tight_layout()
    def repaint(self):
        self.canvas.draw()

