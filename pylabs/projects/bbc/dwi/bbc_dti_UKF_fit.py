# this script takes eddy corrected dti data and using mori and JHU tract atlases generates UKF vtk files.
import os, inspect, itertools, platform
from pathlib import *
import sh
import numpy as np
import nibabel as nib
import pylabs
from sh import Command
fslmaths = Command('fslmaths')
from pylabs.projects.bbc.pairing import dwipairing, dwi_fnames
from pylabs.utils.paths import getnetworkdataroot
from pylabs.utils import run_subprocess, WorkingContext
from pylabs.io.images import savenii
from pylabs.conversion.nifti2nrrd import nii2nrrd, array2nrrd
from pylabs.correlation.atlas import make_mask_fm_stats, make_mask_fm_atlas_parts
from pylabs.alignment.ants_reg import subj2templ_applywarp
from pylabs.utils.provenance import ProvenanceWrapper
provenance = ProvenanceWrapper()
fs = Path(getnetworkdataroot())
pylabs_basepath = Path(*Path(inspect.getabsfile(pylabs)).parts[:-1])
pylabs_atlasdir = Path(*Path(inspect.getabsfile(pylabs)).parts[:-2]) / 'data' / 'atlases'
if platform.system() == 'Darwin':
    slicer_path = Path('/Applications/Slicer_dev4p7_2-21-2017.app/Contents/MacOS/Slicer --launch ')
elif platform.system() == 'Linux':
    slicer_path = Path(*Path(inspect.getabsfile(pylabs)).parts[:-3]) / 'Slicer-4.7.0-2017-03-12-linux-amd64' / 'Slicer --launch '
if not slicer_path.parent.is_dir():
    raise ValueError('Slicer path not found for '+str(slicer_path))
project = 'bbc'
templdir = fs / project / 'reg' / 'ants_vbm_pairedLH_in_template_space'
vbm_statsdir = templdir / 'stats' / 'exchblks'
JHU_atlas = pylabs_atlasdir / 'JHU-ICBM-tracts-prob-1mm.nii.gz'
mori_atlas = pylabs_atlasdir / 'JHU_MNI_SS_WMPM_Type_I_matched.nii.gz'
MNI2templ_invwarp = templdir / 'bbc_pairedLH_template_reg2MNI_1InverseWarp.nii.gz'
MNI2templ_aff = templdir / 'bbc_pairedLH_template_reg2MNI_0GenericAffine.mat'
#directory where eddy current corrected data is stored (from eddy.py)
ec_meth = 'cuda_repol_std2_S0mf3_v5'
JHU_thr = 5  # remove low probability tract regions
stats_thr = 0.95
filterS0_string = '_withmf3S0'
regext = '_withmf3S0_S0_brain_j1_s10_r1_reg2dwiT2template_'
override_mask = {'sub-bbc101_ses-2_dti_15dir_b1000_1_withmf3S0_ec_thr1': fs / project / 'sub-bbc101/ses-2/dwi/sub-bbc101_ses-2_dti_15dir_b1000_1_S0_brain_mask_jsedits.nii'}
#fit methods to loop over
fitmeths = ['UKF']
fitmeth = fitmeths[0]

