from __future__ import print_function
import os, glob, numpy, pandas, seaborn, pickle
import matplotlib.pyplot as plt
from os.path import join
from mmimproc.utils.paths import getlocaldataroot
import mmimproc.graphics.tables as tables
from mmimproc.qt1.correction import CorrectionFactor
from mmimproc.utils.provenance import ProvenanceWrapper as ProvenanceContext
from mmimproc.qt1.temperaturedata import getSessionRecords
provenance = ProvenanceContext()
from mmimproc.correlation.atlas import atlaslabels
from mmimproc.qt1.vials import vialNumbersByAscendingT1
#usedVials = range(7, 18+1)
#vialOrderT1 = [str(v) for v in vialNumbersByAscendingT1 if v in usedVials]
atlasfname = 'phantom_slu_mask_20160113.nii.gz'
vials = atlaslabels(atlasfname)
del vials[vials.index('0')]
del vials[vials.index('18')]

rootdir = join(getlocaldataroot(),'self_control','hbm_group_data','qT1')
method = ('orig_spgr_mag', 14.0, True)

## Gather data
coreg = True
coregtag = {True:'coreg',False:'nocoreg'}[coreg]
datafilepath = 'data/t1_factordata_{0}.pickle'.format(coregtag)
with open(datafilepath) as datafile:
    allmethods = pickle.load(datafile)
methoddata = allmethods[method]
dates = methoddata['dates']
data = {}
for item in ['model', 'observed']:
    itemdata = numpy.array(methoddata[item])
    data[item] = pandas.DataFrame(itemdata, columns=vials, index=dates)
data = pandas.Panel(data)
data['diff'] = data['observed']-data['model']
data['%'] = data['diff']/data['model']*100

## Temperature
sessions = getSessionRecords('disc')
temps = pandas.Series({d:sessions[d].averageTemperature() for d in dates})

## Table 1A: Vial average
vialAverage = data.mean(axis=2)
vialAverage.insert(0, 'temperature', temps)
tables.toLatexAndPdf(vialAverage.round(2), 'table1a', tryImageMagickPNG=True)

## Table 1B: Vial 7
vial7 = data.minor_xs('7')
vial7.insert(0, 'temperature', temps)
tables.toLatexAndPdf(vial7.round(2), 'table1b', tryImageMagickPNG=True)

## correction
factor = CorrectionFactor(method, coreg=True)
factor.byNearestDate()

## Fig A date-average correction for 2 vials
#? Same as fig B?

## Fig B vial-wise correction for one date
june8date = dates[4]
june8 = data.major_xs(june8date)
june8['corrected'] = june8['observed']*factor.forDate(june8date)[0]
del june8['%']
del june8['diff']
june8.plot.bar()
plt.savefig('figB.png')

## Fig C date-wise correction
fig = plt.figure()
ax = vial7[['model', 'observed']].plot.bar()
ax2 = ax.twinx()
ax2.plot(vial7['%'])
plt.savefig('figC.png')



