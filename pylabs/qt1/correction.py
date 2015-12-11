import pickle

class CorrectionFactor(object):


    def __init__(self, method, coreg=True):
        coregtag = {True:'coreg',False:'nocoreg'}[coreg]
        datafilepath = 'data/t1_factordata_{0}.pickle'.format(coregtag)
        with open(datafilepath) as datafile:
            factordata = pickle.load(datafile)
        self.dates = factordata[method]['dates']
        self.observed = factordata[method]['observed']
        self.model = factordata[method]['model']


    def byDate(self, targetdate):
        if targetdate in self.dates:
            refdate = targetdate
        else:
            deltas = [d-targetdate for d in self.dates]
            refdate = self.dates[deltas.index(min(deltas))]
            msg = 'No data for that session, using {0} instead.'
            print(msg.format(refdate))
        
