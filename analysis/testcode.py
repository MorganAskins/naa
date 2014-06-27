# Test the pynaa class
import pynaa as naa
import sys

def main(listoffiles):

    # I have built in exceptions so I could remove this and use try catch
    # real_list = [f for f in listoffiles if f.endswith('.npz')]
    physics = naa.analyzer(['test.npz'])

    for f in physics.filelist:
        print('ran from', f.tstart, 'to', f.tstop,
              'with a dead time of', f.deadtime, '%')
        f.peaks()

if __name__ == '__main__':
    main(sys.argv)
    
