# todo: fix brain extraction by increasing z dim (and maybe xy) to accomodate brain stem and cerebellum of dwi or pre-crop MNI before reg
# todo: add timestamp to status updates
# todo: add dipy save evals and evecs and convert to AFQ dt6.mat
# first set global root data directory
import mmimproc
mmimproc.datadir.target = 'jaba'
import os, itertools
from pathlib import *
from collections import defaultdict
import time
import json
import nipype
from nipype.interfaces import fsl
import nibabel as nib
import numpy as np
import pandas as pd
# working dipy denoise for dki
from dipy.denoise.noise_estimate import estimate_sigma
from dipy.denoise.non_local_means import non_local_means
from dipy.io import read_bvals_bvecs
from dipy.core.gradients import gradient_table
import dipy.reconst.dki as dki
import dipy.reconst.dti as dti
from dipy.reconst.dti import mode
import shutil
import datetime
from scipy.ndimage.filters import median_filter as medianf
from mmimproc.structural.brain_extraction import extract_brain
from mmimproc.conversion.brain_convert import conv_subjs, find_subjs2conv
from mmimproc.conversion.nifti2nrrd import nii2nrrd
from mmimproc.conversion.parrec2nii_convert import mergeddicts
from mmimproc.alignment.ants_reg import subj2templ_applywarp
from mmimproc.correlation.atlas import mori_network_regions
from mmimproc.io.images import savenii
from mmimproc.io.mixed import h52df
from mmimproc.utils import *
#set up provenance
prov = ProvenanceWrapper()

# project, subject, and file objects to work on
from mmimproc.projects.acdc.file_names import project, SubjIdPicks, get_dwi_names, Optsd, merge_ftempl_dicts
from mmimproc.conversion.brain_convert import acdc_conv

#setup paths and file names to process
fs = mmimproc.fs_local

antsRegistrationSyN = get_antsregsyn_cmd()
slicer_path = getslicercmd(ver='stable')
opts = Optsd()

if not opts.dwi_qc and not opts.dwi_pass_qc == '':
    opts.dwi_pass_qc = ''

# instantiate subject id list container
subjids_picks = SubjIdPicks()
# list of subject ids to operate on
picks = [
         {'subj': 'sub-acdctest_jan17', 'session': 'ses-1', 'run': '1', },  # subject selection info
        ]

setattr(subjids_picks, 'subjids', picks)

opts.test = False
skip_tup_eddy_cmds = False
skip_mat = False
new_mask = False

# commands and options are modified below.
# topup command for unwarping dti
topup_cmd = 'topup --imain={topup_dn_fname} --datain=acq_params.txt --config=b02b0.cnf --out={topup_out}'
topup_cmd += ' --iout={topup_out}_unwarped.nii.gz --fout={topup_out}_topdn_concat_mf_warp_field.nii.gz'
# makes mean of unwarped topup down b0 for brain extraction, mask, b0
mean_b0_cmd = 'fslmaths {topup_out}_unwarped -Tmean {topup_out}_unwarped_mean.nii.gz'
# fsl eddy cmd using cuda for speedup. Warning: add --data_is_shelled flag to eddy cmd if the error 'Data not shelled' crops up
eddy_cmd = 'eddy_cuda8.0 --imain={dwif_fname} --mask={b0_brain_mask_fname} --acqp=../acq_params.txt  --index=../index.txt'
eddy_cmd += ' --bvecs={dwi_bvecs_fname} --bvals={dwi_bvals_fname} --topup={topup_out} --repol --ol_nstd=1.96 --out={ec_dwi_fname}' ## --data_is_shelled'

# fsl dtifit command dict to make FA, MD maps etc. then filter tensor, then recon filtered data
fsl_fit_cmds = ['dtifit -k %(ec_dwi_clamp_fname)s -o %(fsl_fits_out)s -m %(b0_brain_mask_fname)s -b %(dwi_bvals_fname)s -r %(dwi_bvecs_ec_rot_fname)s --save_tensor --wls --sse',
                'fslmaths %(fsl_fits_out)s_tensor -fmedian %(fsl_fits_out)s_tensor%(mf_str)s',
                'fslmaths %(fsl_fits_out)s_tensor%(mf_str)s -tensor_decomp %(fsl_fits_out)s_tensor%(mf_str)s',
                'imcp %(fsl_fits_out)s_tensor%(mf_str)s_L1 %(fsl_fits_out)s_tensor%(mf_str)s_AD',
                'fslmaths %(fsl_fits_out)s_tensor%(mf_str)s_L2 -add %(fsl_fits_out)s_tensor%(mf_str)s_L3 -div 2 %(fsl_fits_out)s_tensor%(mf_str)s_RD -odt float',
                'imcp %(fsl_fits_out)s_S0 %(fsl_fits_out)s_tensor%(mf_str)s_S0',
                'fslmaths %(fsl_fits_out)s_tensor -fmedian %(fsl_fits_out)s_tensor%(mf_str)s',     # need to repeat and overwrite because tensor decomp overwrites with FA
                ]

