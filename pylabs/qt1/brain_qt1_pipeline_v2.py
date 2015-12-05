import os, sys
from glob import glob
from os.path import join as pathjoin
import collections
from collections import defaultdict
import cPickle, cloud
from cloud.serialization.cloudpickle import dumps
import nibabel.parrec as pr
from nibabel.volumeutils import fname_ext_ul_case
from pylabs.utils.paths import getlocaldataroot
from pylabs.conversion.phantom_conv import phantom_B1_midslice_par2mni
from pylabs.conversion.phantom_conv import phantom_midslice_par2mni
from nipype.interfaces import fsl


import sys, os, datetime
import itertools
import subprocess
from os.path import join as pathjoin
import fnmatch, collections, datetime, cPickle, cloud
import numpy as np
import scipy.ndimage
from dipy.segment.mask import median_otsu
import nibabel
import nibabel.parrec as pr
import nibabel.nifti1 as nifti1
from nibabel.volumeutils import fname_ext_ul_case
from nibabel.orientations import apply_orientation
from nibabel.orientations import inv_ornt_aff
from nibabel.orientations import io_orientation



from niprov import Context
from pylabs.utils._options import PylabsOptions
_opts = PylabsOptions()
prov = Context()
#opts.dryrun = True
#opts.verbose = True
verbose = True
from pylabs.utils import Shell

def sort_par_glob (parglob):
    return sorted(parglob, key=lambda f: int(f.split('_')[-2]))

fs = getlocaldataroot()
subjdirs = sorted(glob(pathjoin(fs, 'self_control/hbm_group_data/qT1/scs*')), key=lambda f: f.split('/')[-1])
dir = subjdirs[0]
for dir in subjdirs:
    subjSPGRparfiles = sort_par_glob(glob(pathjoin(dir, 'source_parrec/*T1_MAP*.PAR')))
    subjid = subjSPGRparfiles[0].split('/')[-3]
    niioutdir = pathjoin(dir, 'source_nii')
    if not os.path.exists(niioutdir):
        os.mkdir(niioutdir)

    sp = Shell()    #instantiate shell command
    cmd = 'parrec2nii --overwrite --scaling=fp --store-header --output-dir='       #no quoptes except outside
    cmd += niioutdir
    cmd += ' '+' '.join(subjSPGRparfiles)
    sp.run(cmd)
    fitoutdir = pathjoin(dir, 'fitted_qT1_spgr')
    if not os.path.exists(fitoutdir):
        os.mkdir(fitoutdir)
    inspgrs = glob(pathjoin(niioutdir, '*_T1_MAP_*.nii'))
    #spgr = inspgrs[0]
    bet = fsl.BET()

    for spgr in inspgrs:
        fa = spgr.split('_')[-4][0:2]
        bet.inputs.in_file = spgr
        bet.inputs.out_file = pathjoin(fitoutdir, subjid+'_fa_'+str(fa)+'_brain.nii.gz')
        bet.inputs.mask = True
        bet.inputs.robust = True
        bet.inputs.frac = 0.4
        bet.run()
