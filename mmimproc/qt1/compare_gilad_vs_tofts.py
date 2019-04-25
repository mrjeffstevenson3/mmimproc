import pickle, numpy
from mmimproc.qt1.plotting import plotT1Timeseries
from mmimproc.correlation.atlas import atlaslabels

coregtag = {True:'coreg',False:'nocoreg'}[True]
datafilepath = 'data/t1_factordata_{0}.pickle'.format(coregtag)
with open(datafilepath) as datafile:
    factordata = pickle.load(datafile)

giladkey = ('gilad_spgr_mag', 11.0, True)
toftskey = ('orig_spgr_mag', 11.0, False)

giladdates = factordata[giladkey]['dates']
toftsdates = factordata[toftskey]['dates']
commondates = set(giladdates).intersection(set(toftsdates))

giladDateIndices = [giladdates.index(d) for d in commondates]
toftsDateIndices = [toftsdates.index(d) for d in commondates]

gilad = numpy.array(factordata[giladkey]['observed'])[giladDateIndices,:]
tofts = numpy.array(factordata[toftskey]['observed'])[toftsDateIndices,:]
model = numpy.array(factordata[giladkey]['model'])[giladDateIndices,:]

atlasfname = 'T1_seir_mag_TR4000_2014-07-23_mask.nii.gz'
labels = atlaslabels(atlasfname)
labels = labels[1:] # remove label for background
dates = sorted(commondates)

## Difference to model:
giladRelDiff = (model-gilad)/model
toftsRelDiff = (model-tofts)/model

print('Tofts mean absolute difference from model: {:.2%}'.format(
    numpy.abs(toftsRelDiff).mean()))
print('Gilad mean absolute difference from model: {:.2%}'.format(
    numpy.abs(giladRelDiff).mean()))




## Direct difference
difference = gilad-tofts
reldiff = (difference/gilad)*100
print('Overall mean difference: {:.2}%'.format(numpy.abs(reldiff).mean()))
plotT1Timeseries(dates, difference, labels, 'gilad-v-tofts_absdiff', dtype='absdiff')
plotT1Timeseries(dates, reldiff, labels, 'gilad-v-tofts_refdiff', dtype='reldiff') 
