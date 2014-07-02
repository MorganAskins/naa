################################## pynaa.py ####################################
############ Class to analyze data from neutron activation #####################
################################################################################
import numpy as np
import sys, os
import matplotlib as mpl
import matplotlib.pyplot as plt
import math

# User classes for pynaa
#import mfit as mf
import peakfinder as pf
from radionuclide import radionuclide

# Note: All code makes its way here, as a member of PyNaa

# To do:
# Load in single data file
# Fit peaks
# Load in multiple data files and time correct
# Given peaks, guess isotopes (two ways to do this)
# -- Use nuclear data information to relate peaks to elements and look for peak ratios
# -- Fit gamma peaks over multiple files using half lives
# Subtract backgrounds
# Keep track of errors

class analyzer:
    '''
    Primary analysis tool to compare multiple pynaa.files
    '''

    def __init__(self, files, t_begin=0):
        self.filelist=[]
        for f in files:
            self.add_file(f)
        self.t_begin = t_begin

    def add_file(self, filename):
        try:
            self.filelist.append(naafile(filename))
        except (NameError, FileNotFoundError, OSError) as er:
            print(er)

    
            
    # In order to analyze, need json gamma file, 
    
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
        # 

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

    def drawfits(self):
        for fit in self.fits:
            fit.draw()

    def drawdata(self):
        plt.plot(self.x, self.y)

    ### Print options
    def printnuclides(self):
        if hasattr(self, 'nuclides'):
            self.nuclides.write_isotopes()
        else:
            print('Need to run self.findradionculides first')
