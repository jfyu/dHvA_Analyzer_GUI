#!/usr/bin/env python
import wx
import os
import numpy as np
import netCDF4
from plotWindow import *
import dHvA_Util

class dHvAFrame(wx.Frame):
    #"""this creates the frame for the whole program"""
    def __init__(self, *args, **kwargs):
        #initialize all the attributes used later 
        self.dirname=''
        self.varnames =['SampleNumber','CurrentT','CurrentH','A1X','B1X','C1X','D1X','A1Y','B1Y','C1Y','D1Y','A1R','B1R','C1R','D1R','A2X','B2X','C2X','D2X','A2Y','B2Y','C2Y','D2Y','A2R','B2R','C2R','D2R','A3X','B3X','C3X','D3X','A3Y','B3Y','C3Y','D3Y','A3R','B3R','C3R','D3R','A4X','B4X','C4X','D4X','A4Y','B4Y','C4Y','D4Y','A4R','B4R','C4R','D4R','A5X','B5X','C5X','D5X','A5Y','B5Y','C5Y','D5Y','A5R','B5R','C5R','D5R','A6X','B6X','C6X','D6X','A6Y','B6Y','C6Y','D6Y','A6R','B6R','C6R','D6R','EVoltage','FVoltage','GVoltage','HVoltage']
        self.Data_comboBox=[]
        self.data_file=None
        self.xdata = None
        self.InYdata = None
        self.OutYdata = None
        self.xmin = 0
        self.xmax = 16

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

        #setup events
        self.Bind(wx.EVT_COMBOBOX, self.setXdata,self.Data_comboBox[0])
        self.Bind(wx.EVT_COMBOBOX, self.setInYdata,self.Data_comboBox[1])
        self.Bind(wx.EVT_COMBOBOX, self.setOutYdata,self.Data_comboBox[2])
        
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

        #Polynomial BG subtraction
        self.polyBox = wx.StaticBox(self,-1,'Polynomial Background Subtraction (default ON)')
        self.polyBox_sizer = wx.StaticBoxSizer(self.polyBox,wx.VERTICAL)

        self.polyButton = wx.ToggleButton(self,-1,'ON')
        self.polyButton.SetValue(True)

        self.polyOrder_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.polyOrderCheckBox=[]
        for i in range(0,6):
            self.polyOrderCheckBox.append(wx.CheckBox(self,-1,str(i+1)))
            self.polyOrder_sizer.Add(self.polyOrderCheckBox[i],1,wx.EXPAND | wx.ALIGN_CENTER)
        for j in range(0,3):
            self.polyOrderCheckBox[j].SetValue(True)
        self.polyBox_sizer.Add(self.polyButton,0,wx.ALIGN_LEFT)
        self.polyBox_sizer.Add(self.polyOrder_sizer,0,wx.EXPAND)

        #despike 
        self.despikeBox = wx.StaticBox(self,-1,'Remove Spike (default ON)')
        self.despikeBox_sizer = wx.StaticBoxSizer(self.despikeBox,wx.VERTICAL)

        self.despikeButton = wx.ToggleButton(self,-1,'ON')
        self.despikeButton.SetValue(True)

        self.despike_sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        self.despike_lvls_ctrl = wx.SpinCtrl(self,value='2',min=0,max=10)
        self.despike_sizer1.Add(wx.StaticText(self,-1,'Wavelet Filter Level'),0,wx.ALIGN_LEFT)
        self.despike_sizer1.Add(self.despike_lvls_ctrl,1,wx.EXPAND | wx.ALIGN_LEFT)

        self.despike_sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        wavelet_names = ['haar','coif1', 'coif2', 'coif3', 'coif4', 'coif5'] #use one family
        self.despike_type_ctrl = wx.ComboBox(self,choices=wavelet_names,style=wx.CB_READONLY)
        self.despike_sizer2.Add(wx.StaticText(self,-1,'Wavelet Type'),0,wx.EXPAND | wx.ALIGN_RIGHT)
        self.despike_sizer2.Add(self.despike_type_ctrl,1,wx.EXPAND | wx.ALIGN_RIGHT)
        
        self.despike_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.despike_sizer.Add(self.despike_sizer1,0,wx.EXPAND)
        self.despike_sizer.Add(self.despike_sizer2,0,wx.EXPAND)

        self.despikeBox_sizer.Add(self.despikeButton,0,wx.ALIGN_LEFT)
        self.despikeBox_sizer.Add(self.despike_sizer,0,wx.EXPAND)

        #Smooth, Interpolate and FFT controls
        self.smoothFFTBox = wx.StaticBox(self,-1,'Smooth, Interpolate 1/H and FFT')
        self.smoothFFTBox_sizer = wx.StaticBoxSizer(self.smoothFFTBox,wx.VERTICAL)

        self.smoothFFT_sizer = wx.BoxSizer(wx.VERTICAL)
        windowType_list = ['flat', 'hanning', 'hamming', 'bartlett', 'blackman', 'kaiser']
        self.smoothFFT_winCtrl = wx.ComboBox(self,choices=windowType_list,style=wx.CB_READONLY)
        self.smoothFFT_winCtrl.SetValue('hamming')
  
        self.smoothFFT_sizer.Add(wx.StaticText(self,-1,'Window Type'),0,wx.EXPAND|wx.ALIGN_CENTER)
        self.smoothFFT_sizer.Add(self.smoothFFT_winCtrl,1,wx.EXPAND | wx.ALIGN_CENTER)

        self.smoothFFTBox_sizer.Add(self.smoothFFT_sizer,0,wx.EXPAND)
       
        #Apply button
        self.applyButton = wx.Button(self,wx.ID_APPLY)
        self.buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.buttonSizer.Add(self.applyButton,0,wx.ALIGN_RIGHT)

        #Apply button events
        self.Bind(wx.EVT_BUTTON,self.applyChanges,self.applyButton)

        #set up nested control sizers
        self.ctrlSizer = wx.BoxSizer(wx.VERTICAL)
        self.ctrlSizer.Add(self.comboBox_bsizer,0,wx.EXPAND,border=5)
        self.ctrlSizer.Add(self.rangeBox_sizer,0,wx.EXPAND,border=5)
        self.ctrlSizer.Add(self.polyBox_sizer,0,wx.EXPAND,border=5)
        self.ctrlSizer.Add(self.despikeBox_sizer,0,wx.EXPAND,border=5)
        self.ctrlSizer.Add(self.smoothFFTBox_sizer,0,wx.EXPAND,border=5)
        self.ctrlSizer.Add(self.buttonSizer,0,wx.EXPAND,border=5)
       
       #set up final sizers
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(self.plotWindow,0,wx.EXPAND)
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

    def setXdata(self,e):
        self.xdata = self.vardict[self.Data_comboBox[0].GetValue()]
        
    def setInYdata(self,e):
        self.InYdata = self.vardict[self.Data_comboBox[1].GetValue()]

    def setOutYdata(self,e):
        self.OutYdata = self.vardict[self.Data_comboBox[2].GetValue()]

    def minH_Change(self,e):
        self.xmin = self.minH_Ctrl.GetValue()
        #self.plotWindow.draw()
        #self.plotWindow.repaint()

    def maxH_Change(self,e):
        self.xmax = self.maxH_Ctrl.GetValue()
        #self.plotWindow.draw()
        #self.plotWindow.repaint()

    def applyChanges(self,e):
        if self.data_file != None:
            #select data based on the Range of Interest 
            self.plotWindow.x,self.plotWindow.InY,self.plotWindow.OutY = dHvA_Util.select_data(self.xdata,self.InYdata,self.OutYdata,self.xmin,self.xmax)
            try:
                self.plotWindow.InY[0]
            except IndexError:
                message="No Data in Selected Range!"
                caption = "Error!"
                warningDlg = wx.MessageDialog(self,message, caption, wx.OK|wx.ICON_ERROR)
                warningDlg.ShowModal()
                warningDlg.Destroy()
            #Find phase and find signal
            self.InY, self.outY = dHvA_Util.find_angle(self.plotWindow.InY,self.plotWindow.outY)
            #sort the arrays so you can fit the polynomial background
            self.plotWindow.sortedX, self.plotWindow.SortedSignal = dHvA_Util.sort_array(self.x, self.InY)
        if self.polyButton.GetValue() == True:
            self.plotWindow.polyOrder=[]
            for i in range(0,6):
                if self.polyOrderCheckBox[i].GetValue() == True:
                    self.plotWindow.polyOrder.append(i+1)
        #self.plotWindow.xmin=self.xmin
        #self.plotWindow.xmax=self.xmax
        self.plotWindow.draw()
        self.plotWindow.repaint()



