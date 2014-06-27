import numpy as np
import json
import sys
from os.path import isfile
import warnings
with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    from pyne.xs.data_source import ENDFDataSource

'''
Reaction types in an endf file (of importance):

'''

def convert(endfFile):
    if not isfile(endfFile):
        return 1
    ext = '.endf'
    if not endfFile.endswith(ext):
        return 1
    en = ENDFDataSource(endfFile)
    isotope = (endfFile.split('/'))[-1].replace(ext, '')
    dict_list = []
    for i in range(2000):                 #arbitrarily chosen
        try:
            react = en.reaction(isotope, i)
            for key, value in react.items():
                if type(value) is np.ndarray:
                    react.update({key: value.tolist()})
            # Finally make sure the reaction knows which reaction
            # it actually is!!
            react.update({'reaction': i})
            dict_list.append(react)
        except (RuntimeError, KeyError) as er:
            pass

    new_ext = '.json'
    with open(endfFile.replace(ext, new_ext), 'w') as fname:
        json.dump(dict_list, fname, indent=2)
        print('Wrote to:', fname.name)
        
if __name__ == '__main__':
    for fileName in sys.argv:
        convert(fileName)
