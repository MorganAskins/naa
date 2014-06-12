import json
import os

def main():
    keys=['isotope', 'neutron xsection',
          'abundance', 'half life', 'daughters', 'daughter ratio']
    pair=[]
    for el in keys:
        pair.append(input(el+': '))
    
    ele_dict = dict(zip(keys,pair))
    
    fname = 'dbase.json'
    ele_list=[]
    
    if os.path.isfile(fname):
        with open(fname, 'r') as dfile:
            ele_list = json.load(dfile)

    ele_list.append(ele_dict)
            
    with open(fname, 'w') as dfile:
        json.dump(ele_list, dfile, indent=2)

if __name__ == '__main__':
    main()
