import wx
from FFTWindow import * 
class FFTPanel(wx.Frame):
    title='FFT'
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self,*args,**kwargs)
        self.FFTWindow = FFTWindow(self)
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(self.FFTWindow,0,wx.EXPAND)
        self.SetSizer(self.sizer)     
        self.SetAutoLayout(1)
        self.sizer.Fit(self)

        self.Centre()
        self.Show()
    
