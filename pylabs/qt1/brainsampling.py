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

alphas = [2.,10.,20.]
A = radians(alphas)
TR = 11. 

Sa = numpy.array([nibabel.load(f).get_data() for f in alphafiles])
B1 = nibabel.load(b1file).get_data()
assert B1.shape == Sa.shape[1:]

start = datetime.datetime.now()
v = 0
dims = (10,10,10)
nvoxels = numpy.prod(dims)
data = pandas.DataFrame(columns=['x','y','z','S','fit','B1'], dtype=float)
for x in range(dims[0]):
    for y in range(dims[1]):
        for z in range(dims[2]):

            v += 1
            x += 100
            y += 100
            z += 100

            progress.progressbar(v, nvoxels, start)

            Sv = Sa[:,x,y,z]
            B1v = B1[x,y,z]

            S0i = 15*Sa.max()
            Ab1 = A*(B1v/100)
            spgrformula.TR = TR
            T1i = 1000
            try:
                popt, pcov = optimize.curve_fit(
                                    spgrformula, Ab1, Sv, p0=[S0i, T1i])
            except RuntimeError as e:
                continue
            t1 = popt[1]


