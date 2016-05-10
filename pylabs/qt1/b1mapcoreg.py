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


bet = fsl.BET()    #instantiate fsl bet command
fslroi = fsl.ExtractROI()   #instantiate fslroi command
fslrfov = fsl.RobustFOV()     #instantiate robust fov command for cropping B1map before reg
fslflirt = fsl.FLIRT()
fslapplyxfm = fsl.ApplyXfm()

def b1mapcoreg_1file(inb1path, fa02niifile):
    b1mapdir = os.path.dirname(inb1path)
    subjid = os.path.basename(inb1path)
    print('Starting B1 map coregistration etc..')
    olddir = os.getcwd()
    os.chdir(b1mapdir)
    fslroi = fsl.ExtractROI()
    fslroi.inputs.in_file = inb1path
    fslroi.inputs.roi_file = pathjoin(b1mapdir, subjid+'_b1map_mag.nii.gz')
    fslroi.inputs.t_min = 0
    fslroi.inputs.t_size = 1
    fslroi.run()
    fslroi = fsl.ExtractROI()
    fslroi.inputs.in_file = inb1path
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
    fslapplyxfm = fsl.ApplyXfm()
    fslapplyxfm.inputs.in_file = pathjoin(b1mapdir, subjid+'_b1map_phase_rfov.nii.gz')
    fslapplyxfm.inputs.in_matrix_file = pathjoin(b1mapdir, subjid+'_b1map_mag_rfov_reg2qT1.mat')
    fslapplyxfm.inputs.interp = 'nearestneighbour'
    fslapplyxfm.inputs.out_file = pathjoin(b1mapdir, subjid+'_b1map_phase_rfov_reg2qT1.nii.gz')
    fslapplyxfm.inputs.apply_xfm = True
    fslapplyxfm.inputs.reference = fa02niifile
    fslapplyxfm.run()
    os.chdir(olddir)
    return pathjoin(b1mapdir, subjid+'_b1map_phase_rfov_reg2qT1.nii.gz')

#    fslmaths = fsl.BinaryMaths()
#    fslmaths.inputs.in_file = pathjoin(b1mapdir, subjid+'_b1map_phase_rfov_reg2qT1.nii.gz')
#    fslmaths.inputs.operation = 'div'
#    fslmaths.inputs.operand_value = 100
#    fslmaths.inputs.out_file = pathjoin(b1mapdir, subjid+'_b1map_phase_rfov_reg2qT1_perc.nii.gz')
#    fslmaths.run()
#    fslmaths = fsl.BinaryMaths()
#    fslmaths.inputs.in_file = pathjoin(b1mapdir, subjid+'_b1map_phase_rfov_reg2qT1_perc.nii.gz')
#    fslmaths.inputs.operand_file = pathjoin(b1mapdir, subjid+'_b1map_phase_rfov_reg2qT1_perc.nii.gz')
#    fslmaths.inputs.operation = 'mul'
#    fslmaths.inputs.out_file = pathjoin(b1mapdir, subjid+'_b1map_phase_rfov_reg2qT1_squared.nii.gz')
#    fslmaths.run()
#    fslmaths = fsl.BinaryMaths()
#    fslmaths.inputs.in_file = pathjoin(dir, 'T1_'+subjid+'.nii.gz')
#    fslmaths.inputs.operand_file = pathjoin(b1mapdir, subjid+'_b1map_phase_rfov_reg2qT1_squared.nii.gz')
#    fslmaths.inputs.operation = 'div'
#    fslmaths.inputs.out_file = pathjoin(dir, 'T1_'+subjid+'_b1corr.nii.gz')
#    fslmaths.run()

