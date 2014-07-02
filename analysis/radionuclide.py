import numpy as np
import mfit as mf
import json

class radionuclide:
    '''
    Given a set of fits to data, determine the
    likely radionuclides from a gamma database
    '''
    def __init__(self, database, fits):
        self.dbname = database
        self.fits = fits
        self.peaks2isotopes()
    def peaks2isotopes(self):
        ## Todo: remove isotopes that are ~10 half lives from production
        '''
        The isotopes are determined
        '''
        with open(self.dbname, 'r') as dbfile:
            db = json.load(dbfile)
            width = 1
            self.means = [fitter.peak()[0] for fitter in self.fits]
            self.isotopes = isotope_finder(db, self.means, width)
            
    def write_isotopes(self):
        '''
        Print out gamma energies found from the fits with the
        likely isotopes producing them
        '''
        if hasattr(self, 'isotopes'):
            for b,m in zip(self.isotopes, self.means):
                print('Gamma Energy ::', m, 'keV')
                for ele in b:
                    print(ele['Nuclide'], ' -- Halflife:', ele['Half life(s)'])


## functions to be used by the radionuclide class

def isotope_finder(db, means, width):
    isotopes = []
    for this_m in means:
        candidates = erangedb(db,this_m-width, this_m+width)
        true_candidates = []
        for c in candidates:
            top2 = top2Inuclide(db, c['Nuclide'])
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
    
def top2Inuclide(db, nuclide):
    '''
    For a given radionuclide return the energies for the
    two most abundant gamma lines
    '''
    nuc = searchdb(db, 'Nuclide', nuclide)
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
            
def erangedb(db, vmin, vmax, key='Energy(keV)'):
    return [item for item in db if (item[key] > vmin and item[key] < vmax)]

def searchdb(db, key, value):
    return [item for item in db if item[key] == value]
