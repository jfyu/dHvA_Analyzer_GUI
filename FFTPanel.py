import wx
import wx.lib.intctrl
#from FFTWindow import * 
import numpy as np
import matplotlib
matplotlib.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure
from matplotlib.widgets import Cursor
import dHvA_Util
import os
import csv
#from PlotDialog import *

class FFTPanel(wx.Frame):
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self,*args,**kwargs)
        #Toolbar
        #tb = self.CreateToolBar(wx.TB_HORIZONTAL | wx.NO_BORDER | wx.TB_FLAT)
        #tsize = (24,24)
        #save_bmp = wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_TOOLBAR,tsize)
        #tb.SetToolBitmapSize(tsize)

        #menu
        filemenu=wx.Menu()
        #menuSave = filemenu.Append(wx.ID_SAVE,"SAVE","Save a data file")
        menuExit = filemenu.Append(wx.ID_EXIT, "EXIT", "Terminate the Program")

        #plotmenu=wx.Menu()
        #menuLim = plotmenu.Append(wx.NewId(),'Set Axes Limit','sets axes limit')

        #Creating the menu bar and status bar
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu,"File")
        #menuBar.Append(plotmenu,'Plot')
        self.SetMenuBar(menuBar)
        #self.CreateStatusBar()
        
        #Events for menu
        #self.Bind(wx.EVT_MENU, self.OnSave, menuSave)
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
        #self.Bind(wx.EVT_MENU, self.ChangeLimit,menuLim)

        #Events on toolbar
        #tb.AddLabelTool(10,'Save',save_bmp)
        #self.Bind(wx.EVT_TOOL,self.OnSave,id=10)


        #do all the figure plotting things. Reason why we don't do that in a separate class is because the navigation tool bar doesn't like to work
        self.figure=Figure()
        self.x = np.linspace(0.1, 20,183)
        self.Y = np.sin(self.x)
        self.delta_inv_x = 30/100.0
        self.canvas = FigureCanvasWxAgg(self, -1, self.figure)
        self.canvas.mpl_connect('pick_event',self.coordPrint)
        self.draw()

        #canvas tool bar
        self.toolbar = NavigationToolbar2Wx(self.canvas)
        self.toolbar.Realize()
        tw, th = self.toolbar.GetSizeTuple()
        fw, fh = self.canvas.GetSizeTuple()
        self.toolbar.SetSize(wx.Size(fw, th))
        self.toolbar.update()
        self.toolbar.Show()
        
        #Set x an y limits

        #sizers
        self.CanvasSizer = wx.BoxSizer(wx.VERTICAL)
        self.CanvasSizer.Add(self.canvas,1,wx.EXPAND)
        self.CanvasSizer.Add(self.toolbar,0,wx.GROW)


        #add the grid to display the peaks 

        self.tableSizer = wx.BoxSizer(wx.VERTICAL)
        EstPeakSizer = wx.GridBagSizer(11,4)
        EstPeakSizer.Add(wx.StaticText(self,-1,"Est. Freq. "),(0,0))
        EstPeakSizer.Add(wx.StaticText(self,-1,"Real Freq. "),(0,1))
        EstPeakSizer.Add(wx.StaticText(self,-1,"Best Phase "),(0,2))
        EstPeakSizer.Add(wx.StaticText(self,-1,"Best Amp. "),(0,3))
        #EstPeakSizer.Add(wx.TextCtrl(self),(1,1))
        self.Freq_List = []
        self.Calculated_List = []
        for i in range(0,10):
            self.Freq_List.append(wx.lib.intctrl.IntCtrl(self,value = 0,size=(100,-1)))
            EstPeakSizer.Add(self.Freq_List[-1],(i+1,0))
            for j in range(1,4):
                self.Calculated_List.append(wx.TextCtrl(self,-1,"0",size=(100,-1),style=wx.TE_READONLY))
                self.Calculated_List[-1].SetBackgroundColour('Grey')
                self.Calculated_List[-1].SetForegroundColour('White')
                EstPeakSizer.Add(self.Calculated_List[-1],(i+1,j))
 
        #box = wx.BoxSizer()
                # self.DataTable = CustTableGrid(self)#initially two columns and two rows
