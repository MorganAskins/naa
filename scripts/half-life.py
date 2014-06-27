#####################Half-Life Calculator#########################
#Program designed to take in .npz files, integrate over a peak,      ,#
#Plot the areas as a function of time, and fit to an exponential to   #
#Estimate the Half-life of the element associated with the POI        #

import numpy as np
import scipy as sp
import pylab as lab
import matplotlib.pyplot as plt

#First, we need to input the files that we need.  First, I will just choose the specific ones of interest.  Eventually, can modify to be inputs for general cases.
data1=np.load('PPO_control_06112014_000.npz')
x1,y1=data1['x'],data1['y']

data2=np.load('PPO_control_06112014_001.npz')
x2,y2=data2['x'],data2['y']

data3=np.load('PPO_control_06112014_002.npz')
x3,y3=data3['x'],data3['y']

#Next, choose region to integrate over for counts

#This region will integrate over the feature next to the Br-82 619 peak
#x1min=np.where(x1<615)[0][-1]
#x1max=np.where(x1>617.5)[0][0]
#x2min=np.where(x2<615)[0][-1]
#x2max=np.where(x2>617.5)[0][0]
#x3min=np.where(x3<615)[0][-1]
#x3max=np.where(x3>617.5)[0][0]

#This region considers the peak centered around 1327 keV
x1min=np.where(x1<1366)[0][-1]
x1max=np.where(x1>1372)[0][0]


#Integrate in each file to get activities
totact1=sum(y1[x1min:x1max])
bg1l=sum(y1[x1min-len(x1[x1min:x1max]):x1min])
bg1r=sum(y1[x1max:x1max+len(x1[x1min:x1max])])
bg1=bg1l+bg1r
totact2=sum(y2[x1min:x1max])
bg2l=sum(y2[x1min-len(x2[x1min:x1max]):x1min])
bg2r=sum(y2[x1max:x1max+len(x1[x1min:x1max])])
bg2=bg2l+bg2r
totact3=sum(y3[x1min:x1max])
bg3l=sum(y3[x1min-len(x3[x1min:x1max]):x1min])
bg3r=sum(y3[x1max:x1max+len(x1[x1min:x1max])])
bg3=bg3l+bg3r

act1=totact1-bg1
act2=totact2-bg2
act3=totact3-bg3
activity=[act1, act2, act3]
print(activity)

#Time separation of data collection found in data files
t1=0      #Zero relative to other measured times
t2=2.07444
t3=t2+2.071666
time=[t1, t2, t3]
print(time)

plt.plot(time, activity)
plt.show()
