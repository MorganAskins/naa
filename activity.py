import json
from math import *
import numpy as np
import pylab as lab
import sys

#globals (units mostly)
y = 3.15569e7
a = 3.15569e7
d = 86400
h = 3600
m = 60
ms = 1e-3
b=1e-24
mol = 6.022e23

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
    dbase = json.load(open('database/dbase.json', 'r'))
    expmt = json.load(open(input('experiment: '), 'r'))
    
    # tot_k = 1*mol
    sample = expmt[1]
    for k, v in sample.items():
        sample.update({k: eval(v)})
    # sample = {'39K': tot_k*float(search_iso(dbase, '39K')['abundance']),
    #           '40K': tot_k*float(search_iso(dbase, '40K')['abundance']),
    #           '41K': tot_k*float(search_iso(dbase, '41K')['abundance'])}

    
    # Assume running at 1 mw so 1mwh = 1 hour
    # Make plot of activity vs time
    time_axis = np.arange(0, eval(expmt[0]['total time']), step_size)
    time_neutrons = eval(expmt[0]['reactor time'])
    neutron_flux = 2.5e16
    
    ## Save experiment ##
    # make a list of each data point then compare lengths of all data set
    # any that are not long enough add zeros onto the beginning

    saveme = []
    
    #### RUN EXPERIMENT ####
    #lab.ion()
    print('Initial sample:', sample)
    last=time_axis[0]
    for time in time_axis:
        if (time/time_axis[-1]) % 1000:
            sys.stdout.write('Completion: ' + format(time/time_axis[-1]*100,'.0f')+'%\r')
        # decay each sample
        dt=time-last
        last=time
        decay(sample, dbase, dt)
        if time < time_neutrons:
            reactor(sample, dbase, dt, neutron_flux)
        saveme.append(sample.copy())
        
    outname = 'output'
    saver(saveme, time_axis, outname)
    print('Final sample:',sample)

## Function definitions

def saver(save, time, output):
    
    names = list(save[-1].keys())    
    events = len(save)
    if len(time) != len(save):
        print('time and save length not equal??')
    values=[np.zeros(events) for name in names]

    for i, evts in enumerate(save):
        for j, name in enumerate(names):
            if name in evts:
                values[j][i] = evts[name]

    d={ 'time': time }
    for i, name in enumerate(names):
        d.update({name: values[i]})
    
        
    np.savez(output, **d)
    return
        
def decay(sample, db, time):
    add_back={}
    # Decay all of the elements
    for element in sample:
        info = search_iso(db, element)
        if not info:
            continue
        if info['half life'] == 'stable':
            continue
        Nnot = sample[element]
        k = log(2) / eval(info['half life'])
        N = Nnot * e**(-k*time)
        sample.update({element:N})
        if Nnot-N > 0.0:
            add_back.update({info['daughters']: Nnot-N})

    # now add the decay products back in
    for element in add_back:
        if element in sample:
            total = sample[element]+add_back[element]
        else:
            total = add_back[element]
        sample.update({element: total})
    return

def reactor(sample, db, time, flux):
    add_back={}
    for element in sample:
        info = search_iso(db, element)
        if not info:
            continue
        if info['neutron xsection']==0:
            continue
        Nnot = sample[element]
        N = Nnot * flux * eval(info['neutron xsection']) * time
        sample.update({element: (Nnot - N)})
        if N > 0:
            add_back.update({info['neutron product']: N})
    for element in add_back:
        if element in sample:
            total = sample[element]+add_back[element]
        else:
            total = add_back[element]
        sample.update({element: total})
    return
           

def search_iso(db, iso):
    return next((item for item in db if item['isotope'] == iso), None)
    
if __name__ == '__main__':
    main()