#         #self.row = 0 #keep track of how many peaks added
        #save button
        # self.saveButton =wx.Button(self,-1,'Save Data')
        # self.Bind(wx.EVT_BUTTON,self.OnSave,self.saveButton)
        #clear table button
        self.clearButton=wx.Button(self,-1,'Clear Table')
        self.Bind(wx.EVT_BUTTON,self.ClearTable,self.clearButton)
        
        #Button Sizer
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        # buttonSizer.Add(self.saveButton,0,wx.ALIGN_CENTRE|wx.ALL|wx.EXPAND)
        buttonSizer.Add(self.clearButton,0,wx.ALIGN_CENTRE|wx.ALL|wx.EXPAND)
        #Change Size Controls`
        LimitBox = wx.StaticBox(self,-1,"Change x-axis Limits")
        LimitBoxSizer = wx.StaticBoxSizer(LimitBox,wx.VERTICAL)

        xbox = wx.BoxSizer(wx.VERTICAL)
        xLowLimLabel = wx.StaticText(self,-1,"x lower limit")
        xHighLimLabel = wx.StaticText(self,-1,"x upper limit")
        xbox.Add(xLowLimLabel,0,wx.ALIGN_CENTRE|wx.ALL)
        xbox.Add(xHighLimLabel,0,wx.ALIGN_CENTRE|wx.ALL)

        xControlBox = wx.BoxSizer(wx.VERTICAL)
        self.xLowLimCtrl = wx.SpinCtrlDouble(self,value='0.00',min=0.00,max=1e10,inc=1)
        self.xHighLimCtrl = wx.SpinCtrlDouble(self,value='20000',min=0.00,max=1e10,inc=1)
        xControlBox.Add(self.xLowLimCtrl,0,wx.ALIGN_CENTRE|wx.ALL)
        xControlBox.Add(self.xHighLimCtrl,0,wx.ALIGN_CENTRE|wx.ALL)

        self.Bind(wx.EVT_SPINCTRLDOUBLE,self.setxLowLim,self.xLowLimCtrl)
        self.Bind(wx.EVT_SPINCTRLDOUBLE,self.setxHighLim,self.xHighLimCtrl)
 
        XallBox = wx.BoxSizer(wx.HORIZONTAL)
        XallBox.Add(xbox,0,wx.ALIGN_CENTRE|wx.ALL,5)
        XallBox.Add(xControlBox,0,wx.ALIGN_CENTRE|wx.ALL,5)
        
        ybox = wx.BoxSizer(wx.VERTICAL)
        yLowLimLabel = wx.StaticText(self,-1,"y lower limit")
        yHighLimLabel = wx.StaticText(self,-1,"y upper limit")
        ybox.Add(yLowLimLabel,0,wx.ALIGN_CENTRE|wx.ALL)
        ybox.Add(yHighLimLabel,0,wx.ALIGN_CENTRE|wx.ALL)

        yControlBox = wx.BoxSizer(wx.VERTICAL)
        self.yLowLimCtrl = wx.SpinCtrlDouble(self,value='0.00',min=0.00,max=1e10,inc=0.00001)
        self.yHighLimCtrl = wx.SpinCtrlDouble(self,value='0.5',min=0.00,max=1e10,inc=0.00001)
        yControlBox.Add(self.yLowLimCtrl,0,wx.ALIGN_CENTRE|wx.ALL)
        yControlBox.Add(self.yHighLimCtrl,0,wx.ALIGN_CENTRE|wx.ALL)

        self.Bind(wx.EVT_SPINCTRLDOUBLE,self.setyLowLim,self.yLowLimCtrl)
        self.Bind(wx.EVT_SPINCTRLDOUBLE,self.setyHighLim,self.yHighLimCtrl)
 
        YallBox = wx.BoxSizer(wx.HORIZONTAL)
        YallBox.Add(ybox,0,wx.ALIGN_CENTRE|wx.ALL,5)
        YallBox.Add(yControlBox,0,wx.ALIGN_CENTRE|wx.ALL,5)
 
        LimitBoxSizer.Add(XallBox,0,wx.ALIGN_CENTRE|wx.ALL,5)
        LimitBoxSizer.Add(YallBox,0,wx.ALIGN_CENTRE|wx.ALL,5)

        self.ChangeButton = wx.Button(self,-1,'Change Axes Limits')
        self.Bind(wx.EVT_BUTTON,self.ChangeLimit,self.ChangeButton)

        LimitBoxSizer.Add(self.ChangeButton,0,wx.ALIGN_CENTRE|wx.ALL,5)
        
        #self.warningText = wx.StaticText(self, -1,'Warning: If you delete any selections in this table, and then continue to select more peaks, you will result in one more empty row. If you delete two selections, you will end up with two empty rows, and so on')
        #self.warningText.Wrap(200)
        #self.tableSizer.Add(self.ChangeButton,0,wx.EXPAND)
        
        self.tableSizer.Add(LimitBoxSizer,0,wx.EXPAND)
        self.tableSizer.Add(EstPeakSizer, 1, wx.ALL|wx.EXPAND, 10)


        #self.tableSizer.Add(self.warningText,0,wx.EXPAND)
        #self.tableSizer.Add(self.DataTable,1,wx.EXPAND)
        self.tableSizer.Add(buttonSizer,0,wx.EXPAND)
        
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(self.CanvasSizer,1,wx.EXPAND)
        self.sizer.Add(self.tableSizer,0,wx.EXPAND)
        self.SetSizer(self.sizer)     
        self.SetAutoLayout(1)
        self.sizer.Fit(self)
        
        self.Centre()
        self.Show()
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.xlim=[0,20000]
        self.ylim=[0,1]
    
    def draw(self):
        self.figure.clf() #clear the figure
        self.FFTPlot = self.figure.add_subplot(111)
        #if len(self.FFTPlot.lines)>0:
        #    for i in range(0,len(self.FFTPlot.lines)):
        #        del self.FFTPlot.lines[0]
        #self.FFTPlot.cla()
        #print len(self.FFTPlot.lines)
        #smooth and window the data
        self.DeltaFreqY = 1/self.delta_inv_x 
        #padd the data
        pad_mult = 10
        zero_matrixY = np.zeros(len(self.Y)*pad_mult/2)
        self.pad_wind_dataY = np.append(self.Y, zero_matrixY)
        # pad_wind_data = np.append(zero_matrix, pad_wind_data)

        self.FreqY, self.FFT_SignalY = dHvA_Util.take_fft(self.pad_wind_dataY, 20, self.DeltaFreqY)
        self.FFTPlot.plot(self.FreqY,self.FFT_SignalY,linewidth=2,color='blue',picker=10)
        self.FFTPlot.set_xlabel('dHvA Frequency (T)')
        self.FFTPlot.set_ylabel('Amplitude (a.u.)')
        self.FFTPlot.set_title('FFT')
        self.FFTPlot.grid(True)
        self.FFTPlot.relim()
        self.FFTPlot.set_xlim([0,10000])
        #self.FFTPlot.set_ylim([0,0.5])
        self.FFTPlot.autoscale(True,axis='y')

        #add cursor to select points
        self.cursor = Cursor(self.FFTPlot,color='black',linewidth=1)

    def repaint(self):
         self.canvas.draw()

    def coordPrint(self,e):
        print "mouse clicked onto data"
        #because there are a lot of indices in one click, use only the first one
        picked_x = e.artist.get_xdata()[e.ind[0]]
        picked_y = e.artist.get_ydata()[e.ind[0]]
        print picked_x, picked_y
        for i in range(0,len(self.Freq_List)):
            if self.Freq_List[i].GetValue() == 0:
                self.Freq_List[i].SetValue(int(picked_x))
                break
        # self.row = self.DataTable.table.GetNumberRows()
        # self.DataTable.table.AppendRow()
        # if self.row != 0:
            # for i in range(0,self.row):
                # if self.DataTable.table.IsEmptyCell(i,0)==True:
                    # self.row = i
                    # break
        # self.DataTable.table.SetValue(self.row,0,picked_x)
        # self.DataTable.table.SetValue(self.row,1,picked_y)
        #print self.row
        #print self.DataTable.table.AppendRow()
        #print self.DataTable.table.DeleteRow()
    
    
    def ChangeLimit(self,e):
        #dlg = PlotDialog(self,-1,'Change x-axis limits',style=wx.DEFAULT_DIALOG_STYLE)
        #dlg.CenterOnScreen()
        #val=dlg.ShowModal()
        #if val == wx.ID_OK:
        #    print dlg.xlim[0]
        #    print dlg.xlim[1]
        #    print dlg.ylim[0]
        #    print dlg.ylim[1]
        print self.xlim
        print self.ylim
        self.xlim[0] = self.xLowLimCtrl.GetValue()
        self.xlim[1] = self.xHighLimCtrl.GetValue()
        self.ylim[0]=self.yLowLimCtrl.GetValue()
        self.ylim[1] = self.yHighLimCtrl.GetValue()
        self.FFTPlot.set_xlim(self.xlim)
        self.FFTPlot.set_ylim(self.ylim)
        #    #self.FFTPlot.autoscale(True,axis='y')
        #    #self.FFTPlot.set_xlim([0,20000])
        self.repaint()
    def OnSave(self,e):
        dlg = wx.FileDialog(
            self, message="Save file as ...", defaultDir=os.getcwd(), 
            defaultFile="", wildcard="All files (*.*)|*.*", style=wx.SAVE
            )
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            #data = [[1,2],[3,4],[5,6]]
            with open(path,'wb') as file:
                writer=csv.writer(file,delimiter=',')
                #writer.writerows(self.DataTable.table.data)
        dlg.Destroy()
    
    def OnExit(self,e):
        #self.Close(True)  # Close the frame.
        self.Show(False) #just hides it, so we can show it again if desired

    def OnClose(self,e):
        self.Show(False) #same as OnExit
    
    def setxLowLim(self,e):
        self.xlim[0] = self.xLowLimCtrl.GetValue()

    def setxHighLim(self,e):
        self.xlim[1] = self.xHighLimCtrl.GetValue()

    def setyLowLim(self,e):
        self.ylim[0]=self.yLowLimCtrl.GetValue()

    def setyHighLim(self,e):
        self.ylim[1] = self.yHighLimCtrl.GetValue()

    def ClearTable(self,e):
        for i in range(0,len(self.Freq_List)):
            self.Freq_List[i].SetValue(0)
        for j in range(0,len(self.Calculated_List)):
            self.Calculated_List[j].SetValue('0')
        # print "number of rows is "+str(self.row)
        # i=1
        # while i<=self.row+1:
            # self.DataTable.table.DeleteRow()
            # i=i+1
   
