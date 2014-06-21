import numpy as np
import pylab as lab
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
    lab.ion()
    for t in range(0, total_steps, 600):
        height = []
        for iso in listofiso:
            height.append(iso[t])
        purity = listofiso[4][t] / (listofiso[4][t] + listofiso[6][t] + listofiso[7][t]) *100
        lab.clf()
        lab.ylim([1e3, 1e20])
        lab.xlabel('Isotopes')
        lab.title('time '+format(t/3600,'.1f')+' hours ~~ 239Pu purity = '+format(purity, '.2f')+'%')
        lab.ylabel('Abundance (atoms)')
        lab.xticks(index+bar_width/2, names)
        lab.bar(index, height, bar_width, log=True)
        lab.show()
        lab.pause(0.1)
        
if __name__ == '__main__':
    main()
