# de Haas-van Alphen Data Analyzer 
GUI front for analyzing de Haas van Alphen Quantum Oscillation Data 

##Required Packages and Usage
###Required Packages
In addition to basic installation of Python, one would to install the following packages:

    wxPython
    os
    csv
    netCDF
    numpy
    matplotlib
    scipy


###Usage
To use the software, simply run the main.py file in command-line. When finished with inputting all the control parameters, press the Apply button, and the changes will be applied to the plotting window and the FFT window. 

##Main Panel
The main panel consists of a plotting panel on the left and the control panel on the right. The plotting panel plots data after every step of the analysis.    

###Open File
To open the data file, click the open icon button next the data name field. Note that the File Name field is not editable. This function can also be accessed by using the drop-down menu FILE, on the menu panel. Note that this software supports netCDF files only. 

###Choosing Data and Range of Interest (ROI)
Once a data file is chosen, the X, in-phase Y and out-phase Y drop-down menus will be populated with the data fields encoded in the netCDF file. Since this software analyzes dHvA data, X is generally the applied field B and the two Ys would be the complex signal acquired by the lock-in.

In its current state, this software supports max X to be 17.9. The values can be easily changed in the file dHvAFrame.py. 

###Choosing Phase
The phase between the in-phase and out-phase Y, as acquired by the lock-in, is not immediately clear from the setup. This is because the low temperature transformers would introduce a phase shift between the two signals. In general, the optimal phase is found when the FFT signal has maximum amplitude. One can choose whether to use the in-phase (resistive) data or the out of phase (capacitive) data. The optimal phase can be found automatically. 

###Polynomial Background Removal
Next, the user can choose the highest order polynomial background to remove from the raw data. The user can also choose not to remove any background by unchecking the check box. The background is found by fitting a polynomial function of the chosen order to the raw data and then subtracted from it. 

###Spike Removal
Sometimes the raw data will have sharp spikes, either from instrumentation noise or people walking by the dilution fridge while the data is being measured. The problem with these spikes is that once Fourier transformed, they increase the noise floor and thus may smear out dHvA peaks with small amplitudes. To an extent the windowing and smoothing (discussed in the next section) can help alleviate this problem, but not all spikes are removed that way.

The problem of a spike removal algorithm is that it must also not remove high frequency dHvA. The current version of this software supports a median filter algorithm. I must emphasize here that this method is not particularly bulletproof -- it is liable to remove spikes at the expense of reducing oscillation amplitudes. Therefore I have set the default option in the control panel to not perform spike removal. The user is encouraged to experiment with the different inputs to find the optimal combination of parameters
for their own data. It should also be warned here that as the spike removal algorithm inevitably reduces FFT amplitudes, it is not recommended to turn on this option when using the program for temperature dependent mass study. 

The algorithm itself is extremely simple: we move along the x-axis, taking a window with the size of the specified kernel (odd integer only, a warning will be shown if the integer entered is even, and the program will revert back to the closest odd integer. This is a specification from the Numpy package); we then calculate the median in that window, and compare each point in that window to the median. If the proportion of the data value to the median is more than the spike
threshold as specified by the user, then we replace that data with the median value of the window. The user can also specify the number of passes for this procedure. The plot window has a separate figure which plots the data before and after de-spiking. This gives a visual guide to the user for tweaking the input parameters. 

###Smoothing and Windowing
In FFT algorithms, a major assumption is that the signal has exactly integer number of cycles inside the time interval. But this is clearly not always the case. When FFT is performed on Signals with non-integral number of cycles, spectral leakage occurs. Spectral leakage refers to the distortion of the Fourier transformed signal such that a signal from a given frequency is spread out to adjacent frequencies: i.e. satellite peaks surrounding a central
peak. These satellite peaks can be mistaken as dHvA frequencies.

To alleviate the spectral leakage problem, a window that decreases smoothly at the edge is applied to the signal before performing FFT. Essentially, we multiply the input signal with a given window,which will smooth out the satellite peaks once the FFT is applied. In this program, the user has the choices of:
    Flat
    Hanning
    Hamming
    Bartlett
    Blackman
    Kaiser

With the default option of Hamming, which should be sufficient for most signals. The user is encouraged to look up the details on these different windowing functions and choose the most appropriate one. 

The smoothing function is based on the SignalSmooth code of the SciPy.org's cookbook. This function is usually not used.

##FFT Panel
This panel features a plot window where the FFT of the processed signal is plotted, once all the analysis is applied (i.e. the Apply button is pressed on the main panel). The default matplotlib toolbar is available at the bottom. In addition to the toolbar's zoom in functionality, on the top right corner of the control panel the user can adjust the x and y axis limits manually.

The FFT panel cannot be closed. If closed, upon pressing Apply button on the Main Panel, it will appear again. This is helpful to users who tends to close windows instead of minimizing them. 

If the user move the mouse over to the plot window, a cursor will appear. The user can click anywhere on the data, and the nearest frequency will be shown on the table on the right. The implementation of the click is that using the matplotlib "picker" function (see http://matplotlib.org/users/eventi\_handling.html and http://matplotlib.org/examples/eventi\_handling/pick\_event\_demo.html), generally speaking the function will return an array of data points close to the click
position, and this software takes the first element of that array. The user can also manually edit the estimated frequency. 

This function is available so that user can estimate the dHvA frequencies. The grey boxes will then display the amplitude of the peak at that frequency. Once the user has finished identifying all the frequencies, the user can then return to the Main Panel, and press the Auto Phase button. This starts a phase searching process. The software changes the relative phase between the In-Phase Y and the Out-Phase Y at 5 degrees interval. At each step, the software searches +/- 50 T from the estimated frequency, and find the frequency with maximum amplitude. It then compares with previous phase angles, and keep only the frequency-amplitude pair with the highest amplitude. The table also displays the corresponding phase angle to that maximum amplitude. This allows the user to easily discard fake dHvA frequencies (with phase angle dramatically different from others), as well as helps the user to identify the amplitude of the FFT, used in mass
analysis.  

