import os, sys
import urllib.request as ur
import json
import re #regular expressions for parsing
import numpy as np
import h5py as h5

def populate():
    mine, maxe = '1.00', '20000.00'
    intensities = '10'
    lines = '50000'
    webaddr = 'http://atom.kaeri.re.kr/cgi-bin/readgam?' + \
      'xmin='+mine + '&xmax='+maxe + '&h=0.00' + \
      '&i='+intensities+'&l='+lines

    web=ur.urlopen(webaddr)
    
    xhtml = web.read().decode('utf-8')
    output = parse(xhtml)
    
    #save_to_hdf5(output)
    save_to_json(output)

def save_to_json(out):
    with open('gammalist.json', 'w') as fname:
        # Something is weird so lets run some tests
        print(len(out[0]), len(out[1]), len(out[2]), len(out[3]), len(out[4]))
        keys = [ ele[0] for ele in out ]
        dict_list = []
        for energy, intensity, element, decay, life in \
          zip(out[0][1:], out[1][1:], out[2][1:], out[3][1:], out[4][1:]):
            try:
                values = [ float(energy), float(intensity), element, decay, life ]
                dict_list.append(dict(zip(keys,values)))
            except ValueError as er:
                print(er)
        json.dump(dict_list, fname, indent=2)
        print('Wrote to:', fname.name)
    
def save_to_hdf5(out):
    # Not yet working
    with h5.File('gammalist.h5', 'w') as h5f:
        for columns in out:
            name, data = columns[0], [ele for ele in columns[1:] ]
            print('creating::::', name)
            h5f.create_dataset(name, data=data, dtype="S10")
    
def parse(xhtml):
    elements = [['Energy(keV)'], ['Intensity'], ['Nuclide'], ['Decay Mode'], ['Half life(s)']]
    for line in xhtml.split('\n'):
        if line.startswith('<tr>'):
            betterline = re.sub(r'<.+?>', ' ', line)
            betterline = re.sub(r'\(\s(.+?)\)', r'(\g<1>)', betterline)
            betterline = betterline.strip()
            betterline = re.sub(r'\(([^\s]*)\s([^\s]*)\s([^\s]*)\)', '\g<1> \g<2>\g<3>', betterline)
            betterline = betterline.split()[0:5]
            # Strip the errors from the energy
            betterline[0] = re.sub(r'\(.+?\)', '', betterline[0])
            while len(betterline) < 5:
                betterline.append('err')
            if betterline[0] != 'E':
                for idx, ele in enumerate(betterline):
                    elements[idx].append(ele)
            if betterline[2] == 'Br-82':
                print(betterline)
                    
    return elements
    
if __name__ == '__main__':
    populate()
