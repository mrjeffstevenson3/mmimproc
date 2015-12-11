from __future__ import print_function
import os, glob, nibabel
from os.path import join
from pylabs.utils.paths import getlocaldataroot
from pylabs.qt1.correction import CorrectionFactor
from niprov import Context as ProvenanceContext

provenance = ProvenanceContext()
rootdir = join(getlocaldataroot(),'self_control','hbm_group_data','qT1')

method = ('orig_spgr_mag', 11.0, True) #need to adapt for non-b1, create two objs
factor = CorrectionFactor(method, coreg=True)

for subjectdir in glob.glob(join(rootdir, 'scs*')):
    subject = os.path.basename(subjectdir)

    parrecfile = glob.glob(join(subjectdir, 'source_parrec', '*.PAR'))[0]
    (img, status) = provenance.add(parrecfile)
    acqdate = img.provenance['acquired'].date()
    print('Subject {0} data acquired {1}.'.format(subject, acqdate))

    for b1corr in [True]:  #need to adapt for non-b1
        b1corrtag = {False:'',True:'_b1corr'}[b1corr]
        targetfname = 'T1_{0}{1}.nii.gz'.format(subject, b1corrtag)
        targetfilepath = join(subjectdir,targetfname)
        outfile = targetfilepath.replace('.nii','_fcorr.nii')
        print('Applying correction factor to: '+targetfname)
        x = factor.byDate(acqdate)
        print(x)
        origimg = nibabel.load(targetfilepath)
        origdata = origimg.get_data()
        corrdata = origdata*x
        corrimg = nibabel.Nifti1Image(corrdata, origimg.get_affine())
        nibabel.save(corrimg, outfile)


