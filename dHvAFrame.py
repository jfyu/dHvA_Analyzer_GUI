#!/usr/bin/env python
import wx
import os
import numpy as np
import netCDF4
from plotWindow import *
import dHvA_Util
from FFTPanel import *
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
        self.phase = 0
        self.xmin = 0
        self.xmax = 16
        self.despikeKernel = 15
        self.despikeThreshold = 350
        self.despikeRepeat = 12
        # self.despikeLvl = 2
        # self.despikeWaveType = 'coif2'
        # self.despikeWaveMode = 'sym'
        self.smoothWinType = 'hamming'
        self.winlens = 30
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
        #self.CreateStatusBar()
        
        #Events for menu
        self.Bind(wx.EVT_MENU, self.OnOpen, menuOpen)
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)

        #set up toolbar
        tb = self.CreateToolBar(wx.TB_HORIZONTAL | wx.NO_BORDER | wx.TB_FLAT)
        tsize = (24,24)
        open_bmp = wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_TOOLBAR, tsize)
        #save_bmp = wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_TOOLBAR,tsize)
        tb.SetToolBitmapSize(tsize)

        #Events on toolbar
        tb.AddLabelTool(10,'Open',open_bmp)
        self.Bind(wx.EVT_TOOL,self.OnOpen,id=10)

        #tb.AddLabelTool(20,'Save',save_bmp)
        #self.Bind(wx.EVT_TOOL,self.OnSave,id=20)

       #set up plot windows
        self.plotWindow = plotWindow(self)
        self.FFTPanel = FFTPanel(self)

        #sizer for file
        self.fileBox = wx.StaticBox(self,-1,'File Name')
        self.fileBox_sizer = wx.StaticBoxSizer(self.fileBox,wx.VERTICAL)
        
        self.fileNameCtrl = wx.TextCtrl(self,-1,'None',style=wx.TE_READONLY)
        self.fileBox_sizer.Add(self.fileNameCtrl,1,wx.EXPAND|wx.ALIGN_CENTER)

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
            self.comboBox_bsizer.Add(self.Data_comboBox[i],0,wx.EXPAND | wx.ALIGN_CENTER)

        #setup events
        self.Bind(wx.EVT_COMBOBOX, self.setXdata,self.Data_comboBox[0])
        self.Bind(wx.EVT_COMBOBOX, self.setInYdata,self.Data_comboBox[1])
        self.Bind(wx.EVT_COMBOBOX, self.setOutYdata,self.Data_comboBox[2])

        #set phase
        self.phaseBox = wx.StaticBox(self,-1,'Choose Phase')
        self.phaseBox_sizer = wx.StaticBoxSizer(self.phaseBox,wx.HORIZONTAL)

        self.phase_Ctrl = wx.SpinCtrl(self,min=0,max=360,initial=0 )
        self.phaseBox_sizer.Add(wx.StaticText(self,-1,'Phase Angle (deg)'),0,wx.ALIGN_LEFT)
        self.phaseBox_sizer.Add(self.phase_Ctrl,1,wx.EXPAND | wx.ALIGN_CENTER)

        #set up events
        self.Bind(wx.EVT_SPINCTRL, self.phase_Change, self.phase_Ctrl)
 
#         #Choose in or out of phase Y
#         self.YChooseBox = wx.StaticBox(self,-1,'Choose Data to Analyze')
#         self.YChooseBox_sizer = wx.StaticBoxSizer(self.YChooseBox,wx.HORIZONTAL)

#         self.inYRadioButton = wx.RadioButton(self,-1,'In Phase Y',style=wx.RB_GROUP)
#         self.outYRadioButton = wx.RadioButton(self,-1,'Out Phase Y')
        
