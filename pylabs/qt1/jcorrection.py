# J-correction for brains
from __future__ import division
import datetime, glob, nibabel, numpy, scipy.optimize
from numpy import radians
from os.path import join
from pylabs.utils.paths import getlocaldataroot
from pylabs.qt1.formulas import spgrWithJ, spgrformula
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
TR = 14. 
T2s = 50
TE = 4.6 #?
j = 9
# spgrWithJ(a, S0, T1)

Sa = numpy.array([nibabel.load(f).get_data() for f in alphafiles])
B1 = nibabel.load(b1file).get_data()
assert B1.shape == Sa.shape[1:]
Sa = Sa[:,100,100,100]
B1 = B1[100,100,100]

A = radians(alphas)
T1i = 1000
S0i = 15*Sa.max()
Ab1 = A*(B1/100)
spgrformula.TR = TR
popt, pcov = scipy.optimize.curve_fit(spgrformula, Ab1, Sa, p0=[S0i, T1i])
print(popt[1])
