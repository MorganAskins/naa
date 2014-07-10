from .modifier import modifier
import numpy as np

from ..tool import mfit as mf
from ..tool import peakfinder as pf

class radionuclide(modifier):
    '''
    Given a set of fits to data, determine the
    likely radionuclides from a gamma database
    Inherits: database, datacollection, experiment
    '''
    def __setup__(self):
        self.name = 'radionuclide'

    def run(self):
        for datafile in self.datacollection.openfiles:
            # data file needs peaks
            if not hasattr(datafile, 'fits'):
                datafile.fits, datafile.xpeaks, datafile.ypeaks=pf.find_peaks(datafile.x, datafile.y)
                self.peaks2isotopes(datafile)

    def output(self):
        for datafile in self.datacollection.openfiles:
            self.write_isotopes(datafile)
                
    def peaks2isotopes(self, datafile):
        ## Todo: remove isotopes that are ~10 half lives from production
        '''
        The isotopes are determined
        '''
        width = 1
        datafile.peak_means = [fitter.peak()[0] for fitter in datafile.fits]
        datafile.isotopes = self.isotope_finder(datafile.peak_means, width)

    def isotope_finder(self, means, width):
        isotopes = []
        for this_m in means:
            candidates = self.database.energy_range(this_m-width, this_m+width)
            true_candidates = []
            for c in candidates:
                top2 = self.top2Inuclide(c['Nuclide'])
                contains = 0
                if top2[1] == 0:              #only one gamma
                    contains = 1
                for m in means:
                    if (m < top2[0]+width and m > top2[0]-width) or \
                       (m < top2[1]+width and m > top2[1]-width):
                        contains += 1
                if contains > 1:              #must contains the top two peaks
                    true_candidates.append(c)
            isotopes.append(true_candidates)
        return isotopes
    
    def top2Inuclide(self, nuclide):
        '''
        For a given radionuclide return the energies for the
        two most abundant gamma lines
        '''
        nuc = self.database.search('Nuclide', nuclide)
        top_energies = [0, 0]
        i1, i2 = 0, 0
        
        for gamma in nuc:
            if gamma['Intensity'] > i1:
                i1=gamma['Intensity']
                top_energies[0] = gamma['Energy(keV)']
        for gamma in nuc:
            if (gamma['Intensity'] > i2) and (gamma['Intensity'] != i1):
                i2=gamma['Intensity']
                top_energies[1] = gamma['Energy(keV)']
        
        return top_energies
        
    def write_isotopes(self, datafile):
        '''
        Print out gamma energies found from the fits with the
        likely isotopes producing them
        '''
        if hasattr(datafile, 'isotopes'):
            print('Isotopes in file:', datafile.name)
            for b,m in zip(datafile.isotopes, datafile.peak_means):
                print('Gamma Energy ::', m, 'keV')
                for ele in b:
                    print(ele['Nuclide'], ' -- Halflife:', ele['Half life(s)'])
