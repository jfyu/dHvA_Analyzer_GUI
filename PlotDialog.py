import wx

class PlotDialog(wx.Dialog):
    def __init__(self,parent,ID,title,size=wx.DefaultSize,pos=wx.DefaultPosition,style=wx.DEFAULT_DIALOG_STYLE):
        pre = wx.PreDialog()
        pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
        pre.Create(parent,ID,title,pos,size,style)
        self.PostCreate(pre)

        sizer = wx.BoxSizer(wx.VERTICAL)
        label = wx.StaticText(self,-1,"Change x-axis Limits")
        sizer.Add(label,0,wx.ALIGN_CENTRE|wx.ALL,5)

        xbox = wx.BoxSizer(wx.VERTICAL)
        xLowLimLabel = wx.StaticText(self,-1,"x lower limit")
        xHighLimLabel = wx.StaticText(self,-1,"x upper limit")
        xbox.Add(xLowLimLabel,0,wx.ALIGN_CENTRE|wx.ALL)
        xbox.Add(xHighLimLabel,0,wx.ALIGN_CENTRE|wx.ALL)

        #sizer.Add(box,0,wx.ALIGN_CENTRE|wx.ALL,5)

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
        self.yLowLimCtrl = wx.SpinCtrlDouble(self,value='0.00',min=0.00,max=1e10,inc=0.1)
        self.yHighLimCtrl = wx.SpinCtrlDouble(self,value='10',min=0.00,max=1e10,inc=0.1)
        yControlBox.Add(self.yLowLimCtrl,0,wx.ALIGN_CENTRE|wx.ALL)
        yControlBox.Add(self.yHighLimCtrl,0,wx.ALIGN_CENTRE|wx.ALL)

        self.Bind(wx.EVT_SPINCTRLDOUBLE,self.setyLowLim,self.yLowLimCtrl)
        self.Bind(wx.EVT_SPINCTRLDOUBLE,self.setyHighLim,self.yHighLimCtrl)
 
        YallBox = wx.BoxSizer(wx.HORIZONTAL)
        YallBox.Add(ybox,0,wx.ALIGN_CENTRE|wx.ALL,5)
        YallBox.Add(yControlBox,0,wx.ALIGN_CENTRE|wx.ALL,5)
 
        sizer.Add(XallBox,0,wx.ALIGN_CENTRE|wx.ALL,5)
        sizer.Add(YallBox,0,wx.ALIGN_CENTRE|wx.ALL,5)
        line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
        sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)

        btnsizer = wx.StdDialogButtonSizer()
        
        btn = wx.Button(self, wx.ID_OK)
        #btn.SetHelpText("The OK button completes the dialog")
        btn.SetDefault()
        btnsizer.AddButton(btn)

        btn = wx.Button(self, wx.ID_CANCEL)
        #btn.SetHelpText("The Cancel button cancels the dialog. (Cool, huh?)")
        btnsizer.AddButton(btn)
        btnsizer.Realize()

        sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        self.SetSizer(sizer)
        sizer.Fit(self)

        #variables
        self.xlim = [0,20000]
        self.ylim = [0,10]
    def setxLowLim(self,e):
        self.xlim[0] = self.xLowLimCtrl.GetValue()

    def setxHighLim(self,e):
        self.xlim[1] = self.xHighLimCtrl.GetValue()

    def setyLowLim(self,e):
        self.ylim[0]=self.yLowLimCtrl.GetValue()

    def setyHighLim(self,e):
        self.ylim[1] = self.yHighLimCtrl.GetValue()
