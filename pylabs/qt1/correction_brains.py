from __future__ import print_function
import os, glob
from os.path import join
from pylabs.utils.paths import getlocaldataroot


rootdir = join(getlocaldataroot(),'self_control','hbm_group_data','qT1')

method = ('spgr',11,) + b1corr
factor = CorrectionFactor(method)

for subjectdir in glob.glob(join(rootdir, 'scs*')):
    subject = os.path.basename(subjectdir)

    # Determine date by getting parrec file in provenance
    parrecfile = glob.glob(join(subjectdir, 'source_parrec', '*.PAR'))[0]
    (img, status) = niprov.add(parrecfile)
    acqdate = img.provenance['acquired']

    for b1corr in [False, True]:
        b1corrtag = {False:'',True:'_b1corr'}[b1corr]
        targetfname = 'T1_{0}{1}.nii.gz'.format(subject, b1corrtag)
        targetfilepath = join(subjectdir,targetfname)
        outfile = targetfilepath.replace('.nii','_fcorr.nii')
        print('Applying correction factor to: '+targetfname)

        factor.byDate(acqdate)


