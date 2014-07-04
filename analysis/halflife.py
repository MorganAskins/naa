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
import matplotlib.pyplot as plt

class halflife:
	'''
	Given a list of pynaa.naafiles, calculate the
	half-life of a decaying peak associated with
	a single isotope.
	'''
	 	
	def __init__(self, pynaafiles):
		self.naf = pynaafiles
		self.halflifecalc()

	def halflifecalc(self):
		'''
		Half-life is calculated in two ways
		'''
		peakdata=self.choosepeak(self.naf)
		scpeakdata=self.timescaleact(peakdata)
		self.hlexpfit(scpeakdata, peakdata)
		self.hlact(scpeakdata, peakdata)

###Functions used by the half-life calculator
	
	def choosepeak(self, a):
		activity=[]
		time=[]
		runtimes=[]
		plot=0
		for d in a:
			x,y=d.x,d.y
			runtimes.append(float(d.tstop))
			if plot==0:
				plt.ion()
				plt.plot(x,y) #Uses first file for user to choose peak of interest
				plt.title('Find your peak region, then close. Plotted file:' + str(d))
				plt.show()
				xleft=float(input('Leftmost edge of peak (keV):'))
				xright=float(input('Rightmost edge of right peak (keV):'))
				plt.close()
				xmin=np.where(x<xleft)[0][-1]
				xmax=np.where(x>xright)[0][0]
				hpw=len(x[xmin:xmax])/2
				plot=1
			totact=sum(y[xmin:xmax])
			bgl=sum(y[xmin-hpw:xmin]) #Backgrounds calculated from left and right sides of peak
			bgr=sum(y[xmax:xmax+hpw])
			bg=bgl+bgr
			act=totact-bg
			activity.append(act)
			t=float(d.tstart) #No adjustments for run time or live time yet
			time.append(t)
		tmin=min(time)
		ttime=[]
		for v in time:
			s=v-tmin
			ttime.append(s)
		unsorted=zip(ttime, activity, runtimes)
		sortedareas=sorted(unsorted, key = lambda t: t[0])#Organize peak areas chronologically
		return sortedareas
	
	def timescaleact(self, x):
		ttime=[i[0] for i in x]
		activity=[i[1] for i in x]
		runtimes=[i[2] for i in x]
		mtot=max(runtimes)
		scaling=[]
		for p in runtimes:
			y=float(mtot/p)
			scaling.append(y)
		scactivity=[]
		for u in activity:
			u=u*scaling[activity.index(u)]
			scactivity.append(u)
		scaledact=zip(ttime, scactivity, runtimes)
		scaledact=sorted(scaledact)
		return scaledact
	
	def hlexpfit(self, r, t):
		print('Half-life results from exponential fit of scaled activities:')
		ttime=[i[0] for i in r]
		activity=[i[1] for i in t]
		scactivity=[i[1] for i in r]
		runtimes=[i[2] for i in r]
		ffunc = lambda p, x: p[0]*np.exp(-x*p[1])
		gr=mf.graph(np.array(ttime), np.array(scactivity))
		p0=[30000, 1/42000]   #Constants chosen arbitrarily
		fitter=mf.function(ffunc, p0, ttime[0], ttime[-1])
		gr.fit(fitter)
		print('Parameters for fit: ' + str(fitter.p0))
		fitter.draw()
		bfit=fitter.p0[0]
		lfit=fitter.p0[1]
		hlt=lambda x: (1/x)*np.log(2)
		halfl=hlt(lfit)
		print('Fitted half-life (in hours): ' + str(halfl/3600))
		plt.plot(ttime, scactivity, "o")	
		plt.ioff()
		plt.show()
	
	def hlact(self, a, b):
		print('Half-life results calculated directly from activity and count times:') 
		ttime=[i[0] for i in a]
		activity=[i[1] for i in b]
		scactivity=[i[1] for i in a]
		runtimes=[i[2] for i in a]
		k=0
		allhls=[]
		while k < len(ttime):
			p=k	
			while p < len(ttime)-1:			
				p=p+1
				ti1=ttime[k]
				tf1=ttime[k]+runtimes[k]
				ti2=ttime[p]
				tf2=ttime[p]+runtimes[p]
				A=activity[k]/activity[p]
				afun= lambda x, y, z, a: a*(np.exp(-x*y)-np.exp(-x*z))
				#print(afun(x, ti1, tf1, 1))
				lamb=float(fsolve(lambda x: afun(x, ti1, tf1, 1)-afun(x, ti2, tf2, A),1e-5))  #Starting point chosen arbitrarily
				hl=((1/lamb)*np.log(2)/3600) #Converted to hrs
				if hl < 0 or hl > 1.0e+09:
					print('Calculated a half-life of:' + str(hl))
					print('Unphysical half-life calculated. Issue may be in background subtraction or bad peak bounds.  Ignoring value for half-life average.')
				else:
					allhls.append(hl)
			k=k+1		
		print('Average of all calculated half-lifes: ' + str(np.average(allhls)))
		print('Std. dev. of all calculated half-lifes: ' + str(np.std(allhls)))