# slicer UKF commands and default parameters to run
ukfcmds =  {'UKF_whbr': str(slicer_path) + 'UKFTractography --dwiFile %(dwi_nrrd_fname)s --seedsFile %(b0_brain_mask_fname_nrrd)s'
                    ' --labels 1 --maskFile %(b0_brain_mask_fname_nrrd)s --tracts %(ec_dwi_fname)s_mf_clamp1_UKF_whbr.vtk'
                    ' --seedsPerVoxel 1 --seedingThreshold 0.18 --stoppingFA 0.15 --stoppingThreshold 0.1 --numThreads -1'
                    ' --numTensor 2 --stepLength 0.3 --Qm 0 --recordLength 0.9 --maxHalfFiberLength 250 --recordNMSE --freeWater'
                    ' --recordFA --recordTrace --recordFreeWater --recordTensors --Ql 0 --Qw 0 --Qkappa 0.01 --Qvic 0.004'
                    ' --Rs 0 --sigmaSignal 0 --maxBranchingAngle 0 --minBranchingAngle 0 --minGA 10000',

            'NODDI1': str(slicer_path) + 'UKFTractography --dwiFile %(dwi_nrrd_fname)s --seedsFile %(b0_brain_mask_fname_nrrd)s'
                    ' --labels 1 --maskFile %(b0_brain_mask_fname_nrrd)s --tracts %(ec_dwi_fname)s_mf_clamp1_whbr_1tensor_noddi.vtk'
                    ' --seedsPerVoxel 1 --seedingThreshold 0.18 --stoppingFA 0.15 --stoppingThreshold 0.1 --numThreads -1'
                    ' --numTensor 1 --stepLength 0.3 --Qm 0 --recordLength 0.9 --maxHalfFiberLength 250 --Ql 0 --Qw 0'
                    ' --noddi --recordVic --recordKappa --recordViso --Qkappa 0.01 --Qvic 0.004 --Rs 0 --sigmaSignal 0'
                    ' --maxBranchingAngle 0 --minBranchingAngle 0 --minGA 10000',
            'NODDI2': str(slicer_path) + 'UKFTractography --dwiFile %(dwi_nrrd_fname)s --seedsFile %(b0_brain_mask_fname_nrrd)s'
                     ' --labels 1 --maskFile %(b0_brain_mask_fname_nrrd)s --tracts %(ec_dwi_fname)s_mf_clamp1_whbr_2tensor_noddi.vtk'
                     ' --seedsPerVoxel 1 --seedingThreshold 0.18 --stoppingFA 0.15 --stoppingThreshold 0.1 --numThreads -1'
                     ' --numTensor 2 --stepLength 0.3 --Qm 0 --recordLength 0.9 --maxHalfFiberLength 250 --Ql 0 --Qw 0'
                     ' --noddi --recordVic --recordKappa --recordViso --Qkappa 0.01 --Qvic 0.004 --Rs 0 --sigmaSignal 0'
                     ' --maxBranchingAngle 0 --minBranchingAngle 0 --minGA 10000',
            }

# to get indices of upper triangle of tensor for fsl compatibility
_ut_rows = np.array([0, 0, 0, 1, 1, 2])
_ut_cols = np.array([0, 1, 2, 1, 2, 2])
_all_cols = np.zeros(9, dtype=np.int)
_all_rows = np.zeros(9, dtype=np.int)
for i, j in enumerate(list(itertools.product(*(range(3), range(3))))):
    _all_rows[i] = int(j[0])
    _all_cols[i] = int(j[1])


# define local functions
def default_to_regular(d):
    if isinstance(d, defaultdict):
        d = {k: default_to_regular(v) for k, v in d.items()}
    return d


def test4file(file):
    file = Path(file)
    if file.is_file():
        return True
    else:
        raise ValueError(str(file) + ' not found.')

#  define hostnames with working gpus for processing
flt = fsl.FLIRT(bins=640, interp='nearestneighbour', cost_func='mutualinfo', output_type='NIFTI_GZ')
if nipype.__version__ == '0.12.0':
    applyxfm = fsl.ApplyXfm(interp='nearestneighbour', output_type='NIFTI_GZ')
else:
    applyxfm = fsl.ApplyXFM(interp='nearestneighbour', output_type='NIFTI_GZ')

print(os.environ['FSLOUTPUTTYPE'])

"""
pick dict guide:
'subj' = subject being processed
'session' = session being processed
'topup_dn_fname' = combined topup and topdown pre unwarping
'topup_out' = topup out file basename for unwarping
'dwi_fname' = dwi file name to be processed if qc then opts.dwi_pass_qc appended to name
'ec_dwi_fname' = eddy current corrected dwi file for fits and bedpost
'dwi_bvecs_ec_rot_fname' = ec rotated bvecs to be used for fits, bedpost etc
"""

dwi_picks = get_dwi_names(subjids_picks)

if opts.test:
    i = 0
    dwi_picks = [dwi_picks[i]]
# run conversion if needed
if opts.convert:  # add test for overwrite converted and test if subjects in picks dict list.
    subjects = find_subjs2conv(project)
    niftiDict, niftiDF = conv_subjs(project, subjects)
result = ('starting time for dwi preproc pipeline is {:%Y %m %d %H:%M}'.format(datetime.datetime.now()),)

