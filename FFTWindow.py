import wx
import numpy as np
import matplotlib
matplotlib.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.pyplot import gcf, setp
from matplotlib.figure import Figure
from mpldatacursor import datacursor
import dHvA_Util
from scipy import signal


class FFTWindow(wx.Window):
    def __init__(self, *args, **kwargs):
        self.window = wx.Window.__init__(self,*args,**kwargs)
        self.figure=Figure()
        self.x = np.linspace(-10, 20,100)
        self.Y = np.sin(self.x)
        self.delta_inv_x = 30/100.0
        self.canvas = FigureCanvasWxAgg(self, -1, self.figure)
        self.canvas.mpl_connect('button_press_event',self.coordPrint)
        self.toolbar = NavigationToolbar2Wx(self.canvas)
        self.toolbar.Realize()
        self.toolbar.Show()
        #self.draw()

    def draw(self):
        self.FFTPlot = self.figure.add_subplot(111)
        if len(self.FFTPlot.lines)>0:
            del self.FFTPlot.lines[0]
        #smooth and window the data
        self.DeltaFreqY = 1/self.delta_inv_x 
        #padd the data
        pad_mult = 10
        zero_matrixY = np.zeros(len(self.Y)*pad_mult/2)
        self.pad_wind_dataY = np.append(self.Y, zero_matrixY)
        # pad_wind_data = np.append(zero_matrix, pad_wind_data)

        self.FreqY, self.FFT_SignalY = dHvA_Util.take_fft(self.pad_wind_dataY, 20, self.DeltaFreqY)
        self.FFTPlot.plot(self.FreqY,self.FFT_SignalY,linewidth=2,color='blue')
        self.FFTPlot.set_xlabel('dHvA Frequency (1/T)')
        self.FFTPlot.set_ylabel('Amplitude (a.u.)')
        self.FFTPlot.set_title('FFT')
        self.FFTPlot.relim()
        self.FFTPlot.autoscale(True)

    def repaint(self):
         self.canvas.draw()

    def coordPrint(self,e):
        print "mouse clicked"
        print e.xdata
        print e.ydata
