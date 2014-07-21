#####################Half-Life Calculator#########################
#Program designed to take in a list of pynaa files, integrate over a  #
#peak in each, Plot the areas as a function of time, and fit to an    #
#exponential to Estimate the Half-life of the element                 #

##TO-DO##
# * Re-write so the program runs over all peaks in an experiment #
# * Have the program output a data file with peaks and associated#
#   Half-lives found for each peak using both methods            #

import sys
from scipy.optimize import fsolve
from os import listdir
import operator

from .modifier import modifier
from ..tool import mfit as mf

import numpy as np
import matplotlib.pyplot as plt

class halflife(modifier):
	'''
	Given a list of pynaa.naafiles, calculate the
	half-life of a decaying peak associated with
	a single isotope.
	'''
	 	
	def __setup__(self):
		self.name = 'halflife'

	def run(self):
		'''
		Half-life is calculated in two ways
		'''
		peakdata=self.choosepeak(self.datacollection.openfiles)
		scpeakdata=self.timescaleact(peakdata)
		self.hlexpfit(scpeakdata, peakdata)
		self.hlact(scpeakdata, peakdata)

###Functions used by the half-life calculator
	
	def choosepeak(self, a):
		activity=[]
		starttime=[]
		counttimes=[]
		plot=0
		for d in a:
			x,y=d.x,d.y
			counttimes.append(float(d.tstop-d.tstart))
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
			t=float(d.tstart) #Need adjustments for run time or live time yet
			starttime.append(t)
		tmin=min(starttime)
		ttime=[]
		for v in starttime:
			s=v-tmin
			ttime.append(s)
		unsorted=zip(ttime, activity, counttimes, starttime)
		sortedareas=sorted(unsorted, key = lambda t: t[0])#Organize peak areas chronologically
		return sortedareas
	
	def timescaleact(self, x):
		ttime=[i[0] for i in x]
		activity=[i[1] for i in x]
		counttimes=[i[2] for i in x]
		mtot=max(counttimes)
		scaling=[]
		for p in counttimes:
			y=float(mtot/p)
			scaling.append(y)
		scactivity=[]
		for u in activity:
			u=u*scaling[activity.index(u)]
			scactivity.append(u)
		scaledact=zip(ttime, scactivity, counttimes)
		scaledact=sorted(scaledact)
		return scaledact
	
	def hlexpfit(self, r, t):
		print('Half-life results from exponential fit of scaled activities:')
		ttime=[i[0] for i in r]
		activity=[i[1] for i in t]
		scactivity=[i[1] for i in r]
		counttimes=[i[2] for i in r]
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
		counttimes=[i[2] for i in a]
		k=0
		allhls=[]
		while k < len(ttime):
			p=k	
			while p < len(ttime)-1:			
				p=p+1
				ti1=ttime[k]
				tf1=ttime[k]+counttimes[k]
				ti2=ttime[p]
				tf2=ttime[p]+counttimes[p]
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

