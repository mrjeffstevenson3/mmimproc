""" Script to sample and fit some qt1 data from spgr images of a human subject.
Currently samples one slice at y=80.
"""
from __future__ import division
import datetime, glob, nibabel, numpy, scipy.optimize, pandas, seaborn
from numpy import radians
from os.path import join
from pylabs.utils.paths import getlocaldataroot
from pylabs.qt1.formulas import spgrformula
from pylabs.utils import progress
from niprov import Context
provenance = Context()
import warnings
from scipy.optimize import OptimizeWarning
warnings.simplefilter("ignore", OptimizeWarning)

fs = getlocaldataroot()
projectdir = join(fs, 'scsmethods')
subject = 'sub-scs376'
subjectdir = join(projectdir, subject)

alphafiles = sorted(glob.glob(join(subjectdir,'anat','*_fa_*brain.nii.gz')))
b1filter = '{}_b1map_phase_rfov_reg2qT1.nii.gz'
b1file = join(subjectdir, 'fmap', b1filter.format(subject))

alphas = [2.,10.,20.]
A = radians(alphas)
TR = 11. 
yslice = 80 # y coord that cuts through cerebellum

print('Sampling SPGR brain data..')
S = numpy.array([nibabel.load(f).get_data() for f in alphafiles]) # all data
B1 = nibabel.load(b1file).get_data() # B1 data
assert B1.shape == S.shape[1:]  # make sure they have same dimensions

S = S[:,:,[yslice],:]   #select one slice
B1 = B1[:,[yslice],:]   #select one slice
slicenvoxels = numpy.prod(S.shape[1:])  # total voxels in slice for debugging
coords = numpy.argwhere((S>0).all(axis=0))  #xyz coordinates with no zeros in S
nvoxels = coords.shape[0]                   # number of selected voxels
columnnames = ['x','y','z','S0','t1','B1']+alphas
voxelIndex = numpy.arange(nvoxels)+1
data = pandas.DataFrame(index=voxelIndex, columns=columnnames, dtype=float)

start = datetime.datetime.now()
for v in range(nvoxels):

            if v % 10 == 0:
                progress.progressbar(v, nvoxels, start)

            x, y, z = coords[v,:]
            Sv = S[:,x,y,z]
            B1v = B1[x,y,z]

            S0i = 15*Sv.max()
            Ab1 = A*(B1v/100)
            spgrformula.TR = TR
            T1i = 1000
            try:
                popt, pcov = scipy.optimize.curve_fit(
                                    spgrformula, Ab1, Sv, p0=[S0i, T1i])
            except RuntimeError as e:
                continue
            s0, t1 = popt
            data.loc[v] = [x, y, z, s0, t1, B1v]+list(Sv)

seaborn.distplot(data['t1'][data['t1']>300][data['t1']<3000]) # histogram
t1targets = numpy.arange(500, 2500, 200)
vx = [numpy.abs(data['t1']-t).argmin() for t in t1targets]
sample = data.loc[vx].set_index(t1targets)
print('')


