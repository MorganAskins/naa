import mfit
import numpy as np
import pylab as lab

data=np.load('test.npz')
x,y=data['x'],data['y']
gr=mfit.graph(x,y)

#fit a gaussian plus a constant

ffunc = lambda p,x: p[0]*mfit.gauss(x, p[1], p[2]) + x*p[3] + p[4]
p0 = [10000, 511, 1, 1, 200]
fit = mfit.function(ffunc, p0=p0, xmin=500, xmax=520)
gr.fit(fit)
print('drawing')
#gr.bounds(500, 520)
gr.draw()
fit.draw()
print(fit.p0)
lab.show()

