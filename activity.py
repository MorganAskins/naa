import json
from math import *
import numpy as np
import pylab as lab

#globals (units mostly)
y = 3.15569e7
a = 3.15569e7
d = 86400
h = 3600
m = 60
ms = 1e-3

def main():
    # Load in the experiment macro
    # fname = input('json experiment file: ')
    # with open(fname, 'r') as jfile:
    #     data = json.load(jfile)

    # #variables
    step_size = 1                           #milliseconds
    # xsec = data['cross section(b)'] * 1e-24    #cm^2
    # neutrons = data['megawh']*2.5e16
    # target = data['mass (g)'] / data['molar mass'] * 6.022e23

    # Fixed experiment as a test
    #sample = dict(40K=10000, 39K=1000000, 41K=100000)
    sample = {'40K': 10000, '42K': 1000000, '41K': 1000000}
    dbase = json.load(open('database/dbase.json', 'r'))
    
    # Assume running at 1 mw so 1mwh = 1 hour
    # Make plot of activity vs time
    time_axis = np.arange(0, 12*h, step_size)

    #### RUN EXPERIMENT ####
    lab.ion()
    print('Starting:',sample)
    for time in time_axis:
        # decay each sample
        decay(sample, dbase, step_size)
    print('Ending:',sample)
    
def decay(sample, db, time):
    add_back={}
    # Decay all of the elements
    for element in sample:
        info = search_iso(db, element)
        if info['half life'] == 'stable':
            continue
        Nnot = sample[element]
        k = log(2) / eval(info['half life'])
        N = Nnot * e**(-k*time)
        sample.update({element:N})
        add_back.update({info['daughters']: Nnot-N})

    # now add the decay products back in
    for element in add_back:
        if element in sample:
            total = sample[element]+add_back[element]
        else:
            total = add_back[element]
        sample.update({element: total})
        
    return

def produce():
    return 1

def search_iso(db, iso):
    return next((item for item in db if item['isotope'] == iso), None)
    
if __name__ == '__main__':
    main()
