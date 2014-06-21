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
    height=[0 for i in range(num_iso)]
    step_size = 3600*12                       #seconds
    for t in range(0, total_steps, step_size):
        hlast = height
        height = []
        for iso in listofiso:
            height.append(iso[t])
        
        activity= (np.array(hlast)-np.array(height))/step_size   # decays per second (dh per t )
        for i,a in enumerate(activity):
            if a<=1e-6:
                activity[i]=1e-6
        #activity = height
        purity = listofiso[4][t] / (listofiso[4][t] + listofiso[6][t] + listofiso[7][t]) *100
        lab.clf()
        lab.ylim([1e-6, 1e10])
        lab.xlabel('Isotopes')
        lab.title('time '+format(t/3600/24,'.1f')+' days')
        lab.ylabel('Activity Bq')
        lab.xticks(index+bar_width/2, names)
        lab.bar(index, activity, bar_width, log=True)
        lab.show()
        lab.pause(0.1)
        
if __name__ == '__main__':
    main()
