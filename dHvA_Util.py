import numpy as np
from itertools import count,izip
import pywt

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
        temp_field[1] #in case the selected range isn't really in the data range
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

def find_angle(A1X,A1Y):
    ratio = A1X[-1]/A1Y[-1]
    ratio = -1*ratio
    calc_theta_deg = np.arctan(ratio)*180/np.pi
    temp_theta=[]
    temp_value=[]
    for index in range(int(round(calc_theta_deg - 10,0)), int(round(calc_theta_deg + 10,0)),1):
        theta_deg = index
        theta_rad = np.pi*theta_deg/180
        UnSortSignalA = A1X*np.cos(theta_rad)+A1Y*np.sin(theta_rad)
        result = np.average(abs(UnSortSignalA))
        temp_value = np.append(temp_value,result)
        temp_theta = np.append(temp_theta,theta_deg)
        #print(result,theta_deg)

    min_value,min_index = min(izip(temp_value,count()))
    #print(min_value,min_index)
    #Something wonky here. Phase is totally wrong. Try to remove 90 degree shift.
    #theta_deg = temp_theta[min_index]
    #theta_deg = temp_theta[min_index] + 90
    theta_deg = 0
    theta_rad = np.pi*theta_deg/180
    UnSortSignalA = A1X*np.cos(theta_rad)+A1Y*np.sin(theta_rad)
    UnSortSignalAY = A1Y
    #Try this instead of phase.
    #UnSortSignalA = np.sqrt(A1X**2 + A1Y**2)
    
    #print(theta_deg)
    return UnSortSignalA,UnSortSignalAY

def wavelet_filter(A1X, decomp_lev, type):
    if isinstance(decomp_lev, int) and decomp_lev > 0:
        #print(pywt.wavelist('bior'))
        decomp = pywt.wavedec(A1X[:], type, level=decomp_lev)
      
        sigma_j = np.median(abs(decomp[-1]))/0.6745
        threshold_j = sigma_j*np.sqrt(2*np.log(len(A1X)))
    
        for i in range(decomp_lev):
            decomp[i + 1] = pywt.thresholding.less(decomp[i+1],threshold_j)
            decomp[i + 1] = pywt.thresholding.greater(decomp[i+1],-threshold_j)
        
        filt_A1X = pywt.waverec(decomp, type)
        if len(filt_A1X)!= len(A1X):
            print 'Reconstructed Wavelet Length does not match'
            print 'Reconstructed wavelet length is '+str(len(filt_A1X))
            print 'original length is '+str(len(A1X))
            print 'return the original array'
            return A1X
        else:
            return filt_A1X
        
    else:
        print('invalid')

