import pickle, numpy

class CorrectionFactor(object):


    def __init__(self, method, coreg=True):
        coregtag = {True:'coreg',False:'nocoreg'}[coreg]
        datafilepath = 'data/t1_factordata_{0}.pickle'.format(coregtag)
        with open(datafilepath) as datafile:
            factordata = pickle.load(datafile)
        self.dates = factordata[method]['dates']
        self.observed = numpy.array(factordata[method]['observed'])
        self.model = numpy.array(factordata[method]['model'])


    def byDate(self, targetdate):
        if targetdate in self.dates:
            refdate = targetdate
        else:
            deltas = [abs(d-targetdate) for d in self.dates]
            refdate = self.dates[deltas.index(min(deltas))]
            msg = 'No data for that session, using {0} instead.'
            print(msg.format(refdate))
        refdateIndex = self.dates.index(refdate)
        obs = self.observed[refdateIndex,:]
        mod = self.model[refdateIndex,:]
        return 1+((mod-obs)/mod).mean()
        
