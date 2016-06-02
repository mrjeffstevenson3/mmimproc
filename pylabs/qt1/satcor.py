from __future__ import division
import collections, numpy, glob, datetime, pandas, itertools
from numpy import cos, sin, exp, tan, radians, power
import matplotlib.pyplot as plt
from os.path import join, isfile
from niprov import Context
from pylabs.utils.paths import getnetworkdataroot
from pylabs.qt1.fitting import spgrformula
from pylabs.qt1.model_pipeline import modelForDate, hasRecordForDate
from pylabs.qt1.vials import vialNumbersByAscendingT1
from pylabs.io.mixed import listOfDictsFromJson
from pylabs.qt1.simplefitting import fitT1
provenance = Context()

"""
This script uses the sampled phantom data (from phantoms.py) to determine
an appropriate stauration correction factor for a given TR and method.
"""

## settings
fs = getnetworkdataroot()
scanner = 'disc'
targetTR = 11.
targetMethod = 'spgr'
projectdir = join(fs, 'phantom_qT1_{}'.format(scanner))
phantoms = listOfDictsFromJson(join(projectdir, 'phantomdata.json'))
usedVials = range(7, 18+1)
vialOrder = [str(v) for v in vialNumbersByAscendingT1 if v in usedVials]

## Get brain sample:
# from pylabs.qt1.brainsampling import sample # sample a specific file to compare?

selectedPhantoms = [p for p in phantoms if 
    p['TR']==targetTR and p['method']==targetMethod]

data = pandas.Panel()
for phantom in selectedPhantoms:
    date = phantom['date']

    if not hasRecordForDate(date, scanner):
        print('\n\n\nNO TEMP FOUND FOR {}\n\n\n'.format(subject))
        continue
    data[date] = pandas.DataFrame(index=vialOrder, 
                    columns=['model','fit'], dtype=float)

    data[date]['model'] = modelForDate(date, scanner)[vialOrder]

    B1 = phantom['data']['b1']
    alphas = [a for a in phantom['data'].columns.values if a != 'b1']
    A = radians([float(a) for a in alphas])
    S = phantom['data'][alphas]
    data[date]['fit'] = fitT1(S, A, B1, targetTR)




