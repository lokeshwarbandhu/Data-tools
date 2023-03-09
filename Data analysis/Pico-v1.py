import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks as fp
from scipy.optimize import curve_fit
import os

# Rising edge point
def rising_edge(data, thresh):
    sign = data >= thresh
    pos = np.where(np.convolve(sign, [1, -1]) == 1)
    return pos

# Falling edge point
def falling_edge(data, thresh):
    sign = data >= thresh
    pos = np.where(np.convolve(sign, [1, -1]) == -1)
    return pos

# Read data
def read_data(file):
    data = pd.read_csv(file)
    df = pd.DataFrame(data)
    X = df["Time"][1:]
    X = X.transform(pd.to_numeric)
    X = X - X.iloc[0] # Offset X-axis to 0
    Y = df["Channel A"][1:]
    Y = Y.transform(pd.to_numeric)
    return(X,Y)

# Plot graph
def plot_graph(X,Y,label):
    fig,ax = plt.subplots()
    # Plot original
    plt.plot(X,Y, label=label)
    plt.xlabel("Time (us)")
    plt.ylabel("Voltage (V)")
    #ax.legend("Channel A")
    plt.title("Picoscope")
    plt.legend()

    '''
    # x and y ticks
    xmarks=[i for i in np.arange(round(min(X)), round(max(X)), round((min(X)+max(X))/5))]
    plt.xticks(xmarks)
    ymarks=[i for i in np.arange(round(min(Y)), round(max(Y)), round((min(Y)+max(Y))/5))]
    plt.xticks(ymarks)
    '''
    # Auto Locator
    ax.xaxis.set_major_locator(ticker.AutoLocator())
    ax.xaxis.set_minor_locator(ticker.AutoMinorLocator())
    ax.yaxis.set_major_locator(ticker.AutoLocator())
    ax.yaxis.set_minor_locator(ticker.AutoMinorLocator())

# Define a fitting function
###############################################
def exp(t, A, lbda):
    r"""y(t) = A \cdot \exp(-\lambda t)"""
    return A * np.exp(-lbda * t)

def sine(t, omega, phi):
    r"""y(t) = \sin(\omega \cdot t + phi)"""
    return np.sin(omega * t + phi)

def cos(t, omega, phi):
    r"""y(t) = \cos(\omega \cdot t + phi)"""
    return np.cos(omega * t + phi)

def damped_sine(t, A, lbda, omega, phi):
    r"""y(t) = A \cdot \exp(-\lambda t) \cdot \left( \sin \left( \omega t + \phi ) \right)"""
    return exp(t, A, lbda) * sine(t, omega, phi)

def damped_cos(t, A, lbda, omega, phi):
    r"""y(t) = A \cdot \exp(-\lambda t) \cdot \left( \sin \left( \omega t + \phi ) \right)"""
    return exp(t, A, lbda) * cos(t, omega, phi)

def add_noise(y, loc=0, scale=0.01):
    noise = np.random.normal(loc=loc, scale=scale, size=y.shape)
    return y + noise

def find_peaks(x, y):
    peak_x = []
    peak_vals = []
    for i in range(len(y)):
        if i == 0:
            continue
        if i == len(y) - 1:
            continue
        if (y[i-1] < y[i]) and (y[i+1] < y[i]):
            peak_x.append(x[i])
            peak_vals.append(y[i])
    return np.array(peak_x), np.array(peak_vals)
####################################################

