import os, glob, collections
from os.path import join

path = 'data/phantomsampledata/'

data = collections.defaultdict(dict)

for xy in ('x','y'):
    for fpath in glob.glob(join(path, xy+'*')):
        coords = os.path.basename(fpath).split('_')[1].split('.')[0]
        with open(fpath) as datafile:
            lines = datafile.readlines()
        data[coords][xy] = [float(l) for l in lines]

