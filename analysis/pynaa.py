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
from naafile import naafile
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
        limits = limitfinder(self.config)
        limits.run()
                
    def add_file(self, filename, filelist):
        try:
            filelist.append(naafile(filename))
        except (NameError, FileNotFoundError, OSError) as er:
            print(er)    
