#####################Half-Life Calculator#########################
#Program designed to take in .npz files, integrate over a peak,      ,#
#Plot the areas as a function of time, and fit to an exponential to   #
#Estimate the Half-life of the element associated with the POI        #

import sys
from scipy.optimize import fsolve
from os import listdir
import operator
import mfit as mf
import numpy as np
import scipy as sp
import pylab as lab
import matplotlib.pyplot as plt

def halflifecalc(a):
	#Collect all npz files from a directory
	#thepath=input('Input the directory containing files for analysis: ')
	thepath=a[1]
	datfiles = [ v for v in listdir(thepath) if v.endswith('.npz') ]
	activity=[]
	time=[]
	runtimes=[]
	plot=0
	for d in datfiles:
		data=np.load(thepath + '/' + d)
		x,y=data['x'],data['y']
		runtimes.append(float(data['totaltime']))
		if plot==0:
			plt.ion()
			plt.plot(x,y) #Uses first file for user to choose peak of interest
			plt.title('Find your peak region, then close. Plotted file:' + str(d))
			plt.show()
			#Code for user input of peak, need code for people putting in silliness
			xleft=float(input('Leftmost edge of peak (keV):'))
			xright=float(input('Rightmost edge of right peak (keV):'))
			#xleft=553
			#xright=556
			plt.close()
			xmin=np.where(x<xleft)[0][-1]
			xmax=np.where(x>xright)[0][0]
			hpw=len(x[xmin:xmax])/2
			plot=1
		totact=sum(y[xmin:xmax])
		bgl=sum(y[xmin-hpw:xmin])
		bgr=sum(y[xmax:xmax+hpw])
		bg=bgl+bgr
		act=totact-bg
		activity.append(act)
		t=float(data['starttime']) #No adjustments for run time or live time yet
		time.append(t)
	tmin=min(time)
	ttime=[]
	for v in time:
		s=v-tmin
		ttime.append(s)
	
	#Organize data chronologically
	unsorted=zip(ttime, activity, runtimes)
	sortedzip=sorted(unsorted, key = lambda t: t[0])
	ttime=[x[0] for x in sortedzip]
	activity=[x[1] for x in sortedzip]
	runtimes=[x[2] for x in sortedzip]
	
	#We will scale the activity of each data set so all would have the same total run times.  Approximates a large half life compared to total run time
	
	mtot=max(runtimes)
	scaling=[]
	for p in runtimes:
		x=float(mtot/p)
		scaling.append(x)
	scactivity=[]
	for u in activity:
		u=u*scaling[activity.index(u)]
		#u=u/runtimes[activity.index(u)]
		scactivity.append(u)
	#hlexpfit(ttime, scactivity)	
	hlact(ttime, runtimes, activity)

def hlexpfit(a, b):
	ffunc = lambda p, x: p[0]*np.exp(-x*p[1])# + p[2]
	gr=mf.graph(np.array(a), np.array(b))
	p0=[30000, 1/42000]   #Constants chosen arbitrarily
	fitter=mf.function(ffunc, p0, a[0], a[-1])
	gr.fit(fitter)
	print('Parameters for fit: ' + str(fitter.p0))
	fitter.draw()
	bfit=fitter.p0[0]
	lfit=fitter.p0[1]
	#cfit=fitter.p0[2]
	#hlt= lambda x, y, z: (1/x)*(np.log(2*y/(y-z)))
	hlt=lambda x: (1/x)*np.log(2)
	#halfl=hlt(lfit, bfit, cfit)
	halfl=hlt(lfit)
	print('Fitted half-life (in hours): ' + str(halfl/3600))
	plt.plot(a, b, "o")	
	plt.ioff()
	plt.show()

def hlact(a, b, c):
	#We'll do this for just the first two sets of file data first	
	#First, need to get the tf and ti from a file by subtracting runtime from total time
	ti1=a[0]
	print(ti1)
	tf1=a[0]+b[0]
	print(tf1)
	ti2=a[1]
	print(ti2)
	tf2=a[1]+b[1]
	print(tf2)
	A=c[0]/c[1]
	print(A)
	afun= lambda x, y, z, a: a*(np.exp(-x*y)-np.exp(-x*z))
	#print(afun(x, ti1, tf1, 1))
	lamb=float(fsolve(lambda x: afun(x, ti1, tf1, 1)-afun(x, ti2, tf2, A), 1e-9))  #Starting point chosen arbitrarily
	print(lamb)
	#hl=(1/lamb)*np.log(2)
	#print('Half-life calculated(in hrs): ' + str(hl/3600))
	

if __name__ == '__main__':
	halflifecalc(sys.argv)



