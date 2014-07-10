import os
import numpy as np
from ..tool import peakfinder as pf

class datacollection:
    '''
    Contains collections of data files and data objects
    '''
    def __init__(self,listofdatafiles=[]):
        self.filenames = listofdatafiles   #string
        self.openfiles = []                #datafile
    def add_file(self, filename, filetype):
        try:
            self.openfiles.append(datafile(filename, filetype))
        except (NameError, FileNotFoundError, OSError) as er:
            print(er)
        
class datafile:
    '''
    Contains information on a single data file
    Only used by datacollection
    '''
    def __init__(self, filename, filetype):
        ''' filetype should be sample, control, background '''
        self.name = filename
        extension = self.name.split('.')[-1]
        if not os.path.isfile(self.name):
            raise FileNotFoundError(self.name+' not found ...')
        if self.name.endswith('.npz'):
            pass
        elif self.name.endswith('.h5'):
            raise NameError(extension + ' not YET supported')
        else:
            raise NameError(extension + ' not supported')
        self.filetype = filetype
        self.prepare_data()

    def prepare_data(self):
        '''
        Loads the data from the npz file into np.arrays
        This initialized: self.data, self.x, self.y, self.nfo
        self.tstart, self.tstop, and self.deadtime
        '''
        self.data = np.load(self.name)
        self.x, self.y = self.data['x'], self.data['y']
        self.nfo = self.data['info'].tolist()
        self.tstart = self.data['starttime']
        self.tstop = self.tstart + self.data['totaltime']
        self.deadtime = self.data['livetime']/self.data['totaltime']