#         self.YChooseBox_sizer.Add(self.inYRadioButton,wx.ALIGN_LEFT)
#         self.YChooseBox_sizer.Add(self.outYRadioButton,wx.ALIGN_LEFT)

        #set up controls 
        
        #min and max plot range
        self.rangeBox = wx.StaticBox(self,-1,'Select the Data Range of Interest')
        self.rangeBox_sizer = wx.StaticBoxSizer(self.rangeBox,wx.HORIZONTAL)

        self.minH_Ctrl = wx.SpinCtrlDouble(self,value='0.0',min=0.0,max=18.0,inc=0.5)
        self.minH_Ctrl.SetDigits(2)
        self.rangeBox_sizer.Add(wx.StaticText(self,-1,'min'),0,wx.ALIGN_LEFT)
        self.rangeBox_sizer.Add(self.minH_Ctrl,1,wx.EXPAND | wx.ALIGN_CENTER)

        self.maxH_Ctrl = wx.SpinCtrlDouble(self,value='15.9',min=0.0,max=18.0,inc=0.5)
        self.maxH_Ctrl.SetDigits(2)
        self.rangeBox_sizer.Add(wx.StaticText(self,-1,'max'),0,wx.ALIGN_LEFT)
        self.rangeBox_sizer.Add(self.maxH_Ctrl,1,wx.EXPAND | wx.ALIGN_CENTER)

        #Set up events 
        self.Bind(wx.EVT_SPINCTRLDOUBLE,self.minH_Change,self.minH_Ctrl)
        self.Bind(wx.EVT_SPINCTRLDOUBLE,self.maxH_Change,self.maxH_Ctrl)

        #Polynomial BG subtraction
        self.polyBox = wx.StaticBox(self,-1,'Polynomial Background Subtraction (default ON), Select Highest Order')
        self.polyBox_sizer = wx.StaticBoxSizer(self.polyBox,wx.VERTICAL)

        self.polyButton = wx.CheckBox(self,-1,'ON')
        self.polyButton.SetValue(True)

        self.polyOrder_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.polyOrderRadioButton=[]
        self.polyOrderRadioButton.append(wx.RadioButton(self,-1,str(1),style=wx.RB_GROUP)) #new group of radio buttons
        self.polyOrder_sizer.Add(self.polyOrderRadioButton[0],1,wx.EXPAND|wx.ALIGN_CENTER)
        for i in range(1,6):
            self.polyOrderRadioButton.append(wx.RadioButton(self,-1,str(i+1)))
            self.polyOrder_sizer.Add(self.polyOrderRadioButton[i],1,wx.EXPAND | wx.ALIGN_CENTER)
        #for j in range(0,3):
        #    self.polyOrderCheckBox[j].SetValue(True)
        self.polyOrderRadioButton[2].SetValue(True)
        self.polyBox_sizer.Add(self.polyButton,0,wx.ALIGN_LEFT)
        self.polyBox_sizer.Add(self.polyOrder_sizer,0,wx.EXPAND)

        #despike 
        self.despikeBox = wx.StaticBox(self,-1,'Remove Spike (default ON)')
        self.despikeBox_sizer = wx.StaticBoxSizer(self.despikeBox,wx.VERTICAL)

        self.despikeButton = wx.CheckBox(self,-1,'ON')
        self.despikeButton.SetValue(True)

        # self.despike_method_sizer = wx.BoxSizer(wx.HORIZONTAL)
        # self.despikeMethodRadioButton=[]
        # self.despikeMethodRadioButton.append(wx.RadioButton(self,-1,'Median Filter Method',style=wx.RB_GROUP))
        # self.despike_method_sizer.Add(self.despikeMethodRadioButton[0],1,wx.EXPAND|wx.ALIGN_CENTER)
        # self.despikeMethodRadioButton.append(wx.RadioButton(self,-1,'Wavelet Filter Method'))
        # self.despike_method_sizer.Add(self.despikeMethodRadioButton[1],1,wx.EXPAND|wx.ALIGN_CENTER)
        # self.despikeMethodRadioButton[0].SetValue(True)

        #self.despikeMedianBox = wx.StaticBox(self,-1,'Median Filter Method')
        #self.despikeMedianBox_sizer = wx.StaticBoxSizer(self.despikeMedianBox,wx.VERTICAL)

        self.despike_median_sizer1 = wx.BoxSizer(wx.VERTICAL)
        self.despike_kernel_ctrl = wx.SpinCtrl(self,value='15',min=1,max=100001)
        self.despike_median_sizer1.Add(wx.StaticText(self,-1,'Median Filter Kernel Size (odd integer)  '),0,wx.ALIGN_LEFT)
        self.despike_median_sizer1.Add(self.despike_kernel_ctrl,1,wx.EXPAND | wx.ALIGN_LEFT)

        self.despike_median_sizer2 = wx.BoxSizer(wx.VERTICAL)
        self.despike_threshold_ctrl = wx.SpinCtrl(self,value='350',min=0,max=1000000)
        self.despike_median_sizer2.Add(wx.StaticText(self,-1,'Spike Threshold (%)  '),0,wx.ALIGN_LEFT)
        self.despike_median_sizer2.Add(self.despike_threshold_ctrl,1,wx.EXPAND | wx.ALIGN_LEFT)
        
        self.despike_median_sizer3 = wx.BoxSizer(wx.VERTICAL)
        self.despike_repeat_ctrl = wx.SpinCtrl(self,value='12',min=0,max=1000000)
        self.despike_median_sizer3.Add(wx.StaticText(self,-1,'# of passes'),0,wx.ALIGN_LEFT)
        self.despike_median_sizer3.Add(self.despike_repeat_ctrl,1,wx.EXPAND | wx.ALIGN_LEFT)
        



        self.despike_median_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.despike_median_sizer.Add(self.despike_median_sizer1,0,wx.ALIGN_LEFT)
        self.despike_median_sizer.Add(self.despike_median_sizer2,0,wx.ALIGN_LEFT)
        self.despike_median_sizer.Add(self.despike_median_sizer3,0,wx.ALIGN_LEFT)

        #self.despikeMedianBox_sizer.Add(self.despike_median_sizer,0,wx.EXPAND)
        # for wavelet filtering
        # self.despikeWaveletBox = wx.StaticBox(self,-1,'Wavelet Filter Method')
        # self.despikeWaveletBox_sizer = wx.StaticBoxSizer(self.despikeWaveletBox,wx.VERTICAL)

        # self.despike_wavelet_sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        # self.despike_lvls_ctrl = wx.SpinCtrl(self,value='2',min=0,max=10)
        # self.despike_wavelet_sizer1.Add(wx.StaticText(self,-1,'Wavelet Filter Level'),0,wx.ALIGN_LEFT)
        # self.despike_wavelet_sizer1.Add(self.despike_lvls_ctrl,1,wx.EXPAND | wx.ALIGN_LEFT)

        # self.despike_wavelet_sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        # wavelet_names = ['haar','coif1', 'coif2', 'coif3', 'coif4', 'coif5'] #use one family
        # self.despike_type_ctrl = wx.ComboBox(self,choices=wavelet_names,style=wx.CB_READONLY)
        # self.despike_type_ctrl.SetValue('coif2')
        # self.despike_wavelet_sizer2.Add(wx.StaticText(self,-1,'Wavelet Type'),0,wx.EXPAND | wx.ALIGN_LEFT)
        # self.despike_wavelet_sizer2.Add(self.despike_type_ctrl,1,wx.EXPAND | wx.ALIGN_LEFT)

        # self.despike_wavelet_sizer3 = wx.BoxSizer(wx.HORIZONTAL)
        # wavelet_modes = ['sym','zpd','cpd','ppd','sp1','per']#for definitions see pywavelet documentation
        # self.despike_mode_ctrl = wx.ComboBox(self,choices=wavelet_modes,style=wx.CB_READONLY)
        # self.despike_mode_ctrl.SetValue('sym')
        # self.despike_wavelet_sizer3.Add(wx.StaticText(self,-1,'Signal Extension Modes'),0,wx.EXPAND | wx.ALIGN_LEFT)
        # self.despike_wavelet_sizer3.Add(self.despike_mode_ctrl,1,wx.EXPAND|wx.ALIGN_LEFT)
        
        # #self.despikeWaveletBoxsizer = wx.BoxSizer(wx.HORIZONTAL)
        # self.despikeWaveletBox_sizer.Add(self.despike_wavelet_sizer1,0,wx.EXPAND)
        # self.despikeWaveletBox_sizer.Add(self.despike_wavelet_sizer2,0,wx.EXPAND)
        # self.despikeWaveletBox_sizer.Add(self.despike_wavelet_sizer3,0,wx.EXPAND)

        self.despikeBox_sizer.Add(self.despikeButton,0,wx.ALIGN_LEFT)
        self.despikeBox_sizer.Add(self.despike_median_sizer,0,wx.EXPAND)
        #self.despikeBox_sizer.Add(self.despike_method_sizer,0,wx.EXPAND)
        #self.despikeBox_sizer.Add(self.despikeMedianBox_sizer,0,wx.EXPAND)
        #self.despikeBox_sizer.Add(self.despikeWaveletBox_sizer,0,wx.EXPAND)
        #self.despikeBox_sizer.Add(self.despike_sizer,0,wx.EXPAND)

        #despike events
        self.Bind(wx.EVT_SPINCTRL,self.despikeKernel_value, self.despike_kernel_ctrl)
        self.Bind(wx.EVT_SPINCTRL,self.despikeThreshold_value, self.despike_threshold_ctrl)
        self.Bind(wx.EVT_SPINCTRL,self.despikeRepeatFunction,self.despike_repeat_ctrl)
        # self.Bind(wx.EVT_SPINCTRL,self.despikeLevel,self.despike_lvls_ctrl)
        # self.Bind(wx.EVT_SPINCTRL,self.despikeType,self.despike_type_ctrl)
        # self.Bind(wx.EVT_SPINCTRL,self.despikeMode,self.despike_mode_ctrl)

        #Smooth, Interpolate and FFT controls
        self.smoothFFTBox = wx.StaticBox(self,-1,'Smooth (default OFF) and Windowing (default ON)')
        self.smoothFFTBox_sizer = wx.StaticBoxSizer(self.smoothFFTBox,wx.VERTICAL)

        self.smoothFFT_sizer = wx.BoxSizer(wx.VERTICAL)
        windowType_list = ['flat', 'hanning', 'hamming', 'bartlett', 'blackman', 'kaiser']
        self.smoothFFT_winCtrl = wx.ComboBox(self,choices=windowType_list,style=wx.CB_READONLY)
        self.smoothFFT_winCtrl.SetValue('hamming')

        self.smoothFFT_winlenCtrl = wx.SpinCtrl(self,min=3,max=1000,initial=30)

        self.smoothButton = wx.CheckBox(self,-1,'Smooth ON')
        self.smoothButton.SetValue(False)
        self.windowButton = wx.CheckBox(self,-1,'Window ON')
        self.windowButton.SetValue(True)
 
        self.smoothFFTBox_sizer.Add(self.smoothButton,1,wx.EXPAND | wx.ALIGN_CENTER)
        self.smoothFFTBox_sizer.Add(self.windowButton,1,wx.EXPAND | wx.ALIGN_CENTER)

        self.smoothFFT_ctrlsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.smoothFFT_ctrlsizer.Add(wx.StaticText(self,-1,'Window Type'),0,wx.EXPAND|wx.ALIGN_CENTER)
        self.smoothFFT_ctrlsizer.Add(self.smoothFFT_winCtrl,1,wx.EXPAND | wx.ALIGN_CENTER)
        self.smoothFFT_ctrlsizer.Add(wx.StaticText(self,-1,'Window Length'),0,wx.EXPAND|wx.ALIGN_CENTER)
        self.smoothFFT_ctrlsizer.Add(self.smoothFFT_winlenCtrl,1,wx.EXPAND|wx.ALIGN_CENTER)

        self.smoothFFTBox_sizer.Add(self.smoothFFT_ctrlsizer,0,wx.EXPAND)

        #SmoothEvent
        self.Bind(wx.EVT_COMBOBOX,self.smoothType,self.smoothFFT_winCtrl)
        self.Bind(wx.EVT_SPINCTRL,self.setWinLens,self.smoothFFT_winlenCtrl)
       
        #Apply button
        self.applyButton = wx.Button(self,wx.ID_APPLY)
        self.PhaseFinderButton = wx.Button(self,-1,'Auto Phase')
        self.buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.buttonSizer.Add(self.applyButton,0,wx.ALIGN_CENTER)
        self.buttonSizer.Add(self.PhaseFinderButton,0,wx.ALIGN_CENTER)

        #Apply button events
        self.Bind(wx.EVT_BUTTON,self.applyChanges,self.applyButton)
        self.Bind(wx.EVT_BUTTON,self.AutoPhase,self.PhaseFinderButton)
        
        #set up nested control sizers
        self.ctrlSizer = wx.BoxSizer(wx.VERTICAL)
        self.ctrlSizer.Add(self.fileBox_sizer,0,wx.EXPAND,border=5)
        self.ctrlSizer.Add(self.comboBox_bsizer,0,wx.EXPAND,border=5)
        self.ctrlSizer.Add(self.rangeBox_sizer,0,wx.EXPAND,border=5)
        self.ctrlSizer.Add(self.phaseBox_sizer,0,wx.EXPAND,border=5)
        #self.ctrlSizer.Add(self.YChooseBox_sizer,0,wx.EXPAND,border=5)
        self.ctrlSizer.Add(self.polyBox_sizer,0,wx.EXPAND,border=5)
        self.ctrlSizer.Add(self.despikeBox_sizer,0,wx.EXPAND,border=5)
        self.ctrlSizer.Add(self.smoothFFTBox_sizer,0,wx.EXPAND,border=5)
        self.ctrlSizer.Add(self.buttonSizer,0,wx.EXPAND,border=5)
       
       #set up final sizers
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(self.plotWindow,1,wx.GROW)
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
        self.fileNameCtrl.SetValue(self.filename)
        if self.Data_comboBox[0].GetValue() != "":
            #In case you want combo box to stay the same while selecting a different file
            self.setXdata(self)
            self.setInYdata(self)
            self.setOutYdata(self)
    #def OnSave(self,e):
    #    pass

    def AutoPhase(self,e):
        if self.FFTPanel.Freq_List[0].GetValue() == 0:
                message3 = "You have not chosen a peak yet! Click on a peak in FFT Panel"
                caption2 = "Error!"
                warningDlg3 = wx.MessageDialog(self,message3,caption2,wx.OK|wx.ICON_ERROR)
                warningDlg3.ShowModal()
                warningDlg3.Destroy()
        else:
            progressDlg = wx.ProgressDialog("Auto Phase Progress","Auto Phase Engaged, Working...",maximum = 175,parent = self,style = 0 | wx.PD_APP_MODAL | wx.PD_ELAPSED_TIME | wx.PD_REMAINING_TIME |wx.PD_AUTO_HIDE )
            max_signal = []
            for i in range(0,len(self.FFTPanel.Freq_List)):
                max_signal.append(0)
            for phase_tmp in np.arange(0,180,5):
                wx.MilliSleep(250)
                wx.Yield()
                progressDlg.Update(phase_tmp)
                self.phase = phase_tmp
                self.applyChanges(self)
                fft_freq = self.FFTPanel.FreqY
                fft_Signal = self.FFTPanel.FFT_SignalY
                for i in range(0,len(self.FFTPanel.Freq_List)):
                    if self.FFTPanel.Freq_List[i].GetValue()==0:
                        break
                    else:
                        range_min = self.FFTPanel.Freq_List[i].GetValue()-50 #within 50T on either side 
                        range_max = self.FFTPanel.Freq_List[i].GetValue()+50
                        freq_tmp, signal_tmp = dHvA_Util.select_data_one(fft_freq,fft_Signal,range_min,range_max)
                        ind = np.argmax(np.array(signal_tmp))
                        if signal_tmp[ind] > max_signal[i]:
                            #print str(signal_tmp[ind])+'max signal is '+str(max_signal[i])
                            max_signal[i] = signal_tmp[ind]
                            #Set Real Frequency
                            self.FFTPanel.Calculated_List[i*3].SetValue(str(int(freq_tmp[ind])))
                            #Set Best Phase
                            self.FFTPanel.Calculated_List[i*3+1].SetValue(str(phase_tmp))
                            #set Best Amp
                            self.FFTPanel.Calculated_List[i*3+2].SetValue('%.3e' % max_signal[i])
                        self.phase_Ctrl.SetValue(175)
            progressDlg.Destroy() 
    def setXdata(self,e):
        #try:
        self.xdata = self.vardict[self.Data_comboBox[0].GetValue()]
        #except AttributeError:
        #    message="Select a File first!"
        #    caption = "Error!"
        #    warningDlg = wx.MessageDialog(self,message, caption, wx.OK|wx.ICON_ERROR)
        #    warningDlg.ShowModal()
        #    warningDlg.Destroy()
        #    self.OnOpen(self)

        
    def setInYdata(self,e):
        #try:
        self.InYdata = self.vardict[self.Data_comboBox[1].GetValue()]
        #except AttributeError:
        #    message="Select a File first!"
        #    caption = "Error!"
        #    warningDlg = wx.MessageDialog(self,message, caption, wx.OK|wx.ICON_ERROR)
        #    warningDlg.ShowModal()
        #    warningDlg.Destroy()
        #    self.OnOpen(self)


    def setOutYdata(self,e):
        #try:
        self.OutYdata = self.vardict[self.Data_comboBox[2].GetValue()]
        #except AttributeError:
        #    message="Select a File first!"
        #    caption = "Error!"
        #    warningDlg = wx.MessageDialog(self,message, caption, wx.OK|wx.ICON_ERROR)
        #    warningDlg.ShowModal()
        #    warningDlg.Destroy()
        #    self.OnOpen(self)

    def phase_Change(self,e):
        self.phase = self.phase_Ctrl.GetValue()

    def minH_Change(self,e):
        self.xmin = self.minH_Ctrl.GetValue()
        #self.plotWindow.draw()
        #self.plotWindow.repaint()

    def maxH_Change(self,e):
        self.xmax = self.maxH_Ctrl.GetValue()
        #self.plotWind`ow.draw()
        #self.plotWindow.repaint()
    
    def despikeKernel_value(self,e):
        if self.despike_kernel_ctrl.GetValue() % 2 != 0:
            self.despikeKernel = self.despike_kernel_ctrl.GetValue()
        
        else:
            message2 = "Kernel has to be an odd integer! Reset to the nearest odd integer."
            caption2 = "Error!"
            warningDlg2 = wx.MessageDialog(self,message2,caption2,wx.OK|wx.ICON_ERROR)
            warningDlg2.ShowModal()
            warningDlg2.Destroy()
            tmp = self.despike_kernel_ctrl.GetValue()
            self.despike_kernel_ctrl.SetValue(tmp+1)
            self.despikeKernel = tmp+1
        print str(self.despikeKernel) 
    def despikeThreshold_value(self,e):
        self.despikeThreshold = self.despike_threshold_ctrl.GetValue()

    def despikeRepeatFunction(self,e):
        self.despikeRepeat = self.despike_repeat_ctrl.GetValue()

    #for wavelet filter
    # def despikeLevel(self,e):
        # self.despikeLvl=self.despike_lvls_ctrl.GetValue()

    # def despikeType(self,e):
        # self.despikeWaveType = self.despike_type_ctrl.GetValue()

    # def despikeMode(self,e):
        # self.despikeWaveMode = self.despike_mode_ctrl.GetValue()
    
    def smoothType(self,e):
        self.smoothWinType = self.smoothFFT_winCtrl.GetValue()

    def setWinLens(self,e):
        self.winlens = self.smoothFFT_winlenCtrl.GetValue()

    def applyChanges(self,e):
        if self.data_file != None:
            #select data based on the Range of Interest 
            self.plotWindow.x,self.plotWindow.InY,self.plotWindow.OutY = dHvA_Util.select_data(self.xdata,self.InYdata,self.OutYdata,self.xmin,self.xmax)
            if len(self.plotWindow.x)<100:
                message="Very little or no data in selected range!"
                caption = "Error!"
                warningDlg = wx.MessageDialog(self,message, caption, wx.OK|wx.ICON_ERROR)
                warningDlg.ShowModal()
                warningDlg.Destroy()
            #Find phase and find signal
            #self.InY, self.outY = dHvA_Util.find_angle(self.plotWindow.InY,self.plotWindow.OutY)

            #Get phase
            self.plotWindow.phase = self.phase
        # if self.inYRadioButton.GetValue() == True:
        #     self.plotWindow.inYState = True
        #     self.plotWindow.outYState = False
        # if self.outYRadioButton.GetValue() == True:
        #     self.plotWindow.outYState=True
        #     self.plotWindow.inYState = True
        if self.polyButton.GetValue() == True:
            self.plotWindow.polyOn = True
            self.plotWindow.polyOrder=[]
            for i in range(0,6):
                if self.polyOrderRadioButton[i].GetValue() == True:
                    self.plotWindow.polyOrder=i+1
        else:
            self.plotWindow.polyOrder = [0]
            self.plotWindow.polyOn = False

        if self.despikeButton.GetValue() == True:
            self.plotWindow.despikeOn = True

            #reset the conditions
            # self.plotWindow.medianfilterOn=False
            # self.plotWindow.waveletOn = False
            # self.plotWindow.despikeLength=False
 
            #if self.despikeMethodRadioButton[0].GetValue() == True:
            #self.plotWindow.medianfilterOn = True
            self.plotWindow.despikeKernel = self.despikeKernel
            self.plotWindow.despikeThreshold = self.despikeThreshold
            self.plotWindow.despikeRepeat = self.despikeRepeat
           #  elif self.despikeMethodRadioButton[1].GetValue() == True:
                # self.plotWindow.waveletOn = True
                # self.plotWindow.decompLevel = self.despikeLvl
                # self.plotWindow.waveletType = self.despikeWaveType
                # self.plotWindow.waveletMode = self.despikeWaveMode
        else:
            self.plotWindow.despikeOn=False
                   
        if self.windowButton.GetValue()==True:
            self.plotWindow.windowOn = True
            self.plotWindow.smoothWinType = self.smoothWinType
            self.plotWindow.winlens = self.winlens
        else:
            self.plotWindow.windowOn=False
        
        if self.smoothButton.GetValue()==True:
            self.plotWindow.smoothOn=True
            self.plotWindow.smoothWinType = self.smoothWinType
            self.plotWindow.winlens = self.winlens
        else:
            self.plotWindow.smoothOn=False
        #else:
            #self.smoothOn = False
            #print self.winlens
        #self.plotWindow.xmin=self.xmin
        #self.plotWindow.xmax=self.xmax
        self.plotWindow.draw()
        self.plotWindow.repaint()
        # if self.plotWindow.despikeLength:
            # DespikeMessage = "Reconstructed Wavelet Length Does Not Match the Original. Dropped the extra length elements."
            # DespikeCaption = "Warning"
            # despikeDlg = wx.MessageDialog(self,DespikeMessage,DespikeCaption,wx.OK|wx.ICON_WARNING)
            # despikeDlg.ShowModal()
            # despikeDlg.Destroy()
        self.FFTPanel.Y = self.plotWindow.windowed_dataY
        self.FFTPanel.delta_inv_x = self.plotWindow.delta_inv_x
        self.FFTPanel.draw()
        #self.FFTPanel.repaint()
        self.FFTPanel.repaint()
        self.FFTPanel.Show(True)



