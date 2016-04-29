# J-correction for brains
from __future__ import division
import datetime, glob, nibabel, numpy, scipy.optimize
from numpy import radians
from os.path import join
from pylabs.utils.paths import getlocaldataroot
from pylabs.qt1.simplefitting import fitT1
from pylabs.utils import progress
from niprov import Context
provenance = Context()

fs = getlocaldataroot()
projectdir = join(fs, 'scsmethods')
subject = 'sub-scs376'
subjectdir = join(projectdir, subject)
#'source_parrec'

alphafiles = sorted(glob.glob(join(subjectdir,'anat','*_fa_*brain.nii.gz')))
b1filter = '{}_b1map_phase_rfov_reg2qT1.nii.gz'
b1file = join(subjectdir, 'fmap', b1filter.format(subject))

# ## Need j, TR, TE, T2s
#provenance.get(forFile=alphafiles[0]).provenance['repetition-time']
alphas = [2.,10.,20.]
TR = 11. 
# spgrWithJ(a, S0, T1)

Sa = numpy.array([nibabel.load(f).get_data() for f in alphafiles])
B1 = nibabel.load(b1file).get_data()
assert B1.shape == Sa.shape[1:]

start = datetime.datetime.now()
v = 0
dims = (10,10,10)
for x in range(dims[0]):
    for y in range(dims[1]):
        for z in range(dims[2]):

v +=1
x += 100
y += 100
z += 100

progress.progressbar(v, nvoxels, start)
    

Sa = Sa[:,x,y,z]
B1 = B1[x,y,z]

A = radians(alphas)


