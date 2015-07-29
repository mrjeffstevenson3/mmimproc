#!/usr/bin/python 
import os, nibabel
from pylabs.correlation.atlas import report as atlasreport

testdir = os.path.expanduser('~/pylabs-testdata')
statfname = 'randpar_500_c4b21s19d_SOPT41totalcorrectmax3_all_F2_skeletonised.nii.gz_tfce_corrp_tstat2.nii.gz'
statfile = os.path.join(testdir, statfname)
atlasfile = os.path.join(testdir, 'mori1.img')
labelsfile = 'data/mori1.txt'
with open(labelsfile) as labelsfh:
    labels = [line.split()[1] for line in labelsfh.readlines()]

atlasreport(statfile, atlasfile, regionnames=labels)
