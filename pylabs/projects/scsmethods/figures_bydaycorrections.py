from __future__ import print_function
import os, glob, numpy, pandas, pickle
from os.path import join
from pylabs.utils.paths import getlocaldataroot
from pylabs.qt1.correction import CorrectionFactor
from niprov import Context as ProvenanceContext

provenance = ProvenanceContext()
rootdir = join(getlocaldataroot(),'self_control','hbm_group_data','qT1')

method = ('orig_spgr_mag', 14.0, True)

coreg = True
coregtag = {True:'coreg',False:'nocoreg'}[coreg]
datafilepath = 'data/t1_factordata_{0}.pickle'.format(coregtag)
with open(datafilepath) as datafile:
    allmethods = pickle.load(datafile)
data = allmethods[method]
vialAverage = pandas.DataFrame(index=data['dates'])
for col in ['observed', 'model']:
    vialAverage[col] = [numpy.array(d).mean() for d in data[col]]
vialAverage['diff'] = vialAverage['observed']-vialAverage['model']
vialAverage['%'] = vialAverage['diff']/vialAverage['model']*100


factor = CorrectionFactor(method, coreg=True)
factor.byNearestDate()


## determine date range
subjects = {}
for subjectdir in glob.glob(join(rootdir, 'scs*')):
    subject = os.path.basename(subjectdir)
    parrecfile = glob.glob(join(subjectdir, 'source_parrec', '*.PAR'))[0]
    (img, status) = provenance.add(parrecfile)
    acqdate = img.provenance['acquired'].date()
    subjects[subject] = acqdate

for subject in subjects.keys():
    acqdate = subjects[subject]
    print('Subject {0} data acquired {1}.'.format(subject, acqdate))
    subjectdir = join(rootdir, subject)
    rationalefilepath = outfile.replace('.nii.gz','.txt')
    print('Applying correction factor to: '+targetfname)
    x, rationale = factor.forDate(acqdate)


