import pickle, numpy

coregtag = {True:'coreg',False:'nocoreg'}[True]
datafilepath = 'data/t1_factordata_{0}.pickle'.format(coregtag)
with open(datafilepath) as datafile:
    factordata = pickle.load(datafile)

giladkey = ('gilad_spgr_mag', 11.0, True)
toftskey = ('orig_spgr_mag', 11.0, True)

giladdates = factordata[giladkey]['dates']
toftsdates = factordata[toftskey]['dates']
commondates = set(giladdates).intersection(set(toftsdates))

giladDateIndices = [giladdates.index(d) for d in commondates]
toftsDateIndices = [toftsdates.index(d) for d in commondates]

gilad = numpy.array(factordata[giladkey]['observed'])[giladDateIndices,:]
tofts = numpy.array(factordata[toftskey]['observed'])[toftsDateIndices,:]
difference = gilad-tofts