def case1(file):
    X,Y = read_data(file)
    # smoothen the curve
    Y_smooth = gaussian_filter1d(Y, 10)
    # compute first derivative
    Y1 = np.gradient(Y_smooth)
    # compute second derivative
    Y2 = np.gradient(Y1)
    
    ######### Case1 #################
    # Find the point when discharging starts
    for idx, val in enumerate(Y1):
        if val * max(Y_smooth) < -0.5:
            #print(idx,val)
            break
    
    # Split the smooth curve in to chargins and discharging phases
    C = Y_smooth[:idx] # Charging curve
    Xc = X.iloc[:idx] # charging time axis
    D = Y_smooth[idx:] # Discharging curve
    Xd = X.iloc[idx:] # discharging time axis

    # Find charging time and max amplitude
    #trigger = float(input("Enter trigger value (in V) : "))
    trigger = 0.25
    for i, val in enumerate(C):
        if val > trigger:
            #print(i,val)
            t_charge = Xc[idx-1]-Xc[i+1] # Charging time
            Amp = C[-1]-C[i+1] # Amplitude
            #print(t_charge) 
            #print(Amp)
            break
    # Offset time axis to zero
    #print(idx)
    Xd1 = Xd- np.min(Xd) # make new time axis array

    # Fit a polynomial on discharge curve
    try:
        popt, pcov = curve_fit(damped_sine, Xd1, D, p0 = (10,5e-1,5,np.pi/2))
        #print(*[f"{val:.2f}+/-{err:.2f}" for val, err in zip(popt, np.sqrt(np.diag(pcov)))])
        #print(A, lbda, omega, phi)
        #print(popt)
        pulse = [(t_charge, Amp, popt[0], popt[1], popt[2], popt[3])]
        pulse_list.append(pulse)
        global fires
        fires = fires + 1
    except:
        global mis_fires
        mis_fires = mis_fires + 1
        print("Error in curve fitting. Likely misfired pulse.")

def case2(file):
    # raw data
    X,Y = read_data(file)
    #smoothen the raw data
    Y_smooth = gaussian_filter1d(Y,10)
    # compute first derivative
    Y1 = np.gradient(Y_smooth)
    # compute second derivative
    Y2 = np.gradient(Y1)
    try:
        
        # Find rising and falling points
        r = rising_edge(Y1*max(Y_smooth), 0.5)
        f = falling_edge(Y1*max(Y_smooth), -0.5)
        # sort rising and falling points
        t = np.sort(np.hstack((r,f)))
    
        # find t0
        #trigger = float(input("Enter trigger value (in V) : "))
        trigger = 0.5
        for i, val in enumerate(Y_smooth):
            if val > trigger:
                #print(i,val)
                break
        t1 = [X.iloc[i]] # t0 added
        V = [val] # V0 added
        for idx in t:
            #print(idx)
            for id, value in enumerate(idx):
                if id < len(idx)-1:
                    #print(id)
                    if idx[id+1]-idx[id]>1:
                        t1.append(X.iloc[value])
                        #t1.append(value)
                        V.append(Y.iloc[value])
        pulse1 = [(t,V)]
        #print(pulse1)
        pulse.append(pulse1)
    except:
        print("Error in finding rising and falling edges. Likely misfired pulse.")

def pico():
    # Change the directory
    try:
        os.chdir(path)
    except:
        print("File location is not correct")
        raise
    # iterate through all file
    for file in os.listdir():
        print(file)
        #print(files)
        global files
        files = files + 1
        case1(file)
        #case2(file)

def pulse_stats():
    t=[]
    Amp =[]
    A=[]
    lam = []
    w= []
    phi =[]
    for row in pulse_list:
        for id in row:
            t.append(id[0])
            Amp.append(id[1])
            A.append(id[2])
            lam.append(id[3])
            w.append(id[4])
            phi.append(id[5])

    df = pd.DataFrame({'time':t, 'Amp':Amp,'A':A,'lam':lam,'w':w,'phi':phi})
    print(df.describe())
    boxplot = df.boxplot()
    plt.show()

path = input("Enter file location : ")
pulse_list = []
pulse = []
files = 0
fires = 0
mis_fires = 0
pico()
print("No. of pulses : " + str(files) + "\n Fires : " + str(fires) + "\n MisFires : " + str(mis_fires))
pulse_stats()

# Plot the number of fires and misfires
'''
P = pd.DataFrame({'Pulse':['Total', 'Fires', 'Misfires'], 'val':[files,fires,mis_fires]})
ax = P.plot.bar(x='Pulse', y='val', rot=0)
plt.show()
'''