import tarfile
import os, sys
from os.path import isfile

adr = 'http://www.ccfe.ac.uk/EASY-data/eaf2010/ENDF-6/isotopes_un.tar.gz'

def populate():
    fname = 'iso.tar.gz'
    directory = '.'
    print('downloading', adr)
    if not isfile(fname):
        download(adr, fname)
        #response = urllib.request.urlopen(adr)
        #urllib.request.urlretrieve(adr, fname)

    with tarfile.open(fname) as tfile:
        if tarfile.is_tarfile(fname):
            tfile.extractall(directory)
        else:
            print(fname, 'is not a tarfile')

    os.remove(fname)
    return

## Downloader

import urllib.request as ur

def reporter(count, blocksize, totalsize):
    percent = int(count*blocksize*100/totalsize)
    sys.stdout.write('Completion: ' + str(percent) + '%\r')
    sys.stdout.flush()

def download(adr, fname):
    ur.urlretrieve(adr, filename=fname, reporthook=reporter)

if __name__ == '__main__':
    populate()
