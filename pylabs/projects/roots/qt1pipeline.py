import glob, os, pandas, numpy, niprov
from os.path import join
from pylabs.utils.paths import getlocaldataroot
from pylabs.correlation.correlate import correlateWholeBrain
from pylabs.qt1.vectorfitting import fitT1WholeBrain
from pylabs.conversion.helpers import par2mni_1file as conv
from pylabs.qt1.b1mapcoreg import b1mapcoreg_1file
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

## fit T1
files = []
for s, subject in enumerate(subjects):
    print('Converting parrecs for {} of {}: {}'.format(s, nsubjects, subject))
    parrecdir = join(subjectdirs[s], 'source_parrec')
    parsfiles = glob.glob(join(parrecdir, '*T1_MAP*.PAR'))
    sfiles = [conv(p) for p in parsfiles]
    parb1file = glob.glob(join(parrecdir, '*B1MAP*.PAR'))[0]
    b1fileLowRes = conv(parb1file)
    b1file = b1mapcoreg_1file(b1fileLowRes, sfiles[0])
    outfpath = join(subjectdirs[s], 'qT1', 't1_{}.nii.gz'.format(subject))
    print('T1 fitting subject {} of {}: {}'.format(s, nsubjects, subject))
    fitT1WholeBrain(sfiles, b1file, outfpath)
    files.append(outfpath)


## alignment?


## correlation
outfiles = correlateWholeBrain(files, variables)

## Clustering, clustertable? see nipy.labs.statistical_mapping.cluster_stats




