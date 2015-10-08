import numpy as np
import wx

def sort_array(x_in,y_in):
    temp = [x_in,y_in]
    temp = zip(*temp)
    temp.sort(key = lambda x: x[0], reverse=False)
    temp = zip(*temp)
    x_out = np.array(temp[0][:])
    y_out = np.array(temp[1][:])
    return x_out, y_out 

def select_data(x, inY, outY, xmin, xmax):
    temp_field = []
    temp_inY = []
    temp_outY = []
    for i in range(0,len(x)):
        if (x[i]) > xmin and (x[i]) < xmax:
            temp_field = np.append(temp_field,x[i])
            temp_inY = np.append(temp_inY,inY[i])
            temp_outY = np.append(temp_outY,outY[i])
    try: 
        temp_inY[i] #in case the selected range isn't really in the data range
    except IndexError:
        print "Data doesn't exist in this range"
        
    return temp_field, temp_inY, temp_outY

def smooth(x,window_len=11,window='hamming'):
    if x.ndim != 1:
        raise ValueError, "smooth only accepts 1 dimension arrays."
   
    if x.size < window_len:
        raise ValueError, "Input vector needs to be bigger than window size."
  
   
    if window_len<3:
        return x
   
   
    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman', 'kaiser']:
        raise ValueError, "Window is one of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman', 'kaiser'"
  
    s=np.r_[2*x[0]-x[window_len-1::-1],x,2*x[-1]-x[-1:-window_len:-1]]
    
    #print(len(s))
    if window == 'flat': #moving average
        w=np.ones(window_len,'d')
    elif window == 'kaiser':
        w=eval('np.'+window+'(window_len,14)')
    else:
        w=eval('np.'+window+'(window_len)')
  
    y=np.convolve(w/w.sum(),s,mode='same')
    
    return y[window_len:-window_len+1]
