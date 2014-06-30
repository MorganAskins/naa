# Test the pynaa class
import matplotlib.pyplot as plt
import matplotlib as mpl
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
        f.drawdata()
        f.drawfits()
        f.drawpeaks()
        
    plt.show()
    
if __name__ == '__main__':
    main(sys.argv)
    
