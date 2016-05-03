import glob, os, pandas, numpy
from os.path import join
from pylabs.utils.paths import getlocaldataroot
from pylabs.correlation.correlate import correlateWholeBrain
fs = getlocaldataroot()
projectdir = join(fs, 'self_control','hbm_group_data','qT1')
subjects = [317, 328, 332, 334, 335, 347, 353, 364, 370, 371, 376, 379, 381, 
            384, 385, 396]
t1tem = join(projectdir, 'scs{}/T1_scs{}_b1corr_fcorr_byNearestDate.nii.gz')
t1files = [t1tem.format(s, s) for s in subjects]


## conversion to nii

## fit T1

## alignment?

## behavior
pos = numpy.arange(0, 1, 1./len(subjects))
neg = 1-pos
pos += numpy.random.rand(len(subjects))*.2
neg += numpy.random.rand(len(subjects))*.2
variables = pandas.DataFrame({'pos':pos, 'neg':neg}, index=subjects)

## correlation
outfiles = correlateWholeBrain(t1files, variables)




