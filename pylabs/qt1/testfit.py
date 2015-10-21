import os, glob, collections
from os.path import join
import numpy
from scipy.optimize import curve_fit

path = 'data/phantomsampledata/'

data = collections.defaultdict(dict)

for xy in ('x','y'):
    for fpath in glob.glob(join(path, xy+'*')):
        coords = os.path.basename(fpath).split('_')[1].split('.')[0]
        with open(fpath) as datafile:
            lines = datafile.readlines()
        data[coords][xy] = [float(l) for l in lines]


def func(x, a, b, c):
    return a * numpy.exp(-b * x) + c


for coords in data.keys():
    print('Running for coordinates: '+coords)
    X = data[coords]['x']
    Y = data[coords]['y']

    popt, pcov = curve_fit(func, X, Y)



# todo polarity restoration

#y = S0 (1-V*e pow())

# 80,63,0  1727
# 46,65,0  1113
# 46,30,0   688
