#!/usr/bin/env python
import wx
import numpy as np
import matplotlib
matplotlib.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
from matplotlib.pyplot import gcf, setp
from matplotlib.figure import Figure

class plotWindow(wx.Window):
    def __init__(self, *args, **kwargs):
        wx.Window.__init__(self,*args,**kwargs)
        self.figure=Figure()
        self.x = np.linspace(self.xmin, self.xmax,100)
        self.InY = np.pow(x,2)
        self.OutY = np.pow(x,2)
        self.polyOrder = [1,2,3]
        self.xmin=-10
        self.xmax=20
        self.canvas = FigureCanvasWxAgg(self, -1, self.figure)
        self.draw()
    
    def draw(self):
        #test plots
        x1 = np.linspace(self.xmin,self.xmax,100)
        y1 = []
        for i in range(0,len(self.polyOrder)):
            y1=np.power(x1,self.polyOrder[i])
        x2 = x1
        y2 = np.sin(x2)
        x3 = x1
        y3 = np.exp(x3)
        x4 = x1
        y4 = np.cosh(x4)

        self.subplot1=self.figure.add_subplot(221)
        self.subplot1.plot(x1,y1,linewidth=2)
        self.subplot1.set_title('polynomial')
        self.subplot1.set_xlim([self.xmin,self.xmax])
        
        self.subplot2=self.figure.add_subplot(222)
        self.subplot2.plot(x2,y2,linewidth=2)
        self.subplot2.set_title('sine')
        self.subplot2.set_xlim([self.xmin,self.xmax])

        self.subplot3=self.figure.add_subplot(223)
        self.subplot3.plot(x3,y3,linewidth=2)
        self.subplot3.set_title('exponential')
        self.subplot3.set_xlim([self.xmin,self.xmax])

        self.subplot4=self.figure.add_subplot(224)
        self.subplot4.plot(x4,y4,linewidth=2)
        self.subplot4.set_title('hyperbolic cosine')
        self.subplot4.set_xlim([self.xmin,self.xmax])
    
    def repaint(self):
        del self.subplot1.lines[0] #delete the previous plot in the first subplot
        self.canvas.draw()


#class dHvA_App(wx.App):
#    def onInit(self):
#        self.frame = dHvAFrame(parent = None,title='dHvA Analyser',size=(640,480))
#        self.frame.Show()
#        return True
#
