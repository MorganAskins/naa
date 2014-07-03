################################## pynaa.py ####################################
############ Class to analyze data from neutron activation #####################
################################################################################
import numpy as np
import sys, os
import matplotlib as mpl
import matplotlib.pyplot as plt
import math
import json
import copy

# User classes for pynaa
#import mfit as mf
import peakfinder as pf
from radionuclide import radionuclide
from limitfinder import limitfinder

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
    Files classify (currently) into three types: sample, control(spike), background
    Sample files contain the unknown data
    Control has known masses
    Background doesn't have a sample, determining backgrounds of the Ge detector
    '''

    def __init__(self, config=None):
        if config == None:
            self.default_config()
        else:
            self.set_config(config)
        self.controllist = []
        self.samplelist = []
        self.bkglist = []
        self.load_config()
            
    def default_config(self):
        '''
        If there isn't a config file given, assume some default values
        In this case, no spikes or bkg subtraction
        '''
        self.config = { "sample name": "Default",
                        "sample mass": 0.0,
                        "backgrounds": [],
                        "exposure start": 86400.0,
                        "reactor power": 1.0,
                        "exposure time": 1,
                        "neutron flux": 1e10,
                        "samples": [] }
        
    def set_config(self, config_file):
        '''
        Currently assumes the config file contains the correct variables...
        config_file must be json, loads into a dictionary
        '''
        with open(config_file, 'r') as fname:
            try:
                self.config = json.load(fname)
            except ValueError:
                print(fname, 'is not a valid JSON object')
                self.default_config()


    def find_limits(self):
        limitfinder.run()
                
    def add_file(self, filename, filelist):
        try:
            filelist.append(naafile(filename))
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
