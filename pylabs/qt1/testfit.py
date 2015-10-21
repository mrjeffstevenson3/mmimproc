import os, glob, collections
from os.path import join
import numpy
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

path = 'data/phantomsampledata/'

data = collections.defaultdict(dict)

for xy in ('x','y'):
    for fpath in glob.glob(join(path, xy+'*')):
        coords = os.path.basename(fpath).split('_')[1].split('.')[0]
        with open(fpath) as datafile:
            lines = datafile.readlines()
        data[coords][xy] = [float(l) for l in lines]


def func(x, a, b, c):
    return numpy.abs(a * (1 - b * numpy.exp(-x/c)))


for coords in data.keys():
    print('Running for coordinates: '+coords)
    X = numpy.array(data[coords]['x'])
    Y = numpy.array(data[coords]['y'])


    ai = Y[0]
    bi = 2 # -Y[0]*2
    ci = 1000
    popt, pcov = curve_fit(func, X, Y, p0=[ai, bi, ci])
    print('   fitted parameters: a {0} b {1} c {2}'.format(*popt))



    # plot development over time for each vial
    Xrange = numpy.arange(5000)
    fit = [func(x, *popt) for x in Xrange]
    plt.plot(Xrange, fit) 
    plt.plot(X, Y, 'bo')
    plt.savefig('testT1fit.png')

# todo polarity restoration

#y = S0 (1-V*e pow())

# 80,63,0  1727
# 46,65,0  1113
# 46,30,0   688
