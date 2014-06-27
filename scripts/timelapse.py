import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn
#import time

def main():
    datfile = input('data: ')
    data = np.load(datfile)
    num_iso = len(data.files)-1
    listofiso, names = [], []

    time = data['time']
    for iso in data.files:
        if iso != 'time':
            listofiso.append(data[iso])
            names.append(iso)

    index = np.arange(num_iso)

    #refresh every 1/10 second where 1 second is 10 minutes so once per minute
    bar_width=0.35
    total_steps = len(time)
    plt.ion()
    for t in range(0, total_steps, 600):
        height = []
        for iso in listofiso:
            height.append(iso[t])
        purity = listofiso[4][t] / (listofiso[4][t] + listofiso[6][t] + listofiso[7][t]) *100
        plt.clf()
        plt.ylim([1e3, 1e20])
        plt.xlabel('Isotopes')
        plt.title('time '+format(t/3600,'.1f')+' hours ~~ 239Pu purity = '+format(purity, '.2f')+'%')
        plt.ylabel('Abundance (atoms)')
        plt.xticks(index+bar_width/2, names)
        plt.bar(index, height, bar_width, log=True)
        plt.show()
        plt.pause(0.1)
        
if __name__ == '__main__':
    main()