for i, pick in enumerate(dwi_picks):
    start_time = time.time()
    print('working on dwi preproc for {project} subject {subj} session {session}'.format(**pick))
    print('starting time for pipeline is {:%Y %m %d %H:%M}'.format(datetime.datetime.now()))
    result += ('working on dwi preproc for {project} subject {subj} session {session}'.format(**pick),)
    result += ('starting time for pipeline is {:%Y %m %d %H:%M}'.format(datetime.datetime.now()),)
    # MNI2dwi_regpath = fs / project / '{subj}/{session}/reg'.format(**pick) / opts.MNI2dwi
    if not pick['eddy_path'].is_dir():
        pick['eddy_path'].mkdir(parents=True)
    # if not MNI2dwi_regpath.is_dir():
    #     MNI2dwi_regpath.mkdir(parents=True)
    # define files
    orig_dwif_fname = pick['dwi_path'] / '{dwi_fname}.nii'.format(**pick)
    orig_dwi_bvals_fname = pick['dwi_path'] / '{dwi_fname}.bvals'.format(**pick)
    orig_dwi_bvecs_fname = pick['dwi_path'] / '{dwi_fname}.bvecs'.format(**pick)
    dwi_dwellt_fname = pick['dwi_path'] / '{dwi_fname}.dwell_time'.format(**pick)
    orig_topup_fname = pick['dwi_path'] / '{topup_fname}.nii'.format(**pick)
    orig_topdn_fname = pick['dwi_path'] / '{topdn_fname}.nii'.format(**pick)
    topup_dwellt_fname = pick['dwi_path'] / '{topup_fname}.dwell_time'.format(**pick)
    topdn_dwellt_fname = pick['dwi_path'] / '{topdn_fname}.dwell_time'.format(**pick)
    # test they exist
    for f in [orig_dwif_fname, orig_dwi_bvals_fname, orig_dwi_bvecs_fname, dwi_dwellt_fname, orig_topup_fname,
              topup_dwellt_fname, orig_topdn_fname, topdn_dwellt_fname]:
        test4file(f)
    # get data
    orig_dwi_img = nib.load(str(orig_dwif_fname))
    orig_dwi_data = orig_dwi_img.get_data().astype(np.float64)
    orig_dwi_affine = orig_dwi_img.affine
    orig_topup_img = nib.load(str(orig_topup_fname))
    orig_topup_data = orig_topup_img.get_data().astype(np.float64)
    orig_topup_affine = orig_topup_img.affine
    orig_topdn_img = nib.load(str(orig_topdn_fname))
    orig_topdn_data = orig_topdn_img.get_data().astype(np.float64)
    orig_topdn_affine = orig_topdn_img.affine
    if orig_topup_data.shape[2] % 2 == 0:
        even_sl = True
    else:
        even_sl = False

    # select volumes that pass dwi qc
    if pick['dwi_qc']:
        vis_qc = h52df(pick['info_fname'], '/{subj}/{session}/dwi/vis_qc'.format(**pick))
        vis_qc.replace({'True': True, 'False': False}, inplace=True)
        dwi_good_vols = vis_qc[vis_qc.dwi_visqc]
        topup_goodvols = vis_qc[vis_qc.itopup_visqc]
        topdn_goodvols = vis_qc[vis_qc.itopdn_visqc]
        dwi_bvals_fname = appendposix(orig_dwi_bvals_fname, pick['dwi_pass_qc'])
        pick['dwi_bvals_fname'] = dwi_bvals_fname
        dwi_bvecs_fname = appendposix(orig_dwi_bvecs_fname, pick['dwi_pass_qc'])
        pick['dwi_bvecs_fname'] = dwi_bvecs_fname
        topup_fname = appendposix(orig_topup_fname, pick['dwi_pass_qc'])
        topdn_fname = appendposix(orig_topdn_fname, pick['dwi_pass_qc'])
        pick['dwif_fname'] = appendposix(orig_dwif_fname, pick['dwi_pass_qc'])
        dwi_good_vols[[u'x_bvec', u'y_bvec', u'z_bvec']].T.to_csv(str(dwi_bvecs_fname), index=False, header=False, sep=' ')
        pd.DataFrame(dwi_good_vols[u'bvals']).T.to_csv(str(dwi_bvals_fname), index=False, header=False, sep=' ')
        bvecs = dwi_good_vols[[u'x_bvec', u'y_bvec', u'z_bvec']].T.values
        bvals = pd.DataFrame(dwi_good_vols[u'bvals']).T.values[0]
        gtab = gradient_table(bvals, bvecs)
        # set target shapes
        if even_sl:
            if pick['dwi_add_blanks']:  # add slice above and below
                topup_goodvols_shape = orig_topup_data.shape[:2] + (orig_topup_data.shape[2] + 2,) + (len(topup_goodvols.index),)
                topdn_goodvols_shape = orig_topdn_data.shape[:2] + (orig_topdn_data.shape[2] + 2,) + (len(topdn_goodvols.index),)
                dwi_goodvols_shape = orig_dwi_data.shape[:2] + (orig_dwi_data.shape[2] + 2,) + (len(dwi_good_vols.index),)
                topup_data = np.zeros(topup_goodvols_shape)
                topdn_data = np.zeros(topdn_goodvols_shape)
                dwi_data = np.zeros(dwi_goodvols_shape)
                topup_data[:, :, 1:topup_goodvols_shape[2]-1, :] = orig_topup_data[:,:,:,np.array(topup_goodvols.index)]
                topdn_data[:, :, 1:topdn_goodvols_shape[2]-1, :] = orig_topdn_data[:,:,:,np.array(topdn_goodvols.index)]
                dwi_data[:, :, 1:dwi_goodvols_shape[2]-1, :] = orig_dwi_data[:,:,:,np.array(dwi_good_vols.index)]
            else: # keep original slices with good volumes and run eddy
                topup_data = orig_topup_data[:,:,:,np.array(topup_goodvols.index)]
                topdn_data = orig_topdn_data[:,:,:,np.array(topdn_goodvols.index)]
                dwi_data = orig_dwi_data[:,:,:,np.array(dwi_good_vols.index)]
        else:
            if pick['dwi_add_blanks']:# correct odd number slices with 2 blanks on top and 1 on bottom
                topup_goodvols_shape = orig_topup_data.shape[:2] + (orig_topup_data.shape[2] + 3,) + (len(topup_goodvols.index),)
                topdn_goodvols_shape = orig_topdn_data.shape[:2] + (orig_topdn_data.shape[2] + 3,) + (len(topdn_goodvols.index),)
                dwi_goodvols_shape = orig_dwi_data.shape[:2] + (orig_dwi_data.shape[2] + 3,) + (len(dwi_good_vols.index),)
                topup_data = np.zeros(topup_goodvols_shape)
                topdn_data = np.zeros(topdn_goodvols_shape)
                dwi_data = np.zeros(dwi_goodvols_shape)
                topup_data[:, :, 1:orig_topup_data[2]-2, :] = orig_topup_data[:,:,:,np.array(topup_goodvols.index)]
                topdn_data[:, :, 1:orig_topdn_data[2]-2, :] = orig_topdn_data[:,:,:,np.array(topdn_goodvols.index)]
                dwi_data[:, :, 1:dwi_goodvols_shape[2]-2, :] = orig_dwi_data[:,:,:,np.array(dwi_good_vols.index)]
            else: # correct odd number slices with 1 blank on top
                topup_goodvols_shape = orig_topup_data.shape[:2] + (orig_topup_data.shape[2] + 1,) + (len(topup_goodvols.index),)
                topdn_goodvols_shape = orig_topdn_data.shape[:2] + (orig_topdn_data.shape[2] + 1,) + (len(topdn_goodvols.index),)
                dwi_goodvols_shape = orig_dwi_data.shape[:2] + (orig_dwi_data.shape[2] + 1,) + (len(dwi_good_vols.index),)
                topup_data = np.zeros(topup_goodvols_shape)
                topdn_data = np.zeros(topdn_goodvols_shape)
                dwi_data = np.zeros(dwi_goodvols_shape)
                topup_data[:, :, :-1, :] = orig_topup_data[:,:,:,np.array(topup_goodvols.index)]
                topdn_data[:, :, :-1, :] = orig_topdn_data[:,:,:,np.array(topdn_goodvols.index)]
                dwi_data[:, :, :-1, :] = orig_dwi_data[:,:,:,np.array(dwi_good_vols.index)]

    else:   # select all volumes without any qc
        bvals, bvecs = read_bvals_bvecs(str(orig_dwi_bvals_fname), str(orig_dwi_bvecs_fname))
        gtab = gradient_table(bvals, bvecs)
        pick['dwif_fname'] = orig_dwif_fname
        dwi_bvals_fname = orig_dwi_bvals_fname
        dwi_bvecs_fname = orig_dwi_bvecs_fname
        topup_fname = orig_topup_fname
        topdn_fname = orig_topdn_fname
        if even_sl:
            if pick['dwi_add_blanks']:
                topup_shape = orig_topup_data.shape[:2] + (orig_topup_data.shape[2] + 2,) + (orig_topup_data.shape[3],)
                topdn_shape = orig_topdn_data.shape[:2] + (orig_topdn_data.shape[2] + 2,) + (orig_topdn_data.shape[3],)
                dwi_shape = orig_dwi_data.shape[:2] + (orig_dwi_data.shape[2] + 2,) + (orig_dwi_data.shape[3],)
                topup_data = np.zeros(topup_shape)
                topdn_data = np.zeros(topdn_shape)
                dwi_data = np.zeros(dwi_shape)
                topup_data[:, :, 1:-1, :] = orig_topup_data
                topdn_data[:, :, 1:-1, :] = orig_topdn_data
                dwi_data[:, :, 1:-1, :] = orig_dwi_data
            else:
                topup_data = orig_topup_data
                topdn_data = orig_topdn_data
                dwi_data = orig_dwi_data
        else:
            if pick['dwi_add_blanks']:
                topup_shape = orig_topup_data.shape[:2] + (orig_topup_data.shape[2] + 3,) + (orig_topup_data.shape[3],)
                topdn_shape = orig_topdn_data.shape[:2] + (orig_topdn_data.shape[2] + 3,) + (orig_topdn_data.shape[3],)
                dwi_shape = orig_dwi_data.shape[:2] + (orig_dwi_data.shape[2] + 3,) + (orig_dwi_data.shape[3],)
                topup_data = np.zeros(topup_shape)
                topdn_data = np.zeros(topdn_shape)
                dwi_data = np.zeros(dwi_shape)
                topup_data[:, :, 1:-2, :] = orig_topup_data
                topdn_data[:, :, 1:-2, :] = orig_topdn_data
                dwi_data[:, :, 1:-2, :] = orig_dwi_data
            else:
                topup_shape = orig_topup_data.shape[:2] + (orig_topup_data.shape[2] + 1,) + (orig_topup_data.shape[3],)
                topdn_shape = orig_topdn_data.shape[:2] + (orig_topdn_data.shape[2] + 1,) + (orig_topdn_data.shape[3],)
                dwi_shape = orig_dwi_data.shape[:2] + (orig_dwi_data.shape[2] + 1,) + (orig_dwi_data.shape[3],)
                topup_data = np.zeros(topup_shape)
                topdn_data = np.zeros(topdn_shape)
                dwi_data = np.zeros(dwi_shape)
                topup_data[:, :, :-1, :] = orig_topup_data
                topdn_data[:, :, :-1, :] = orig_topdn_data
                dwi_data[:, :, :-1, :] = orig_dwi_data

    savenii(topup_data, orig_topup_affine, topup_fname)
    savenii(topdn_data, orig_topdn_affine, topdn_fname)
    savenii(dwi_data, orig_dwi_affine, pick['dwif_fname'])

    # make acq_params and index files for fsl eddy
    with open(str(topup_dwellt_fname), 'r') as tud:
        topup_dwellt = tud.read().replace('\n', '')

    with open(str(topdn_dwellt_fname), 'r') as tdd:
        topdn_dwellt = tdd.read().replace('\n', '')

    topup_numlines = (nib.load(str(topup_fname))).header['dim'][4]
    topdn_numlines = (nib.load(str(topdn_fname))).header['dim'][4]

    with open(str(pick['dwi_path'] / 'acq_params.txt'), 'w') as ap:
        for x in range(topup_numlines):
            ap.write('0 1 0 ' + topup_dwellt + '\n')
        for x in range(topdn_numlines):
            ap.write('0 -1 0 ' + topdn_dwellt + '\n')


    # topup distortion correction
    if pick['run_topup'] or pick['overwrite']:
        print('starting time for topup is {:%Y %m %d %H:%M}'.format(datetime.datetime.now()))
        topup_dn_data_concat = np.concatenate((topup_data, topdn_data), axis=3)
        topup_dn_data_concat_mf = medianf(topup_dn_data_concat, size=3)
        pick['topup_dn_fname'] = pick['dwi_path'] / '{topup_fname}_topdn_concat_mf.nii.gz'.format(**pick)
        pick['topup_out'] = pick['dwi_path'] / '{topup_fname}_topdn_concat_mf'.format(**pick)
        savenii(topup_dn_data_concat_mf, orig_topup_affine, str(pick['topup_dn_fname']))
        prov.log(str(pick['topup_dn_fname']), 'concatenated topup-dn S0 vols', [str(topup_fname), str(topdn_fname)])

        with WorkingContext(str(pick['dwi_path'])):
            with open('index.txt', 'w') as f:
                f.write('1 ' * len(gtab.bvals))
            if not skip_tup_eddy_cmds: # or not Path('{topup_out}_unwarped_mean.nii.gz'.format(**pick)).is_file():
                result += run_subprocess([topup_cmd.format(**pick)])
                result += run_subprocess([mean_b0_cmd.format(**pick)])
                prov.log('{topup_out}_unwarped_mean.nii.gz'.format(**pick), 'median filtered mean of topup-dn S0 vols', [str(topup_fname), str(topdn_fname)])
            print('end time for topup is {:%Y %m %d %H:%M}'.format(datetime.datetime.now()))


    # eddy current correction
    pick['ec_dwi_fname'] = pick['eddy_path'] / '{dwi_fname}_topdn_unwarped_ec'.format(**pick)
    pick['dwi_bvecs_ec_rot_fname'] = '{ec_dwi_fname}.eddy_rotated_bvecs'.format(**pick)
    if not skip_tup_eddy_cmds and (pick['eddy_corr'] or pick['overwrite']):
        with WorkingContext(pick['eddy_path']):
            print('starting time for eddy is {:%Y %m %d %H:%M}'.format(datetime.datetime.now()))
            b0_brain_fname, b0_brain_mask_fname, b0_brain_cropped_fname = extract_brain('{topup_out}_unwarped_mean.nii.gz'.format(**pick), mode='T2', dwi=True, f_factor=pick['dwi_bet_ffac'], robust=True)
            pick['b0_brain_mask_fname'] = b0_brain_mask_fname
            nii2nrrd(pick['b0_brain_mask_fname'], replacesuffix(pick['b0_brain_mask_fname'], '.nhdr'), ismask=True)
            pick['b0_brain_mask_fname_nrrd'] = replacesuffix(pick['b0_brain_mask_fname'], '.nhdr')
            pick['ec_dwi_clamp_fname'] = '{ec_dwi_fname}{mf_str}_clamp1.nii.gz'.format(**pick)
            pick['dwi_nrrd_fname'] = replacesuffix(pick['ec_dwi_clamp_fname'], '.nhdr')
            # bvals, ec_bvecs = read_bvals_bvecs(str(pick['dwi_bvals_fname']), pick['dwi_bvecs_ec_rot_fname'])
            # ec_gtab = gradient_table(bvals, ec_bvecs)
            # run eddy correction
            result += run_subprocess([eddy_cmd.format(**pick)])
            # clamp, filter, and make nrrd
            bvals, ec_bvecs = read_bvals_bvecs(str(pick['dwi_bvals_fname']), pick['dwi_bvecs_ec_rot_fname'])
            ec_gtab = gradient_table(bvals, ec_bvecs)
            ec_data = nib.load('{ec_dwi_fname}.nii.gz'.format(**pick)).get_data().astype(np.float64)
            ec_data_affine = nib.load('{ec_dwi_fname}.nii.gz'.format(**pick)).affine
            if pick['mf_str'] != '':
                S0 = ec_data[:, :, :, gtab.b0s_mask]
                S0_mf = medianf(S0, size=3)
                ec_data[:, :, :, gtab.b0s_mask] = S0_mf
            ec_data[ec_data <= 0] = 0
            savenii(ec_data, ec_data_affine, pick['ec_dwi_clamp_fname'])
            prov.log(pick['ec_dwi_clamp_fname'], 'median filtered mean of topup-dn S0 vols clamped','{ec_dwi_fname}.nii.gz'.format(**pick))
            nii2nrrd(pick['ec_dwi_clamp_fname'], str(pick['dwi_nrrd_fname']), bvalsf=pick['dwi_bvals_fname'], bvecsf=pick['dwi_bvecs_ec_rot_fname'])
            prov.log(str(replacesuffix(pick['ec_dwi_clamp_fname'], '.nhdr')), 'nrrd converted median filtered mean of topup-dn S0 vols', pick['ec_dwi_clamp_fname'])
            print('ending time for eddy is {:%Y %m %d %H:%M}'.format(datetime.datetime.now()))


    # do fsl fits and dipy fits
    if skip_tup_eddy_cmds:
        pick['b0_brain_mask_fname'] = Path('{topup_out}_unwarped_mean_brain_mask.nii.gz'.format(**pick))
        pick['b0_brain_mask_fname_nrrd'] = replacesuffix(pick['b0_brain_mask_fname'], '.nhdr')
        pick['ec_dwi_clamp_fname'] = '{ec_dwi_fname}{mf_str}_clamp1.nii.gz'.format(**pick)
        pick['dwi_nrrd_fname'] = replacesuffix(pick['ec_dwi_clamp_fname'], '.nhdr')
        bvals, ec_bvecs = read_bvals_bvecs(str(pick['dwi_bvals_fname']), pick['dwi_bvecs_ec_rot_fname'])
        ec_gtab = gradient_table(bvals, ec_bvecs)
    if not pick['fits_path'].is_dir():
        pick['fits_path'].mkdir(parents=True)
    pick['fsl_fits_out'] = pick['fits_path'] / '{subj}_{session}_dwi_unwarped_ec_fslfit'.format(**pick)
    pick['dipy_fits_out'] = pick['fits_path'] / '{subj}_{session}_dwi_unwarped_ec_dipyfit'.format(**pick)
    pick['dipy_dki_fits_out'] = pick['fits_path'] / '{subj}_{session}_dwi_unwarped_ec_dki_dipyfit'.format(**pick)
    with WorkingContext(pick['fits_path']):
        print('starting time for fiting is {:%Y %m %d %H:%M}'.format(datetime.datetime.now()))
        # do fsl dtifit cmds incl median filter etc
        result += tuple([run_subprocess(c % pick) for c in fsl_fit_cmds])
        nii2nrrd('{fsl_fits_out}_tensor{mf_str}.nii.gz'.format(**pick), '{fsl_fits_out}_tensor{mf_str}.nhdr'.format(**pick), istensor=True)
        # do dipy fits
        tenmodel = dti.TensorModel(ec_gtab, fit_method='WLS')
        data = nib.load(pick['ec_dwi_clamp_fname']).get_data().astype(np.float64)
        affine = nib.load(pick['ec_dwi_clamp_fname']).affine
        mask = nib.load(str(pick['b0_brain_mask_fname'])).get_data().astype(np.int64)
        fit = tenmodel.fit(data, mask)
        # filter and save all dipy files
        fit_quad_form = fit.quadratic_form
        fit_quad_form_mf = np.zeros(fit_quad_form.shape)
        for r, c in zip(_all_rows, _all_cols):
            fit_quad_form_mf[..., r, c] = medianf(fit_quad_form[..., r, c], size=1, mode='constant', cval=0)
        tensor_ut = fit_quad_form[..., _ut_rows, _ut_cols]
        tensor_ut_mf = fit_quad_form_mf[..., _ut_rows, _ut_cols]
        savenii(tensor_ut, affine, '{dipy_fits_out}_tensor.nii'.format(**pick))
        savenii(tensor_ut_mf, affine, '{dipy_fits_out}_tensor{mf_str}.nii'.format(**pick))
        nii2nrrd('{dipy_fits_out}_tensor{mf_str}.nii'.format(**pick), '{dipy_fits_out}_tensor{mf_str}.nhdr'.format(**pick), istensor=True)
        savenii(fit.fa, affine, '{dipy_fits_out}_FA.nii'.format(**pick), minmax=(0, 1))
        savenii(fit.md, affine, '{dipy_fits_out}_MD.nii'.format(**pick))
        savenii(fit.rd, affine, '{dipy_fits_out}_RD.nii'.format(**pick))
        savenii(fit.ad, affine, '{dipy_fits_out}_AD.nii'.format(**pick))
        savenii(fit.mode, affine, '{dipy_fits_out}_MO.nii'.format(**pick), minmax=(-1, 1))
        # calculate eigenvalues for median filtered tensor and then FA, MD, RD etc and save
        evals, evecs = np.linalg.eigh(fit_quad_form_mf)
        evals = np.rollaxis(evals, axis=-1)  # order evals
        all_zero = (evals == 0).all(axis=0)  # remove NaNs
        ev1, ev2, ev3 = evals  # need to test if ev1 > ev2 > ev3
        fa_mf = np.sqrt(0.5 * ((ev1 - ev2) ** 2 +
                               (ev2 - ev3) ** 2 +
                               (ev3 - ev1) ** 2) /
                        ((evals * evals).sum(0) + all_zero))
        savenii(fa_mf, affine, '{dipy_fits_out}_mf_FA.nii'.format(**pick), minmax=(0, 1))
        savenii(evals.mean(0), affine, '{dipy_fits_out}_mf_MD.nii'.format(**pick))
        savenii(ev1, affine, '{dipy_fits_out}_mf_AD.nii'.format(**pick))
        savenii(evals[1:].mean(0), affine, '{dipy_fits_out}_mf_RD.nii'.format(**pick))
        savenii(mode(fit_quad_form_mf), affine, '{dipy_fits_out}_mf_MO.nii'.format(**pick), minmax=(-1, 1))
        # make AFQ dt6 file out of fsl
        mempkey = [k for k in acdc_conv.keys() if 'MEMP_' in k][0]
        t1_fname = fs/project/('{subj}/{session}/anat/'+acdc_conv[mempkey]['fname_template']).format(**merge_ftempl_dicts(
            dict1=acdc_conv[mempkey], dict2=pick, dict3={'scan_info': 'ti1200_rms'}))
        t1_fname = replacesuffix(t1_fname, '_brain.nii.gz')
        if not t1_fname.is_file() and Path(str(t1_fname).replace('_brain.nii.gz', '.nii')).is_file():
            t1_fname, t1_fname_mask, t1_fname_cropped = extract_brain(str(t1_fname).replace('_brain.nii.gz', '.nii'), robust=True)
        if t1_fname.is_file() and not skip_mat:
            fsl_S0_fname = '{subj}_{session}_dwi_unwarped_ec_fslfit_tensor_mf_S0.nii.gz'.format(**pick)
            fsl_dt6_fname = '{subj}_{session}_dwi_unwarped_ec_fslfit_tensor_mf_dt6.mat'.format(**pick)
            mcmd = 'matlab -nodesktop -nodisplay -nosplash -r "{0}"'
            cmd = "addpath('{path1}', genpath('{path2}')); dtiMakeDt6FromFsl('{S0}', '{t1}', '{outf}'); quit".format(
                **{'S0': fsl_S0_fname, 't1': str(t1_fname), 'outf': fsl_dt6_fname, 'path1': mmimproc_dir/'mmimproc/diffusion', 'path2': mmimproc_dir.parent/'vistasoft'})
            if which('matlab') == None:
                print('matlab not found or installed on this machine. please check. skipping dt6.mat ')
            else:
                print('start time for mat file is {:%Y %m %d %H:%M}'.format(datetime.datetime.now()))
                result += run_subprocess([mcmd.format(cmd)])
                print('ending time for mat file is {:%Y %m %d %H:%M}'.format(datetime.datetime.now()))


        # do denoise and dki
        sigma = estimate_sigma(data, N=4)
        den_data = non_local_means(data, sigma=np.average(sigma), mask=mask)
        dkimodel = dki.DiffusionKurtosisModel(ec_gtab)
        dkifit = dkimodel.fit(den_data, mask=mask)
        # save dki files with savenii
        savenii(dkifit.fa, affine, '{dipy_dki_fits_out}_FA.nii'.format(**pick), minmax=(0, 1))
        savenii(dkifit.md, affine, '{dipy_dki_fits_out}_MD.nii'.format(**pick))
        savenii(dkifit.rd, affine, '{dipy_dki_fits_out}_RD.nii'.format(**pick))
        savenii(dkifit.ad, affine, '{dipy_dki_fits_out}_AD.nii'.format(**pick))
        savenii(dkifit.mk(-3, 3), affine, '{dipy_dki_fits_out}_MK.nii'.format(**pick), minmax=(-3, 3))
        savenii(dkifit.rk(-3, 3), affine, '{dipy_dki_fits_out}_RK.nii'.format(**pick), minmax=(-3, 3))
        savenii(dkifit.ak(-3, 3), affine, '{dipy_dki_fits_out}_AK.nii'.format(**pick), minmax=(-3, 3))
        # save evals and evecs for AFQ...

        print('ending time for fitting is {:%Y %m %d %H:%M}'.format(datetime.datetime.now()))

    if pick['do_ukf']:
        if not pick['vtk_path'].is_dir():
            pick['vtk_path'].mkdir(parents=True)
        try:
            with WorkingContext(pick['eddy_path']):
                print('starting UKF tractography at {:%Y %m %d %H:%M}'.format(datetime.datetime.now()))
                result += ('starting UKF tractography at {:%Y %m %d %H:%M}'.format(datetime.datetime.now()),)
                result += run_subprocess([ukfcmds['UKF_whbr'] % pick])
                pick['ukf_fname'] = Path('%(ec_dwi_fname)s_mf_clamp1_UKF_whbr.vtk' % pick).name
                with WorkingContext(pick['vtk_path']):
                    result += run_subprocess(['ln -sf ../{eddy_corr_dir}/{ukf_fname} {ukf_fname}'.format(**pick)])
                print('finished UKF tractography at {:%Y %m %d %H:%M} starting NODDI 1 tensor'.format(datetime.datetime.now()))
                result += ('finished UKF tractography at {:%Y %m %d %H:%M} starting NODDI 1 tensor'.format(datetime.datetime.now()),)
                result += run_subprocess([ukfcmds['NODDI1'] % mergeddicts(pick, vars(opts))])
                pick['noddi1_fname'] = Path('%(ec_dwi_fname)s_mf_clamp1_whbr_1tensor_noddi.vtk' % pick).name
                with WorkingContext(pick['vtk_dir']):
                    result += run_subprocess(['ln -sf ../{eddy_corr_dir}/{noddi1_fname} {noddi1_fname}'.format(**pick)])
                print('finished NODDI 1 tensor tractography at {:%Y %m %d %H:%M} starting NODDI 2 tensor'.format(datetime.datetime.now()))
                result += ('finished NODDI 1 tensor tractography at {:%Y %m %d %H:%M} starting NODDI 2 tensor'.format(datetime.datetime.now()),)
                result += run_subprocess([ukfcmds['NODDI2'] % pick])
                pick['noddi2_fname'] = Path('%(ec_dwi_fname)s_mf_clamp1_whbr_2tensor_noddi.vtk' % pick).name
                with WorkingContext(pick['vtk_dir']):
                    result += run_subprocess(['ln -sf ../{eddy_corr_dir}/{noddi2_fname} {noddi2_fname}'.format(**pick)])
                print('finished NODDI 2 tensor tractography at {:%Y %m %d %H:%M}'.format(datetime.datetime.now()))
                result += ('finished NODDI 2 tensor tractography at {:%Y %m %d %H:%M}'.format(datetime.datetime.now()),)
        except:
            print('ukf failed to run with {slicer}'.format(**{'slicer': slicer_path}))

    # bedpost input files and execute (hopefully) on gpu
    if pick['run_bedpost'] or pick['overwrite']:
        if not pick['bedpost_path'].is_dir():
            pick['bedpost_path'].mkdir(parents=True)
        with WorkingContext(pick['bedpost_path']):
            print('starting time for bedpost is {:%Y %m %d %H:%M}'.format(datetime.datetime.now()))
            shutil.copy(pick['ec_dwi_clamp_fname'], str(pick['bedpost_path']))
            os.rename(Path(pick['ec_dwi_clamp_fname']).name, str(pick['bedpost_path']/'data.nii.gz'))
            shutil.copy(pick['dwi_bvecs_ec_rot_fname'], str(pick['bedpost_path']))
            os.rename(Path(pick['dwi_bvecs_ec_rot_fname']).name, str(pick['bedpost_path']/'bvecs'))
            shutil.copy(str(pick['dwi_bvals_fname']), str(pick['bedpost_path']))
            os.rename(Path(pick['dwi_bvals_fname']).name, str(pick['bedpost_path']/'bvals'))
            shutil.copy(str(pick['b0_brain_mask_fname']), str(pick['bedpost_path']))
            os.rename(pick['b0_brain_mask_fname'].name, str(pick['bedpost_path']/'nodif_brain_mask.nii.gz'))
            # run bedpost, probtracks, network, UKF, NODDI, and DKI here
            with WorkingContext(pick['dwi_path']):
                if (pick['dwi_path'] / 'bedpost.bedpostX').is_dir() and pick['overwrite']:
                    bumptodefunct(pick['dwi_path'] / 'bedpost.bedpostX')
                if test4working_gpu():
                    os.environ['FSLPARALLEL'] = ''
                    result += run_subprocess(['bedpostx_gpu bedpost -n 3 --model=2'])
                    os.environ['FSLPARALLEL'] = 'condor'
                    # what cleanup is required?
                else:
                    result += run_subprocess(['bedpostx bedpost -n 3 --model=2'])

    print('finished dwi preproc for {project} subject {subj} session {session}'.format(**pick))
    print('ending time for this subjects pipeline is {:%Y %m %d %H:%M}'.format(datetime.datetime.now()))
    print('total elapsed time is '+str(datetime.timedelta(seconds=(time.time() - start_time))))
    result += ('ending time for this subjects pipeline is {:%Y %m %d %H:%M}'.format(datetime.datetime.now()),)
    result += ('total elapsed time is '+str(datetime.timedelta(seconds=(time.time() - start_time))),)
    with open(str(pick['dwi_path'] / 'dwi_preproc_log{:%Y%m%d%H%M}.json'.format(datetime.datetime.now())), mode='a') as logr:
        json.dump(result, logr, indent=2)



