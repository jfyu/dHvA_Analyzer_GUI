import numpy as np
from itertools import count,izip
#import pywt
from scipy.interpolate import interp1d,InterpolatedUnivariateSpline
from numpy import arange,array,average,diff,sqrt,take,argsort,sort,transpose,ones,add

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
    indic = np.where(np.logical_and(np.array(x)>=xmin,np.array(x)<=xmax))[0]
    #print indic, len(x)
    if len(indic)>0:
        temp_field = x[indic[0]:indic[-1]+1]
        temp_inY = inY[indic[0]:indic[-1]+1]
        temp_outY = outY[indic[0]:indic[-1]+1]
    # for i in range(0,len(x)):
    #     if (x[i]) > xmin and (x[i]) < xmax:
    #         temp_field.append(x[i])
    #         temp_inY.append(inY[i])
    #         temp_outY.append(outY[i])
            #temp_field = np.append(temp_field,x[i])
            #temp_inY = np.append(temp_inY,inY[i])
            #temp_outY = np.append(temp_outY,outY[i])
    #try: 
        #temp_field[1] #in case the selected range isn't really in the data range
    #except IndexError:
    else:
        print "Data doesn't exist in this range"
        
    return temp_field, temp_inY, temp_outY
def select_data_one(x,Y,xmin,xmax):
    temp_field = []
    temp_inY = []
    indic = np.where(np.logical_and(np.array(x)>=xmin,np.array(x)<=xmax))[0]
    #print indic, len(x)
    if len(indic)>0:
        temp_field = x[indic[0]:indic[-1]+1]
        temp_inY = Y[indic[0]:indic[-1]+1]
    # for i in range(0,len(x)):
    #     if (x[i]) > xmin and (x[i]) < xmax:
    #         temp_field.append(x[i])
    #         temp_inY.append(inY[i])
    #         temp_outY.append(outY[i])
            #temp_field = np.append(temp_field,x[i])
            #temp_inY = np.append(temp_inY,inY[i])
            #temp_outY = np.append(temp_outY,outY[i])
    #try: 
        #temp_field[1] #in case the selected range isn't really in the data range
    #except IndexError:
    else:
        print "Data doesn't exist in this range"
        
    return temp_field, temp_inY

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

# def find_angle(A1X,A1Y):
    # ratio = A1X[-1]/A1Y[-1]
    # ratio = -1*ratio
    # calc_theta_deg = np.arctan(ratio)*180/np.pi
    # temp_theta=[]
    # temp_value=[]
    # for index in range(int(round(calc_theta_deg - 10,0)), int(round(calc_theta_deg + 10,0)),1):
        # theta_deg = index
        # theta_rad = np.pi*theta_deg/180
        # UnSortSignalA = A1X*np.cos(theta_rad)+A1Y*np.sin(theta_rad)
        # result = np.average(abs(UnSortSignalA))
        # temp_value = np.append(temp_value,result)
        # temp_theta = np.append(temp_theta,theta_deg)
        # #print(result,theta_deg)

    # min_value,min_index = min(izip(temp_value,count()))
    # #print(min_value,min_index)
    # #Something wonky here. Phase is totally wrong. Try to remove 90 degree shift.
    # #theta_deg = temp_theta[min_index]
    # #theta_deg = temp_theta[min_index] + 90
    # theta_deg = 0
    # theta_rad = np.pi*theta_deg/180
    # UnSortSignalA = A1X*np.cos(theta_rad)+A1Y*np.sin(theta_rad)
    # UnSortSignalAY = A1Y
    # #Try this instead of phase.
    # #UnSortSignalA = np.sqrt(A1X**2 + A1Y**2)
    
    # #print(theta_deg)
    # return UnSortSignalA,UnSortSignalAY

# def wavelet_filter(A1X, decomp_lev, type, mode): #uses pywt package, make sure to install/import that
    # if isinstance(decomp_lev, int) and decomp_lev > 0:
        # #print(pywt.wavelist('bior'))
        # decomp = pywt.wavedec(A1X[:], type, mode=mode,level=decomp_lev)
      
        # sigma_j = np.median(abs(decomp[-1]))/0.6745
        # threshold_j = sigma_j*np.sqrt(2*np.log(len(A1X)))
    
        # for i in range(decomp_lev):
            # decomp[i + 1] = pywt.thresholding.less(decomp[i+1],threshold_j)
            # decomp[i + 1] = pywt.thresholding.greater(decomp[i+1],-threshold_j)
        
        # filt_A1X = pywt.waverec(decomp, type,mode=mode)
        # #if len(filt_A1X)!= len(A1X):
        # #    print 'Reconstructed Wavelet Length does not match'
        # #    print 'Reconstructed wavelet length is '+str(len(filt_A1X))
        # #    print 'original length is '+str(len(A1X))
        # #    print 'return the original array'
        # #    return A1X
        # #else:
        # return filt_A1X
        
    # else:
        # print('invalid')

