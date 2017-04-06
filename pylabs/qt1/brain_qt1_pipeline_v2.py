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
from pylabs.utils.provenance import ProvenanceWrapper
prov = ProvenanceWrapper()

#opts.dryrun = True
#opts.verbose = True
verbose = True
from pylabs.utils import Shell

def sort_par_glob (parglob):
    return sorted(parglob, key=lambda f: int(f.split('_')[-2]))

fs = getlocaldataroot()
subjdirs = sorted(glob(pathjoin(fs, 'self_control/hbm_group_data/qT1/scs*')), key=lambda f: f.split('/')[-1])
dir = subjdirs[0]
sp = Shell()    #instantiate shell command
bet = fsl.BET()    #instantiate fsl bet command
fslroi = fsl.ExtractROI()   #instantiate fslroi command
fslrfov = fsl.RobustFOV()     #instantiate robust fov command for cropping B1map before reg
fslflirt = fsl.FLIRT()
fslapplyxfm = fsl.ApplyXFM()

for dir in subjdirs:
    subjSPGRparfiles = sort_par_glob(glob(pathjoin(dir, 'source_parrec/*T1_MAP*.PAR')))
    subjB1MAPfiles = sort_par_glob(glob(pathjoin(dir, 'source_parrec/*B1MAP*.PAR')))
    subjid = subjSPGRparfiles[0].split('/')[-3]
    niioutdir = pathjoin(dir, 'source_nii')
    b1mapdir = pathjoin(dir, 'B1map_qT1')
    if not os.path.exists(niioutdir):
        os.mkdir(niioutdir)
    if not os.path.exists(b1mapdir):
        os.mkdir(b1mapdir)
    cmd = 'parrec2nii --overwrite --scaling=fp --store-header --output-dir='       #no quoptes except outside
    cmd += niioutdir
    cmd += ' '+' '.join(subjSPGRparfiles)
    sp.run(cmd)
    cmd = 'parrec2nii --overwrite --scaling=dv --store-header --output-dir='       #no quoptes except outside
    cmd += b1mapdir
    cmd += ' '+' '.join(subjB1MAPfiles)
    sp.run(cmd)
    fitoutdir = pathjoin(dir, 'fitted_qT1_spgr')
    if not os.path.exists(fitoutdir):
        os.mkdir(fitoutdir)
    inspgrs = glob(pathjoin(niioutdir, '*_T1_MAP_*.nii'))
    #spgr = inspgrs[0]
    fa02niifile = [s for s in inspgrs if '02B' in s][0]

    for b1map in subjB1MAPfiles:
        os.chdir(b1mapdir)
        fslroi = fsl.ExtractROI()
        fslroi.inputs.in_file = pathjoin(b1mapdir, subjB1MAPfiles[0].split('/')[-1].split('.')[-2]+'.nii')
        fslroi.inputs.roi_file = pathjoin(b1mapdir, subjid+'_b1map_mag.nii.gz')
        fslroi.inputs.t_min = 0
        fslroi.inputs.t_size = 1
        fslroi.run()
        fslroi = fsl.ExtractROI()
        fslroi.inputs.in_file = pathjoin(b1mapdir, subjB1MAPfiles[0].split('/')[-1].split('.')[-2]+'.nii')
        fslroi.inputs.roi_file = pathjoin(b1mapdir, subjid+'_b1map_phase.nii.gz')
        fslroi.inputs.t_min = 2
        fslroi.inputs.t_size = 1
        fslroi.run()
        fslrfov = fsl.RobustFOV()
        fslrfov.inputs.in_file = pathjoin(b1mapdir, subjid+'_b1map_mag.nii.gz')
        fslrfov.inputs.out_roi = pathjoin(b1mapdir, subjid+'_b1map_mag_rfov.nii.gz')
        fslrfov.inputs.terminal_output = 'file'
        fslrfov.run()
        with open('stdout.nipype', "rb") as f:
            cropvals = f.read().splitlines()
        zstart = int(float(cropvals[1].split()[-2]))
        zend = int(float(cropvals[1].split()[-1]))
        fslroi = fsl.ExtractROI()
        fslroi.inputs.in_file = pathjoin(b1mapdir, subjid+'_b1map_phase.nii.gz')
        fslroi.inputs.roi_file = pathjoin(b1mapdir, subjid+'_b1map_phase_rfov.nii.gz')
        fslroi.inputs.x_min = 0
        fslroi.inputs.x_size = -1
        fslroi.inputs.y_min = 0
        fslroi.inputs.y_size = -1
        fslroi.inputs.z_min = zstart
        fslroi.inputs.z_size = zend
        fslroi.run()
        fslflirt = fsl.FLIRT()
        fslflirt.inputs.in_file = pathjoin(b1mapdir, subjid+'_b1map_mag_rfov.nii.gz')
        fslflirt.inputs.reference = fa02niifile
        fslflirt.inputs.searchr_x = [-20, 20]
        fslflirt.inputs.searchr_y = [-20, 20]
        fslflirt.inputs.searchr_z = [-20, 20]
        fslflirt.inputs.interp = 'nearestneighbour'
        fslflirt.inputs.out_matrix_file = pathjoin(b1mapdir, subjid+'_b1map_mag_rfov_reg2qT1.mat')
        fslflirt.inputs.out_file = pathjoin(b1mapdir, subjid+'_b1map_mag_rfov_reg2qT1.nii.gz')
        fslflirt.run()
        fslapplyxfm = fsl.ApplyXFM()
        fslapplyxfm.inputs.in_file = pathjoin(b1mapdir, subjid+'_b1map_phase_rfov.nii.gz')
        fslapplyxfm.inputs.in_matrix_file = pathjoin(b1mapdir, subjid+'_b1map_mag_rfov_reg2qT1.mat')
        fslapplyxfm.inputs.interp = 'nearestneighbour'
        fslapplyxfm.inputs.out_file = pathjoin(b1mapdir, subjid+'_b1map_phase_rfov_reg2qT1.nii.gz')
        fslapplyxfm.inputs.apply_xfm = True
        fslapplyxfm.inputs.reference = fa02niifile
        fslapplyxfm.run()
        fslmaths = fsl.BinaryMaths()
        fslmaths.inputs.in_file = pathjoin(b1mapdir, subjid+'_b1map_phase_rfov_reg2qT1.nii.gz')
        fslmaths.inputs.operation = 'div'
        fslmaths.inputs.operand_value = 100
        fslmaths.inputs.out_file = pathjoin(b1mapdir, subjid+'_b1map_phase_rfov_reg2qT1_perc.nii.gz')
        fslmaths.run()
        fslmaths = fsl.BinaryMaths()
        fslmaths.inputs.in_file = pathjoin(b1mapdir, subjid+'_b1map_phase_rfov_reg2qT1_perc.nii.gz')
        fslmaths.inputs.operand_file = pathjoin(b1mapdir, subjid+'_b1map_phase_rfov_reg2qT1_perc.nii.gz')
        fslmaths.inputs.operation = 'mul'
        fslmaths.inputs.out_file = pathjoin(b1mapdir, subjid+'_b1map_phase_rfov_reg2qT1_squared.nii.gz')
        fslmaths.run()
        fslmaths = fsl.BinaryMaths()
        fslmaths.inputs.in_file = pathjoin(dir, 'T1_'+subjid+'.nii.gz')
        fslmaths.inputs.operand_file = pathjoin(b1mapdir, subjid+'_b1map_phase_rfov_reg2qT1_squared.nii.gz')
        fslmaths.inputs.operation = 'div'
        fslmaths.inputs.out_file = pathjoin(dir, 'T1_'+subjid+'_b1corr.nii.gz')
        fslmaths.run()

#     for spgr in inspgrs:
#         fa = spgr.split('_')[-4][0:2]
#         bet.inputs.in_file = spgr
#         bet.inputs.out_file = pathjoin(fitoutdir, subjid+'_fa_'+str(fa)+'_brain.nii.gz')
#         bet.inputs.mask = True
#         bet.inputs.robust = True
#         bet.inputs.frac = 0.4
#         bet.run()
