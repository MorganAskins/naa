# Todo: let the user put in units then do the conversions here

import json
import time
import datetime as dt

# This allows for tab completion of input file names and globbing
import readline, glob
def complete(text, state):
    return (glob.glob(text+'*')+[None])[state]
readline.set_completer_delims(' \t\n;')
readline.parse_and_bind('tab: complete')
readline.set_completer(complete)

def setup():

    # Read in details from the user and put them in a python dictionary, then json that file
    config={}
    
    print('\033[1;32mThis utility sets up an analysis config file to be read into a pynaa object\033[0;37m')
    config['samples']=glob.glob(input('\033[36mList of sample files (use tab complete/globbing): \033[37m'))
    config['sample name']=input('\033[0;33m -- Sample Name:\033[37m ')
    config['sample mass']=float(input('\033[0;33m    || Sample Mass(g):\033[37m '))
    config['backgrounds']=glob.glob(input('\033[36mList of background files (use tab complete/globbing): \033[37m'))
    print('\033[1;32mNow lets determine which controls were used')
    num_controls=int(input('\033[0;36mHow many control samples were used?:\033[37m '))
    print('\033[1;32mDescribe the control samples\033[0;37m')
    for ctrl in range(num_controls):
        ctrl_dict={}
        name='control <'+str(ctrl)+'>'
        print('\033[0;36m'+name)
        ctrl_dict['name'] = input('\033[0;33m -- Control Sample Name:\033[37m ')
        ctrl_dict['mass'] = float(input('\033[0;33m    || Sample Mass(g):\033[37m '))
        ctrl_dict['controls'] = glob.glob(input('\033[36mList of conrol files (use tab complete/globbing): \033[37m'))
        num_spikes = int(input('\033[0;36mHow many spikes in the control?:\033[37m '))
        for spikes in range(num_spikes):
            spike_dict={}
            spike_dict['isotope(eg. He-4)'] = input('\033[0;33m -- Isotope:\033[37m ')
            spike_dict['mass'] = float(input('\033[0;33m    || Mass(g):\033[37m '))
            ctrl_dict['spike <'+str(spikes)+'>'] = spike_dict
        config[name] = ctrl_dict
    print('\033[1;32mNow some reactor details\033[0;37m')
    print('\033[36mSample was placed in the reactor at: \033[37m')
    year = int(input('\033[33m -- Year: \033[37m'))
    month = int(input('\033[33m -- Month: \033[37m'))
    day = int(input('\033[33m -- Day: \033[37m'))
    hour = int(input('\033[33m -- Hour(24hr): \033[37m'))
    minute = int(input('\033[33m -- Minute: \033[37m'))
    second = int(input('\033[33m -- Second: \033[37m'))
    config['reactor power'] = float(input('\033[36mReactor power(MW): \033[37m'))
    config['exposure time'] = int(input('\033[36mExposure Time(seconds): \033[37m'))
    config['neutron flux'] = float(input('\033[36mNeutron Flux(/cm2/s): \033[37m'))

    reactor_on = (dt.datetime(year, month, day, hour, minute, second)-dt.datetime(1970,1,1)).total_seconds()

    config['exposure start'] = reactor_on
    filename = input('\033[1;31mSave file as(no extension): ')+'.json'
    with open(filename, 'w') as fopen:
        json.dump(config, fopen, indent=2)
    
if __name__ == '__main__':
    setup()
