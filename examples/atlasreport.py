#!/usr/bin/python 
from pylabs.correlation.atlas import report as atlasreport

testdir = '~/pylabs-testdata'
statfname = 'randpar_500_c4b21s19d_SOPT41totalcorrectmax3_all_F2_skeletonised.nii.gz_tfce_corrp_tstat2.nii.gz'
statfile = os.path.join(testdir, statfname)
atlasfile = os.path.join(testdir, 'mori1.img')


atlasreport(statfname, atlasfname)
