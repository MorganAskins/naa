# Test the pynaa class
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import pynaa as naa
import sys
import mfit as mf
import json

def main(listoffiles):

    # I have built in exceptions so I could remove this and use try catch
    # real_list = [f for f in listoffiles if f.endswith('.npz')]
    physics = naa.analyzer(['test.npz'])
    halfrange = 1

    for f in physics.filelist:
        print('ran from', f.tstart, 'to', f.tstop,
              'with a dead time of', f.deadtime, '%')
        f.peaks()
        xp, yp = f.xpeaks, f.ypeaks
        fits = f.fits
        # The information I need is the mean and integral of the gauss fit
        integrals = [fitter.p0[0] for fitter in fits]
        means = [fitter.p0[1] for fitter in fits]
        peaks2elements(means, integrals)
        f.drawdata()
        f.drawfits()
        f.drawpeaks()
        
    plt.show()

def peaks2elements(mu, area):
    with open('../database/gammalist.json', 'r') as dbfile:
        db = json.load(dbfile)
        width=1
        isotopes=[]
        for m in mu:
            candidates = erangedb(db, m-width, m+width)
            true_candidates = []
            for c in candidates:
                emax, imax= maxInuclide(db, c['Nuclide'])
                default = False
                for mm in mu:
                    if mm < emax+width and mm > emax-width:
                        default = True
                if default:
                    true_candidates.append(c)
            isotopes.append(true_candidates)
        a_err = 0.3
        better_isotopes=[]
        for iso, a in zip(isotopes, area):
            # Check if areas are within 20% expected from intensities
            better_elements = []
            for element in iso:
                emax, imax = maxInuclide(db, element['Nuclide'])
                iratio_true = element['Intensity'] / imax
                bigarea_max = np.where(np.array(mu)>emax-width)[0][0]
                bigarea_min = np.where(np.array(mu)<emax+width)[0][-1]
                iratio_data = a / area[bigarea_min:bigarea_max+1][0]
                if not (iratio_true > iratio_data*(1+a_err) or
                        iratio_true < iratio_data*(1-a_err)):
                    better_elements.append(element)
            better_isotopes.append(better_elements)
            
        for b,m in zip(better_isotopes,mu):
            print('Gamma Energy ::', m, ' keV')
            for ele in b:
                print(ele['Nuclide'], ' -- Halflife:', ele['Half life(s)'])
            
def maxInuclide(db, nuclide):
    nuc = [item for item in db if item['Nuclide'] == nuclide]
    maxI, maxE = 0, 0
    for gamma in nuc:
        if gamma['Intensity'] > maxI:
            maxI = gamma['Intensity']
            maxE = gamma['Energy(keV)']
    return maxE, maxI
        
def searchdb(db, key, value):
    return [item for item in db if item[key] == value]

def erangedb(db, vmin, vmax, key='Energy(keV)'):
    return [item for item in db if (item[key] > vmin and item[key] < vmax)]
    
if __name__ == '__main__':
    main(sys.argv)