UKF_atlases = {'mori': {'atlas_fname': mori_atlas, 'ROIs': {
                'mori_LeftPostIntCap-35': {'roi_fname': 'mori_LeftPostIntCap-35.nhdr', 'roi_list': '35', 'Sl_cmd': 'TractographyLabelMapSeeding -m 2000 -l 2 -x -v 0.1 -a '},
                'mori_RightPostIntCap-123': {'roi_fname': 'mori_RightPostIntCap-123.nhdr', 'roi_list': '123', 'Sl_cmd': 'TractographyLabelMapSeeding -m 2000 -l 2 -x -v 0.1 -a '},
                'mori_CC': {'roi_fname': 'mori_bilatCC-52to54-140to142.nhdr', 'roi_list': '52,53,54,140,141,142', 'Sl_cmd': 'TractographyLabelMapSeeding -m 2000 -l 2 -x -v 0.1 -a '},
                'mori_Left_IFOF-45-47': {'roi_fname': 'mori_Left_IFOF-45-47.nhdr', 'roi_list': '45,47,36', 'Sl_cmd': 'TractographyLabelMapSeeding -m 2000 -l 2 -x -v 0.1 -a '},
                'mori_Right_IFOF-133-135': {'roi_fname': 'mori_Right_IFOF-133-135.nhdr', 'roi_list': '133,135,124',  'Sl_cmd': 'TractographyLabelMapSeeding -m 2000 -l 2 -x -v 0.1 -a '},
                'mori_Left_SLF-43-81-83':  {'roi_fname': 'mori_Left_SLF-43.nhdr', 'roi_list': '43,81,83', 'Sl_cmd': 'TractographyLabelMapSeeding -m 2000 -l 2 -x -v 0.1 -a '},
                'mori_Right_SLF-131-169-171': {'roi_fname': 'mori_Right_SLF-131.nhdr', 'roi_list': '131,169,171', 'Sl_cmd': 'TractographyLabelMapSeeding -m 2000 -l 2 -x -v 0.1 -a '},},},

                'JHU':{ 'atlas_fname': JHU_atlas, 'ROIs': {
                'JHU_tracts_Left_ATR-1': {'atlas_fname': 'JHU_tracts_thr%(JHU_thr)s_Left_ATR-1.nhdr', 'roi_list': 1, 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'JHU_tracts_Right_ATR-2': {'atlas_fname': 'JHU_tracts_thr%(JHU_thr)s_Right_ATR-2.nhdr', 'roi_list': 2, 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'JHU_tracts_Left_CSP-3': {'atlas_fname': 'JHU_tracts_thr%(JHU_thr)s_Left_CSP-3.nhdr', 'roi_list': 3, 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'JHU_tracts_Right_CSP-4': {'atlas_fname': 'JHU_tracts_thr%(JHU_thr)s_Right_CSP-4.nhdr', 'roi_list': 4, 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'JHU_tracts_Left_Cing-5': {'atlas_fname': 'JHU_tracts_thr%(JHU_thr)s_Left_Cing-5.nhdr', 'roi_list': 5, 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'JHU_tracts_Right_Cing-6': {'atlas_fname': 'JHU_tracts_thr%(JHU_thr)s_Right_Cing-6.nhdr', 'roi_list': 6, 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'JHU_tracts_Forceps_Major-9': {'atlas_fname': 'JHU_tracts_thr%(JHU_thr)s_Forceps_Major-9.nhdr', 'roi_list': 9, 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'JHU_tracts_Forceps_Minor-10': {'atlas_fname': 'JHU_tracts_thr%(JHU_thr)s_Forceps_Minor-10.nhdr', 'roi_list': 10, 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'JHU_tracts_Left_IFOF-11': {'atlas_fname': 'JHU_tracts_thr%(JHU_thr)s_Left_IFOF-11.nhdr', 'roi_list': 11, 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'JHU_tracts_Right_IFOF-12':  {'atlas_fname': 'JHU_tracts_thr%(JHU_thr)s_Right_IFOF-12.nhdr', 'roi_list': 12, 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'JHU_tracts_Left_ILF-13': {'atlas_fname': 'JHU_tracts_thr%(JHU_thr)s_Left_ILF-13.nhdr', 'roi_list': 13, 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'JHU_tracts_Right_ILF-14': {'atlas_fname': 'JHU_tracts_thr%(JHU_thr)s_Right_ILF-14.nhdr', 'roi_list': 14, 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'JHU_tracts_Left_SLF-15': {'atlas_fname': 'JHU_tracts_thr%(JHU_thr)s_Left_SLF-15.nhdr', 'roi_list': 15, 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'JHU_tracts_Right_SLF-16': {'atlas_fname': 'JHU_tracts_thr%(JHU_thr)s_Right_SLF-16.nhdr', 'roi_list': 16, 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'JHU_tracts_Left_Unc-17': {'atlas_fname': 'JHU_tracts_thr%(JHU_thr)s_Left_Unc-17.nhdr', 'roi_list': 17, 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'JHU_tracts_Right_Unc-18': {'atlas_fname': 'JHU_tracts_thr%(JHU_thr)s_Right_Unc-18.nhdr', 'roi_list': 18, 'Sl_cmd': 'ModelMaker -l 1 -n '},},},

                'stats_VBM':{'atlas_fname': mori_atlas, 'ROIs': {
                'stats_vbm_WM_s2'  : {'atlas_fname': vbm_statsdir / 'all_WM_mod_s2_n10000_exchbl_tfce_corrp_tstat2.nii.gz', 'roi_list': 1, 'Sl_cmd': 'UKFTractography --dwiFile %(fdwinrrd)s --seedsFile %(seed_fnamenrrd)s --labels 1 --maskFile %(mask_fnamenrrd)s --tracts %(dwif)s_UKF_whbr.vtk '
                                     '--seedsPerVoxel 1 --seedFALimit 0.18 --minFA 0.15 --minGA 0.2 --numThreads -1 --numTensor 2 --stepLength 0.3 --Qm 0 --recordLength 0.9 --maxHalfFiberLength 250 --recordNMSE --freeWater '
                                     '--recordFA --recordTrace --recordFreeWater --recordTensors --Ql 0 --Qw 0 --Qkappa 0.01 --Qvic 0.004 --Rs 0 --sigmaSignal 0 --maxBranchingAngle 0 --minBranchingAngle 0'},},
                }
               }
#main comand template dictionary for each fit method with %variables to be substituted later by cmdvars
cmds_d = {'UKF':  {'slicerpart1': [str(slicer_path) + 'UKFTractography --dwiFile %(fdwi)s --seedsFile %(label_mask_fnamenrrd)s --labels %(label_num)s --maskFile %(mask_fnamenrrd)s --tracts %(dwif)s_%(roi)s_UKF.vtk '
                                     '--seedsPerVoxel 1 --seedFALimit 0.18 --minFA 0.15 --minGA 0.2 --numThreads -1 --numTensor 2 --stepLength 0.3 --Qm 0 --recordLength 0.9 --maxHalfFiberLength 250 --recordNMSE --freeWater '
                                     '--recordFA --recordTrace --recordFreeWater --recordTensors --Ql 0 --Qw 0 --Qkappa 0.01 --Qvic 0.004 --Rs 0 --sigmaSignal 0 --maxBranchingAngle 0 --minBranchingAngle 0']},
        }
#primary loop over subjects dwi
for dwif in dwi_fnames:
    # set working directory to execute
    execwdir = fs / project / dwif.split('_')[0] / dwif.split('_')[1] / 'dwi' / ec_meth / fitmeth
    if not execwdir.is_dir():
        execwdir.mkdir(parents=True)
    # set eddy corrected DTI nrrd file
    fdwi = fs / project / dwif.split('_')[0] / dwif.split('_')[1] / 'dwi' / ec_meth / str(dwif+'.nhdr')
    # set mori atlas targets in subject space
    mori_fname = fs / project / dwif.split('_')[0] / dwif.split('_')[1] / 'dwi' / str('_'.join(dwif.split('_')[:6])+'_mori.nii')
    mori_fname_nrrd =  execwdir / str(dwif+'_mori.nhdr')
    # apply warp to this subj mori atlas then convert to nrrd
    ref = Path(*execwdir.parts[:-2]) / str(dwif.replace('_ec_thr1', '_S0_brain.nii'))
    inv_warp1 = fs / project / 'reg' / 'ants_dwiS0_in_template_space' / str(dwif.replace('_withmf3s0_ec_thr1', regext + '1InverseWarp.nii.gz'))
    aff1 = fs / project / 'reg' / 'ants_dwiS0_in_template_space' / str(dwif.replace('_withmf3s0_ec_thr1', regext + '0GenericAffine.mat'))
    warpfiles = [str(MNI2templ_invwarp), str(inv_warp1)]
    affine_xform = [str(MNI2templ_aff), str(aff1)]
    subj2templ_applywarp(str(mori_atlas), str(ref), str(mori_fname), warpfiles, str(execwdir), affine_xform=affine_xform, inv=True)
    nii2nrrd(str(mori_fname), str(mori_fname_nrrd), ismask=True)
    # now set targets for JHU atlas
    JHU_fname = fs / project / dwif.split('_')[0] / dwif.split('_')[1] / 'dwi' / str('_'.join(dwif.split('_')[:6])+'_JHU_prob_tracts.nii')
    JHU_fname_nrrd = execwdir / str('_'.join(dwif.split('_')[:6])+'_JHU_prob_tracts.nii').replace('.nii', '.nhdr')
    subj2templ_applywarp(str(JHU_atlas), str(ref), str(JHU_fname), warpfiles, str(execwdir), affine_xform=affine_xform, dims=4, inv=True)
    # set whole brain mask
    if dwif in override_mask:
        mask_fname = str(override_mask[dwif])
        mask_fname_nrrd = execwdir / str(override_mask[dwif].name.replace('.nii', '.nhdr'))
        nii2nrrd(str(mask_fname), str(mask_fname_nrrd), ismask=True)
    else:
        mask_fname = Path(*execwdir.parts[:-2]) / str(dwif.replace('_ec_thr1', '_S0_brain_mask.nii'))
        mask_fname_nrrd = execwdir / str(dwif.replace('_ec_thr1', '_S0_brain_mask.nhdr'))
        nii2nrrd(str(mask_fname), str(mask_fname_nrrd), ismask=True)
    result = tuple()
    # start processing
    for atlas in UKF_atlases:
        if 'mori' in atlas:
            for roi in UKF_atlases[atlas]['ROIs']:
                cmdvars = {'dwif': dwif, 'roi': roi,
                            'fdwi': str(fdwi), 'mask_fname': str(mask_fname),
                           'mask_fnamenrrd': str(mask_fname_nrrd),
                           'label_mask_fnamenrrd': str(mori_fname_nrrd),
                           'label_num': UKF_atlases[atlas]['ROIs'][roi]['roi_list']}
                with WorkingContext(str(execwdir)):
                    result += run_subprocess(cmds_d['UKF']['slicerpart1'][0] % cmdvars)
        if 'JHU' in atlas:
            JHU_data = nib.load(str(JHU_fname)).get_data()
            affine = nib.load(str(JHU_fname)).affine
            JHU_data_thr_mask = np.zeros(JHU_data.shape)
            JHU_data_thr_mask[JHU_data > JHU_thr] = 1
            for roi in UKF_atlases[atlas]['ROIs']:
                JHU_nrrd_fname = execwdir / str(dwif.replace('ec_thr1', UKF_atlases[atlas]['ROIs'][roi]['atlas_fname'] % {'JHU_thr': JHU_thr}))
                array2nrrd(JHU_data_thr_mask[:,:,:,UKF_atlases[atlas]['ROIs'][roi]['roi_list'] - 1], affine, str(JHU_nrrd_fname), ismask=True)
                cmdvars = {'dwif': dwif, 'roi': roi,
                            'fdwi': str(fdwi), 'mask_fname': str(mask_fname),
                           'mask_fnamenrrd': str(mask_fname_nrrd),
                           'label_mask_fnamenrrd': str(JHU_nrrd_fname),
                           'label_num': 1}
                with WorkingContext(str(execwdir)):
                    result += run_subprocess(cmds_d['UKF']['slicerpart1'][0] % cmdvars)

        # if 'stats_' in atlas:
        #     stats_fname = vbm_statsdir / str(UKF_atlases[labels]['atlas_fname'])
        #     stats_mask = execwdir / str(UKF_atlases[labels]['atlas_fname']).replace('.nii.gz', '_thr'+str(stats_thr).replace('0.','')+'_bin.nii')
        #     stats_mask_nrrd = execwdir / str(UKF_atlases[labels]['atlas_fname']).replace('.nii.gz', '_thr'+str(stats_thr).replace('0.','')+'_bin.nhdr')
        #     make_mask_fm_stats(stats_fname, thresh=stats_thr, stats_mask)
        #     nii2nrrd(str(stats_mask), str(stats_mask_nrrd), ismask=True)
