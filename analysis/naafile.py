import numpy as np
import sys, os
import matplotlib as mpl
import matplotlib.pyplot as plt
import math
import json
import copy

# Naa data file, as .npz (or later hdf5) ... I'm deprecating .spe
class naafile:
    '''
    Naa data file as an npz or hdf5 file, .spe won't be supported
    but can be converted to npz easily with a script
    Will raise a NameError if the wrong filetype is passed

    Public variable members:
    filename
    data
    x,y (spectrum)
    '''
    
    def __init__(self, name, gammadb='../database/gammalist.json'):
        self.filename = name
        extension = name.split('.')[-1]
        if not os.path.isfile(name):
            raise FileNotFoundError(name + ' not found ...')
        if name.endswith('.npz'):
            pass
        elif name.endswith('.h5'):
            raise NameError(extension + ' not YET supported')
        else:
            raise NameError(extension + ' not supported')
        # TODO: check if valid .npz and is naa file
        if os.path.isfile(gammadb):
            self.gammadb = gammadb
        self.prepare_data()

    def __add__(self, other):
        if type(other) == type(self):
            newfile = copy.copy(self)
            newfile.y = newfile.y + other.y
            newfile.tstart = float(min(newfile.tstart, other.tstart))
            t1, t2 = self.tstop - self.tstart, other.tstop-other.tstart
            newfile.tstop = newfile.tstart+t1+t2
            newfile.deadtime = (t1*self.deadtime+t2*other.deadtime)/(t1+t2)
            return newfile
        else:
            return self

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if type(other) == type(self):
            newfile = copy.copy(self)
            newfile.y = newfile.y - other.y
            newfile.tstart = float(min(newfile.tstart, other.tstart))
            t1, t2 = self.tstop - self.tstart, other.tstop-other.tstart
            newfile.tstop = newfile.tstart+t1-t2
            newfile.deadtime = (t1*self.deadtime+t2*other.deadtime)/(t1+t2)
            return newfile
        else:
            return self

    def bkg_subtract(self, bkg):
        if type(bkg) != type(self):
            print('background must be an naafile')
            return
        bkg.time_normalize()
        self.y = self.y - (bkg.y)*(self.tstop - self.tstart)
        
    def time_normalize(self):
        dt = self.tstop - self.tstart
        self.y = self.y / dt
        self.tstart, self.tstop = 0, 1
        
    def prepare_data(self):
        '''
        Loads the data from the npz file into np.arrays
        This initialized: self.data, self.x, self.y, self.nfo
        self.tstart, self.tstop, and self.deadtime
        '''
        self.data = np.load(self.filename)
        self.x, self.y = self.data['x'], self.data['y']
        self.nfo = self.data['info'].tolist()
        self.tstart = self.data['starttime']
        self.tstop = self.tstart + self.data['totaltime']
        self.deadtime = self.data['livetime']/self.data['totaltime']

    def do_all(self):
        # Apply all analysis requirements, in order, in one shot
        self.peaks()
        self.findradionuclides()
            
    def peaks(self):
        self.fits, self.xpeaks, self.ypeaks = pf.find_peaks(self.x, self.y)

    def findradionuclides(self):
        '''
        Given a gamma json file, using the fitted peaks, this will attempt
        to identify the elements producing the gammas
        '''
        if not hasattr(self, 'fits'):
            self.peaks()
        if hasattr(self, 'gammadb'):
            self.nuclides = radionuclide(self.gammadb, self.fits)
        else:
            print('Gamma database not given or does not exist')

    ### Draw options
    '''
    These are the available draw options that will draw onto the current
    matplotlib instance.
    This can drawpeaks, drawfits, and drawdata
    '''
        
    def drawpeaks(self):
        plt.plot(self.xpeaks, self.ypeaks, 'ro')
        plt.show()

    def drawfits(self):
        for fit in self.fits:
            fit.draw()
        plt.show()

    def drawdata(self):
        plt.plot(self.x, self.y)
        plt.show()

    ### Print options
    def printnuclides(self):
        if hasattr(self, 'nuclides'):
            self.nuclides.write_isotopes()
        else:
            print('Need to run self.findradionculides first')
