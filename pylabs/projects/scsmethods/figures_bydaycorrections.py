from __future__ import print_function
import os, glob, nibabel
from os.path import join
from pylabs.utils.paths import getlocaldataroot
from pylabs.qt1.correction import CorrectionFactor
from niprov import Context as ProvenanceContext

provenance = ProvenanceContext()
rootdir = join(getlocaldataroot(),'self_control','hbm_group_data','qT1')




## determine date range
subjects = {}
for subjectdir in glob.glob(join(rootdir, 'scs*')):
    subject = os.path.basename(subjectdir)
    parrecfile = glob.glob(join(subjectdir, 'source_parrec', '*.PAR'))[0]
    (img, status) = provenance.add(parrecfile)
    acqdate = img.provenance['acquired'].date()
    subjects[subject] = acqdate

factors = {}
for b1corr in [True, False]:
    method = ('orig_spgr_mag', 11.0, b1corr) 
    factors[b1corr] = CorrectionFactor(method, coreg=True)
    ## Choose either one of these:
    #factors[b1corr].byNearestDate()
    factors[b1corr].byDateRangeInterceptAndSlope(subjects.values())

tabledata = {True:{}, False:{}}

for subject in subjects.keys():
    acqdate = subjects[subject]
    print('Subject {0} data acquired {1}.'.format(subject, acqdate))
    subjectdir = join(rootdir, subject)
    for b1corr in [True, False]: 
        b1corrtag = {False:'',True:'_b1corr'}[b1corr]
        factor = factors[b1corr]
        rationalefilepath = outfile.replace('.nii.gz','.txt')
        print('Applying correction factor to: '+targetfname)
        x, rationale = factor.forDate(acqdate)
        corrdata = origdata*x
        with open(rationalefilepath, 'w') as logfile:
            logfile.write(rationale)
        tabledata[b1corr][subject] = x


for b1corr in [True, False]: 
    tdata = tabledata[b1corr]
    b1corrtag = {False:'',True:'_b1corr'}[b1corr]
    tablefname = 'fcor_table_{0}{1}.tsv'.format(factors[b1corr].name, b1corrtag)
    lines = ['{0}\t{1}'.format(s, tdata[s]) for s in tdata.keys()]
    content = '\n'.join(lines)
    with open(tablefname, 'w') as tablefile:
        tablefile.write(content)

