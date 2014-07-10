# Test the pynaa class
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import pynaa as naa
import sys
import mfit as mf
import json
import copy

def main(listoffiles):

    # I have built in exceptions so I could remove this and use try catch
    # real_list = [f for f in listoffiles if f.endswith('.npz')]
    physics = naa.analyzer(listoffiles)

    for f in physics.filelist:
        print('ran ', f.tstop-f.tstart, 'seconds',
              'beginning at', f.tstart,
              'with a dead time of', f.deadtime, '%')
        f.do_all()
        f.printnuclides()
        f.drawdata()
        f.drawfits()
        f.drawpeaks()
        
    plt.show()

def integrals_from_fits(fit):
    newfit = copy.deepcopy(fit)
    # Without backgrounds:
    newfit.p0[4]=0
    xmin, xmax = newfit.xmin, newfit.xmax
    x = np.arange(xmin, xmax, 1000)
    width = (xmax-xmin)/1000.0
    return sum(newfit.func(newfit.p0, x))*width          
        
def searchdb(db, key, value):
    return [item for item in db if item[key] == value]

def erangedb(db, vmin, vmax, key='Energy(keV)'):
    return [item for item in db if (item[key] > vmin and item[key] < vmax)]
    
if __name__ == '__main__':
    main(sys.argv)
