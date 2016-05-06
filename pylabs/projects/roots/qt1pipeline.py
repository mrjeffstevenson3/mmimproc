import glob, os, pandas, numpy
from os.path import join
from pylabs.utils.paths import getlocaldataroot
from pylabs.correlation.correlate import correlateWholeBrain
from pylabs.qt1.vectorfitting import fitT1WholeBrain
fs = getlocaldataroot()
projectdir = join(fs, 'roots_of_empathy')
subjectdirs = glob.glob(join(projectdir, 'sub-*'))
subjects = [os.path.basename(sd) for sd in subjectdirs]
nsubjects = len(subjects)
t1tem = join(projectdir, 'scs{}/T1_scs{}_b1corr_fcorr_byNearestDate.nii.gz')
files = [t1tem.format(s, s) for s in subjects]

## behavior
pos = numpy.arange(0, 1, 1./len(subjects))
neg = 1-pos
pos += numpy.random.rand(len(subjects))*.2
neg += numpy.random.rand(len(subjects))*.2
variables = pandas.DataFrame({'pos':pos, 'neg':neg}, index=subjects)

## conversion to nii

## fit T1
files = []
for s, subject in enumerate(subjects):
    print('T1 fitting subject {} of {}: {}'.format(s, nsubjects, subject))
    sfiles = glob.glob(join(subjectdirs[s], 'qT1', '*flip.nii.gz'))
    b1file = glob.glob(join(subjectdirs[s], 'qT1', '*b1map.nii.gz'))[0]
    files.append(fitT1WholeBrain(sfiles, b1file))


## alignment?


## correlation
outfiles = correlateWholeBrain(files, variables)




