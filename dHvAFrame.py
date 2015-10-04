#!/usr/bin/env python
import wx
import os
import numpy as np
import netCDF4
import matplotlib
matplotlib.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
from matplotlib.pyplot import gcf, setp
from matplotlib.figure import Figure

class dHvAFrame(wx.Frame):
    #"""this creates the frame for the whole program"""
    def __init__(self, *args, **kwargs):
        #initialize all the attributes used later 
        self.dirname=''
        self.varnames =['SampleNumber','CurrentT','CurrentH','A1X','B1X','C1X','D1X','A1Y','B1Y','C1Y','D1Y','A1R','B1R','C1R','D1R','A2X','B2X','C2X','D2X','A2Y','B2Y','C2Y','D2Y','A2R','B2R','C2R','D2R','A3X','B3X','C3X','D3X','A3Y','B3Y','C3Y','D3Y','A3R','B3R','C3R','D3R','A4X','B4X','C4X','D4X','A4Y','B4Y','C4Y','D4Y','A4R','B4R','C4R','D4R','A5X','B5X','C5X','D5X','A5Y','B5Y','C5Y','D5Y','A5R','B5R','C5R','D5R','A6X','B6X','C6X','D6X','A6Y','B6Y','C6Y','D6Y','A6R','B6R','C6R','D6R','EVoltage','FVoltage','GVoltage','HVoltage']
        self.Data_comboBox=[]
        
        #same initialization as wx.Frame
        wx.Frame.__init__(self,*args,**kwargs)

   
        #setting up the menu
        filemenu=wx.Menu()
        menuOpen = filemenu.Append(wx.ID_OPEN,"OPEN","Open a data file")
        menuExit = filemenu.Append(wx.ID_EXIT, "EXIT", "Terminate the Program")

        #Creating the menu bar and status bar
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu,"File")
        self.SetMenuBar(menuBar)
        self.CreateStatusBar()
        
        #Events for menu
        self.Bind(wx.EVT_MENU, self.OnOpen, menuOpen)
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)

        #set up toolbar
        tb = self.CreateToolBar(wx.TB_HORIZONTAL | wx.NO_BORDER | wx.TB_FLAT)
        tsize = (24,24)
        open_bmp = wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_TOOLBAR, tsize)
        save_bmp = wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_TOOLBAR,tsize)
        tb.SetToolBitmapSize(tsize)

        #Events on toolbar
        tb.AddLabelTool(10,'Open',open_bmp)
        self.Bind(wx.EVT_TOOL,self.OnOpen,id=10)

        tb.AddLabelTool(20,'Save',save_bmp)
        self.Bind(wx.EVT_TOOL,self.OnSave,id=20)

       #set up plot windows
        self.plotWindow = plotWindow(self)

        #Sizers for the comboBoxes 
        self.comboBox_box = wx.StaticBox(self,-1,'Select Data Arrays')
        self.comboBox_bsizer = wx.StaticBoxSizer(self.comboBox_box, wx.VERTICAL)

        #set up controls. Dropdown menu for selecting data
        # 0 = x data, 1 = in phase y, 2 = outphase y
        comboBox_text = ['X','in-phase Y','out-phase Y']
        for i in range(0,3):
            self.Data_comboBox.append(wx.ComboBox(self,choices=self.varnames,style=wx.CB_READONLY))
            tmp_text = wx.StaticText(self,-1,comboBox_text[i])
            #self.ComboBoxSizer.Add(self.Data_comboBox[i],1,wx.EXPAND | wx.ALIGN_CENTER)
            self.comboBox_bsizer.Add(tmp_text,0,wx.ALIGN_LEFT)
            self.comboBox_bsizer.Add(self.Data_comboBox[i],1,wx.EXPAND | wx.ALIGN_CENTER)


        #set up controls 

        #min and max plot range
        self.rangeBox = wx.StaticBox(self,-1,'Select the Data Range of Interest')
        self.rangeBox_sizer = wx.StaticBoxSizer(self.rangeBox,wx.HORIZONTAL)

        self.minH_Ctrl = wx.SpinCtrlDouble(self,value='0.0',min=0.0,max=16.0,inc=0.5)
        self.minH_Ctrl.SetDigits(2)
        self.rangeBox_sizer.Add(wx.StaticText(self,-1,'min'),0,wx.ALIGN_LEFT)
        self.rangeBox_sizer.Add(self.minH_Ctrl,1,wx.EXPAND | wx.ALIGN_CENTER)

        self.maxH_Ctrl = wx.SpinCtrlDouble(self,value='16.0',min=0.0,max=16.0,inc=0.5)
        self.maxH_Ctrl.SetDigits(2)
        self.rangeBox_sizer.Add(wx.StaticText(self,-1,'max'),0,wx.ALIGN_LEFT)
        self.rangeBox_sizer.Add(self.maxH_Ctrl,1,wx.EXPAND | wx.ALIGN_CENTER)

        #Set up events 
        self.Bind(wx.EVT_SPINCTRLDOUBLE,self.minH_Change,self.minH_Ctrl)
        self.Bind(wx.EVT_SPINCTRLDOUBLE,self.maxH_Change,self.maxH_Ctrl)

        #set up nested control sizers
        self.ctrlSizer = wx.BoxSizer(wx.VERTICAL)
        self.ctrlSizer.Add(self.rangeBox_sizer,0,wx.EXPAND,border=5)
        self.ctrlSizer.Add(self.comboBox_bsizer,0,wx.EXPAND,border=5)

       #set up final sizers
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(self.plotWindow,1,wx.EXPAND)
        #self.sizer.Add(self.ComboBoxSizer,0,wx.EXPAND,border=5)
        self.sizer.Add(self.ctrlSizer,0,wx.EXPAND,border=5)

        #Layout sizers
        self.SetSizer(self.sizer)     
        self.SetAutoLayout(1)
        self.sizer.Fit(self)
        self.Show()

    def OnExit(self,e):
        self.Close(True)  # Close the frame.

    def OnOpen(self,e):
     #""" Open a file"""
        dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", "*.nc", wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetFilename()
            self.dirname = dlg.GetDirectory()
            self.data_file = netCDF4.Dataset(os.path.join(self.dirname,self.filename), 'r')
            #f = open(os.path.join(self.dirname, self.filename), 'r')
            self.ncattr = self.data_file.ncattrs()   # dictionary of attribute
	    self.vardict = self.data_file.variables   # dictionary of variables
	    self.varnames = self.vardict.keys()    # list of variable
            #update the choices available to the comboBox
            for i in range(0,3):
                self.Data_comboBox[i].Clear()
                for ii in range(len(self.varnames)):
                    self.Data_comboBox[i].Append(self.varnames[ii])
        dlg.Destroy()

    def OnSave(self,e):
        pass

    def minH_Change(self,e):
        self.plotWindow.xmin = self.minH_Ctrl.GetValue()
        self.plotWindow.draw()
        self.plotWindow.repaint()

    def maxH_Change(self,e):
        self.plotWindow.xmax = self.maxH_Ctrl.GetValue()
        self.plotWindow.draw()
        self.plotWindow.repaint()


class plotWindow(wx.Window):
    def __init__(self, *args, **kwargs):
        wx.Window.__init__(self,*args,**kwargs)
        self.figure=Figure()
        self.xmin=-10
        self.xmax=20
        self.canvas = FigureCanvasWxAgg(self, -1, self.figure)
        self.draw()
    
    def draw(self):
        #test plots
        x1 = np.linspace(self.xmin,self.xmax,100)
        y1 = np.power(x1,2)
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
        self.canvas.draw()


#class dHvA_App(wx.App):
#    def onInit(self):
#        self.frame = dHvAFrame(parent = None,title='dHvA Analyser',size=(640,480))
#        self.frame.Show()
#        return True
#
