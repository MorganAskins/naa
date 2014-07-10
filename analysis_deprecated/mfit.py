############################## mfit.py #########################################
############ Class to implement fitting in a straight forward way ##############
################################################################################
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import math
from scipy.optimize import leastsq as ls
import scipy.special as sp

# Two types of graphs we would like to fit, (x,y) coordinates and histograms
# We would also like a simple conversion from one to another

class graph:
    """ Graph object that can be fit and transformed to a histogram """
    def __init__(self, x, y):
        '''
        Build the graph with given x, y lists or np.arrays
        Saves the members as np.arrays for speed
        ''' 
        self.x, self.y = np.array(x), np.array(y)
        self.xmin, self.xmax = 0, len(self.x)
    def draw(self):
        plt.plot(self.x[self.xmin:self.xmax], self.y[self.xmin:self.xmax])
    def bounds(self, xmin, xmax):
        self.xmin = np.where(self.x>=xmin)[0][0]
        self.xmax = np.where(self.x<=xmax)[0][-1]
    def fit(self, func):#expects a mfit.function
        residual = func.residual()
        p0 = func.p0
        xmin, xmax = np.where(self.x>=func.xmin)[0][0], np.where(self.x<=func.xmax)[0][-1]
        fitout = ls(residual, p0, args=(self.x[xmin:(xmax+1)], self.y[xmin:(xmax+1)]))
        func.p0, func.covariance = fitout[0], fitout[1]
    def integrate(self, xmin, xmax):
        xmindx, xmaxdx = np.where(self.x>=xmin)[0][0], np.where(self.x<=xmax)[0][-1]
        return sum(self.y[xmindx:xmaxdx]), len(self.y[xmindx:xmaxdx])
        
class function:
    def __init__(self, func, p0=[0], xmin=0, xmax=-1):
        self.p0=p0
        self.xmin, self.xmax = xmin, xmax
        self.func = func
        self.covariance = 0
    def bounds(self, xmin, xmax):
        self.xmin = xmin
        self.xmax = xmax
    def residual(self):
        return lambda p, x, y: ( y - self.func(p, x) )
    def draw(self, step_size=0.1):
        steps = (self.xmax-self.xmin)/step_size
        x=np.linspace(self.xmin, self.xmax, steps)
        plt.plot(x, self.func(self.p0, x))
    def f(self, x):
        return self.func(self.p0, x)
    def peak(self, step_size=0.1):
        steps = (self.xmax-self.xmin)/step_size
        x=np.linspace(self.xmin, self.xmax, steps)
        y=self.func(self.p0, x)
        ypeak = max(y)
        xpeak = x[np.where(y==ypeak)[0][0]]
        return xpeak, ypeak
    
# Finally a bunch of functions often used in fitting
gauss = lambda x, m, s: (s**2*2*np.pi)**(-1/2)*np.exp(-1/2*(x-m)**2/s**2)
breitwigner = lambda x, m, s: 1/( (x**2 - m**2)**2 + (m*s)**2 )
compshoulder = lambda x, m, a, b: sp.erfc((x-m)/a)*np.exp((x-m)/b)
