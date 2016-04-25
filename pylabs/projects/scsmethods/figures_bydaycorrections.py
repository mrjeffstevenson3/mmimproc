from __future__ import print_function
import os, glob, numpy, pandas, pickle, latex
from os.path import join
from pylabs.utils.paths import getlocaldataroot
from pylabs.qt1.correction import CorrectionFactor
from niprov import Context as ProvenanceContext
provenance = ProvenanceContext()
from pylabs.correlation.atlas import atlaslabels
from pylabs.qt1.vials import vialNumbersByAscendingT1
usedVials = range(7, 18+1)
vialOrderT1 = [str(v) for v in vialNumbersByAscendingT1 if v in usedVials]
atlasfname = 'phantom_slu_mask_20160113.nii.gz'
vials = atlaslabels(atlasfname)

rootdir = join(getlocaldataroot(),'self_control','hbm_group_data','qT1')
method = ('orig_spgr_mag', 14.0, True)

## Table 1: Vial average
coreg = True
coregtag = {True:'coreg',False:'nocoreg'}[coreg]
datafilepath = 'data/t1_factordata_{0}.pickle'.format(coregtag)
with open(datafilepath) as datafile:
    allmethods = pickle.load(datafile)
methoddata = allmethods[method]
dates = meth
vialAverage = pandas.DataFrame(index=data['dates'])
data = {}
for item in ['model', 'observed']:
    data[item] = pandas.DataFrame(columns=vials, index=dates)



    vialAverage[col] = [numpy.array(d).mean() for d in data[col]]
vialAverage['diff'] = vialAverage['observed']-vialAverage['model']
vialAverage['%'] = vialAverage['diff']/vialAverage['model']*100

## Table 1: Vial average export
content = vialAverage.to_latex()
header = "\documentclass[12pt]{article}\n\\usepackage{booktabs}\n\\begin{document}\n"
footer = "\end{document}"
tabledoc = header + content + footer
with open('table1.tex','w') as tablefile:
    tablefile.write(tabledoc)
pdf = latex.build_pdf(tabledoc)
pdf.save_to('table1.pdf')

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