####################### end here for now
'''

    # use ants to warp mori atlas into subj space
    if not test4file(regpath/replacesuffix(moriMNIatlas.name, '_reg2dwi.nii.gz')) or (test4file(regpath/replacesuffix(moriMNIatlas.name, '_reg2dwi.nii.gz')) & overwrite):
        with WorkingContext(regpath):
            MNI2b0_brain_antscmd = [str(antsRegistrationSyN), '-d 3 -m', str(MNI1mm_T2_brain), '-f',str(b0_brain_fname), '-o',
                                    str(regpath / replacesuffix(MNI1mm_T2_brain, '_reg2dwi_').name),'-n 30 -t s -p f -j 1 -s 10 -r 1']
            result += run_subprocess([' '.join(MNI2b0_brain_antscmd)])
            warpfiles = [regpath/replacesuffix(moriMNIatlas, '_reg2dwi_1Warp.nii.gz'),]
            affines = [regpath/replacesuffix(moriMNIatlas, '_reg2dwi_0GenericAffine.mat'),]
            subj2templ_applywarp(str(moriMNIatlas), str(b0_brain_fname), str(regpath/replacesuffix(moriMNIatlas.name, '_reg2dwi.nii.gz')), warpfiles=warpfiles, regpath, affine_xform=affines)
            subj2templ_applywarp(str(MNI1mm_T1_brain), str(b0_brain_fname), str(regpath/replacesuffix(MNI1mm_T1_brain.name, '_reg2dwi.nii.gz')), warpfiles=warpfiles, regpath, affine_xform=affines)




    cmdvars = {'fdwinrrd': str(ec_dwi_name)+mf_str+'_clamp1.nhdr',
               'mask_fnamenrrd': str(dwipath/str(topup + '_topdn_concat_mf_unwarped_mean_brain_mask.nii.gz')),
               'dwif': str(fits_dir/dwif)}




warp MNI_T1 to dwi for mricros :done
loop over mori to gen seed bin mask and dilate and get com coord and put subject.node 
probtracts cmd:
probtrackx2 --network -x listseeds.txt  -l --onewaycondition --omatrix1 -c 0.2 -S 1000 --steplength=0.5 -P 1000 --fibthresh=0.01 --distthresh=0.0 --sampvox=0.0 --forcedir --opd -s bedpost.bedpostX/merged -m bedpost.bedpostX/nodif_brain_mask  --dir=probtrackoutput


subject.node is row by row x y z center of mass coordinate for each seed plus 3 3 3 (space separated
150 130 48 3 3 3\n # for seed001.nii.gz
matrix2 = for loop by row matrix / waytotal to normalise and rename to .edge
this is the input for mricros ????? what????

'''
