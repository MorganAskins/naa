import numpy as np
import sys, os
import mfit as mf
import matplotlib as mpl
import matplotlib.pyplot as plt
import math

## Currently a bunch of magic numbers, this can be optimized
## later to deal with this, in particular not every peak should
## be treated the same. Peaks that are close should be fit together,
## and large peaks should have longer tails. Also a guassian doesn't
## do these spectra justice

def find_peaks(x, y):
    # Peaks should be no wider than 20 points
    search_length = 30
    short = 5
    # Put a dot at each peak
    # A peak must be 3 sigma above background
    xp, yp = [], []                       #Peak locations
    x_t, y_t = [], []                     #Temp array

    # Fit each peak to x+k+gauss
    ffunc = lambda p, x: p[0]*mf.gauss(x, p[1], p[2]) + x*p[3] + p[4]
        
    for xv, yv in zip(x,y):
        x_t.append(xv)
        y_t.append(yv)
        if len(x_t) >= search_length:
            mu = np.mean(y_t[-1:-search_length:-1])
            sig = np.std(y_t[-1:-search_length:-1])
            bg = np.mean(y_t[-search_length:-(short+search_length):-1])
            if sig > 2*math.sqrt(mu) and y_t[-1] < bg + math.sqrt(bg):
                # There is a peak nearby, lets find it
                peak = np.where(y_t==max(y_t[-1:-search_length:-1]))[0][0]
                if peak > short:
                    yp.append(y_t[peak])
                    xp.append(x_t[peak])
                    x_t, y_t = [], []

    # Add fits
    fit_distance = 40
    gr = mf.graph(x, y)
    fits=[]
    for xf, yf in zip(xp, yp):
        peak = np.where(x==xf)[0][0]
        xmin, xmax = (peak-fit_distance), (peak+fit_distance)
        bwidth = (x[xmax]-x[xmin])/len(x[xmin:xmax])
        p0 = [ (sum(y[xmin:xmax]) - len(y[xmin:xmax])*min(y[xmin:xmax]))*bwidth,
                xf, bwidth*5, 1, min(y[xmin:xmax])]
        fitter = mf.function(ffunc, p0, x[xmin], x[xmax])
        gr.fit(fitter)
        fits.append(fitter)

    return fits, xp, yp
