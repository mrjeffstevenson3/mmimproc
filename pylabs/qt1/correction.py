import pickle, numpy
import scipy.stats

class CorrectionFactor(object):


    def __init__(self, method, coreg=True):
        coregtag = {True:'coreg',False:'nocoreg'}[coreg]
        datafilepath = 'data/t1_factordata_{0}.pickle'.format(coregtag)
        with open(datafilepath) as datafile:
            factordata = pickle.load(datafile)
        self.method = method
        self.dates = factordata[method]['dates']
        self.observed = numpy.array(factordata[method]['observed'])
        self.model = numpy.array(factordata[method]['model'])
        self.reldiff = (self.model-self.observed)/self.model
        self.factor = {}
        self.rationale = {}

    def byNearestDate(self):
        self.name = 'byNearestDate'
        self.requiresPhantomReferenceDate = True
        ratiotem = ('method: {0}\nfactor: {1}\nrefdate: {2}'
            '\nphantom reference method: {3}')
        for d in self.dates:
            refdateIndex = self.dates.index(d)
            reldiffForDate = self.reldiff[refdateIndex,:]
            f = reldiffForDate.mean()
            self.factor[d] = f
            self.rationale[d] = ratiotem.format(self.name, f, d, self.method)

    def byDateRangeInterceptAndSlope(self, sampledates):
        self.name = 'byDateRangeInterceptAndSlope'
        self.requiresPhantomReferenceDate = False
        ratiotem = ('method: {0}\nfactor: {1}'
            '\nrefdate: {2}\nintercept: {3}\nslope: {4}'
            '\ndays after first phantom in range: {5}'
            '\nphantom reference method: {6}')
        start = min(sampledates)
        end = max(sampledates)
        pdaterange = [d for d in self.dates if d>start and d<end]
        pstart = min(pdaterange)
        x = [(d-pstart).days for d in pdaterange]
        y = [self.reldiff[self.dates.index(d),:].mean() for d in pdaterange]
        slope, intercept, r, p, std = scipy.stats.linregress(x,y)
        for d in sampledates:
            ndaysAfterStart = (d-pstart).days
            f = intercept + slope*ndaysAfterStart
            self.factor[d] = f
            self.rationale[d] = ratiotem.format(self.name, f, d, intercept, 
                slope, ndaysAfterStart, self.method)
        
    def nearestPhantomDateForSampleDate(self, targetdate):
        deltas = [abs(d-targetdate) for d in self.dates]
        refdate = self.dates[deltas.index(min(deltas))]
        msg = 'No data for that session, using {0} instead.'
        print(msg.format(refdate))
        return refdate

    def forDate(self, targetdate):
        refdate = targetdate
        if self.requiresPhantomReferenceDate:
            refdate = self.nearestPhantomDateForSampleDate(targetdate)
        return (1+self.factor[refdate], self.rationale[refdate])
        
