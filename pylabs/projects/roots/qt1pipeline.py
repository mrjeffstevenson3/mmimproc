import glob, os, pandas, numpy, niprov
from os.path import join
from pylabs.utils.paths import getlocaldataroot
from pylabs.correlation.correlate import correlateWholeBrain
from pylabs.qt1.vectorfitting import fitT1WholeBrain
provenance = niprov.Context()

fs = getlocaldataroot()
projectdir = join(fs, 'roots_of_empathy')
subjectdirs = glob.glob(join(projectdir, 'sub-*'))
subjects = [os.path.basename(sd) for sd in subjectdirs]
nsubjects = len(subjects)

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
    for sfile in sfiles:
        provenance.add(sfile)
    b1file = join(subjectdirs[s], 'qT1', 'b1phase_reg_masked_s5.nii.gz')
    outfpath = join(subjectdirs[s], 'qT1', 't1_{}.nii.gz'.format(subject))
    fitT1WholeBrain(sfiles, b1file, outfpath)
    files.append(outfpath)


## alignment?


## correlation
outfiles = correlateWholeBrain(files, variables)