def next_pow_2(N):
    #used to define number of points in the interpolation
    i = 0
    two_to_the_i = 1
    while N>two_to_the_i:
        i += 1
        two_to_the_i *= 2
    return i
def Sum_i(f):
    return add.reduce(f,0)
def Sum_j(f):
    return add.reduce(f,1)
def window(N):
    return arange(1,N+1,1)*arange(N,0,-1)
def four_point(x,y,x0):
        result = 0.0e+00
        result += (x0 - x[1])*( x0 - x[2])*(x0 - x[3])/( (x[0] - x[1])*(x[0] - x[2])*(x[0] - x[3]))*y[0]
        result += (x0 - x[0])*(x0 - x[2])*(x0 - x[3])/( (x[1] - x[0])*(x[1] - x[2])*(x[1] - x[3]))*y[1]
        result += (x0 - x[0])*(x0 - x[1])*(x0 - x[3])/( (x[2] - x[0])*(x[2] - x[1])*(x[2] - x[3]))*y[2]
        result += (x0 - x[0])*(x0 - x[1])*(x0 - x[2])/( (x[3] - x[0])*(x[3] - x[1])*(x[3] - x[2]))*y[3]
        return result

def inv_field_interp(data,B):
    #print "using numpy interp"
    Pow_2 = next_pow_2(len(B))
    N = pow(2,Pow_2)
    inv_B_min = 1.0/max(B)
    inv_B_max = 1.0/min(B)
    Delta_inv_B = (inv_B_max-inv_B_min)/N
    inv_B_array = np.arange(inv_B_min, inv_B_max,Delta_inv_B)#don't have the problem of four points, make length to N
    inv_data_func = interp1d(B,data,bounds_error=False,fill_value="extrapolate")
    inv_data = inv_data_func(1/inv_B_array)
    return inv_data, inv_B_array,Delta_inv_B
 
def inv_field(x_i,B_i):
    Pow_2 = next_pow_2( len(B_i) )   #next_pow_2 is defined at start of this file
    N = pow(2,Pow_2)
    I_B_min = 1.0/max(B_i)
    I_B_max = 1.0/min(B_i)
    Delta_I_B = (I_B_max - I_B_min)/N
    tmpX = []
    tmpIB = []
    tmpIB1 = sort(1.0/B_i)
    next_inverse_field = I_B_min
    current_index = 0
    for i in range(0,N-1):
        tmpIB.append( next_inverse_field )
        while ( tmpIB[i] ) >= tmpIB1[current_index]:
            current_index += 1 
        if current_index < ( len(tmpIB1) ):
            index = len(B_i)-1  - current_index
            if (index <= 1) | (index >= len(B_i)-2):
                tmpX.append(x_i[index] + (1.0/tmpIB[i] - B_i[index])*(x_i[index+1] - x_i[index] )/(B_i[index+1] - B_i[index] ) )
            else:
                tmpX.append(  four_point( B_i[index-1:index+3] , x_i[index-1:index+3] , 1.0/tmpIB[i] ))
        next_inverse_field += Delta_I_B
    IB_i = array(tmpIB)
    Ix_i = array(tmpX)
    return Ix_i, IB_i, Delta_I_B
#def inv_field(sortedField,signal):
#    #we have to interpolate for the x axis of FFT, which is 1/B and needs to be evenly spaced
#    inv_B = []#for the 1/B, x axis
#    interp_data = []#for the y axis, where one performs FFT
#    Pow_2 = next_pow_2( len(sortedField) )   #next_pow_2 is defined before
#    N = pow(2,Pow_2)
#    I_B_min = 1.0/max(sortedField)
#    I_B_max = 1.0/min(sortedField)
#    Delta_I_B = (I_B_max - I_B_min)/N
#    i=0
#    while i<N:
#        inv_B.append(I_B_min+i*Delta_I_B) #create the inverse_B array
#        i+=1
#    f = InterpolatedUnivariateSpline(sortedField,signal,k=3)#build a function that extrapolates as well as interpolates so it doesn't go out of bounds for the new x. See doc for more information. Interpolation and extrapolation using cubic spline
#    interp_data=f(inv_B)
#    #try:
#    #    interp_data = interp1d(sortedField,inv_B,kind='cubic')#get interpolated data
#    #except ValueError:
#    #    print 'interpolation outside range. Extrapolation required'
#
#    return inv_B, interp_data, Delta_I_B


def take_fft(y,power,delta_freq):
    pow_res = np.power(2,power)
    temp_fft = np.fft.fft(y,pow_res)
    temp_y = np.abs(temp_fft)
    temp_x = np.array(range(len(temp_y)/2))
    freq_array = delta_freq*temp_x/len(temp_y)
    fft_array = temp_y[0:len(temp_y)/2]
    return freq_array, fft_array
