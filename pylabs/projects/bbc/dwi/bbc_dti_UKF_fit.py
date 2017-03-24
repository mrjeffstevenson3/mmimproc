import os, inspect, itertools, platform
from pathlib import *
import sh
import numpy as np
import nibabel as nib
import pylabs
from sh import Command
fslmaths = Command('fslmaths')
from dipy.io import read_bvals_bvecs
from dipy.core.gradients import gradient_table
import dipy.reconst.dti as dti
import dipy.denoise.noise_estimate as ne
from dipy.reconst.dti import mode
from scipy.ndimage.filters import median_filter as medianf
#from pylabs.diffusion.dti_fit import DTIFitCmds
from pylabs.projects.bbc.pairing import dwipairing, dwi_fnames
from pylabs.utils.paths import getnetworkdataroot
from pylabs.utils import run_subprocess, WorkingContext
from pylabs.io.images import savenii
from pylabs.conversion.nifti2nrrd import nii2nrrd
from pylabs.projects.bbc.dwi.bbc_dti_fit import MNI_atlases
from pylabs.utils.provenance import ProvenanceWrapper
provenance = ProvenanceWrapper()
fs = Path(getnetworkdataroot())
pylabs_basepath = Path(*Path(inspect.getabsfile(pylabs)).parts[:-1])
pylabs_atlasdir = Path(*Path(inspect.getabsfile(pylabs)).parts[:-2]) / 'data' / 'atlases'
if platform.system() == 'Darwin':
    slicer_path = Path('/Applications/Slicer_dev4p7_2-21-2017.app/Contents/MacOS/Slicer --launch ')
elif platform.system() == 'Linux':
    slicer_path = Path(*Path(inspect.getabsfile(pylabs)).parts[:-3]) / 'Slicer-4.7.0-2017-02-01-linux-amd64' / 'Slicer --launch '
project = 'bbc'
templdir = fs / project / 'reg' / 'ants_vbm_pairedLH_in_template_space'
vbm_statsdir = templdir / 'stats' / 'exchblks'
#directory where eddy current corrected data is stored (from eddy.py)
ec_meth = 'cuda_repol_std2_S0mf3_v5'
JHU_thr = 5
filterS0_string = ''
filterS0 = True
if filterS0:
    filterS0_string = '_withmf3S0'
override_mask = {'sub-bbc101_ses-2_dti_15dir_b1000_1_withmf3S0_ec_thr1': fs / project / 'sub-bbc101/ses-2/dwi/sub-bbc101_ses-2_dti_15dir_b1000_1_S0_brain_mask_jsedits.nii'}
#fit methods to loop over
fitmeths = ['UKF']
fitmeth = fitmeths[0]

UKF_atlases = {'mori_LeftPostIntCap-35': {'atlas_fname': 'mori_LeftPostIntCap-35.nii', 'roi_list': [35], 'Sl_cmd': 'TractographyLabelMapSeeding -m 2000 -l 2 -x -v 0.1 -a '},
                'mori_RightPostIntCap-123': {'atlas_fname': 'mori_RightPostIntCap-123.nii', 'roi_list': [123], 'Sl_cmd': 'TractographyLabelMapSeeding -m 2000 -l 2 -x -v 0.1 -a '},
                'mori_CC': {'atlas_fname': 'mori_bilatCC-52to54-140to142.nii', 'roi_list': [52, 53, 54, 140, 141, 142], 'Sl_cmd': 'TractographyLabelMapSeeding -m 2000 -l 2 -x -v 0.1 -a '},
                'mori_Left_IFOF-45-47': {'atlas_fname': 'mori_Left_IFOF-45-47.nii', 'roi_list': [45,47,36], 'Sl_cmd': 'TractographyLabelMapSeeding -m 2000 -l 2 -x -v 0.1 -a '},
                'mori_Right_IFOF-133-135': {'atlas_fname': 'mori_Right_IFOF-133-135.nii', 'roi_list': [133, 135, 124],  'Sl_cmd': 'TractographyLabelMapSeeding -m 2000 -l 2 -x -v 0.1 -a '},
                'mori_Left_SLF-43':  {'atlas_fname': 'mori_Left_SLF-43.nii', 'roi_list': [43], 'Sl_cmd': 'TractographyLabelMapSeeding -m 2000 -l 2 -x -v 0.1 -a '},
                'mori_Right_SLF-131': {'atlas_fname': 'mori_Right_SLF-131.nii', 'roi_list': [131], 'Sl_cmd': 'TractographyLabelMapSeeding -m 2000 -l 2 -x -v 0.1 -a '},

                'JHU_tracts_Left_ATR-1': {'atlas_fname': 'JHU_tracts_thr%(JHU_thr)s_Left_ATR-1.nii', 'roi_list': 1, 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'JHU_tracts_Right_ATR-2': {'atlas_fname': 'JHU_tracts_thr%(JHU_thr)s_Right_ATR-2.nii', 'roi_list': 2, 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'JHU_tracts_Left_CSP-3': {'atlas_fname': 'JHU_tracts_thr%(JHU_thr)s_Left_CSP-3.nii', 'roi_list': 3, 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'JHU_tracts_Right_CSP-4': {'atlas_fname': 'JHU_tracts_thr%(JHU_thr)s_Right_CSP-4.nii', 'roi_list': 4, 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'JHU_tracts_Left_Cing-5': {'atlas_fname': 'JHU_tracts_thr%(JHU_thr)s_Left_Cing-5.nii', 'roi_list': 5, 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'JHU_tracts_Right_Cing-6': {'atlas_fname': 'JHU_tracts_thr%(JHU_thr)s_Right_Cing-6.nii', 'roi_list': 6, 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'JHU_tracts_Forceps_Major-9': {'atlas_fname': 'JHU_tracts_thr%(JHU_thr)s_Forceps_Major-9.nii', 'roi_list': 9, 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'JHU_tracts_Forceps_Minor-10': {'atlas_fname': 'JHU_tracts_thr%(JHU_thr)s_Forceps_Minor-10.nii', 'roi_list': 10, 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'JHU_tracts_Left_IFOF-11': {'atlas_fname': 'JHU_tracts_thr%(JHU_thr)s_Left_IFOF-11.nii', 'roi_list': 11, 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'JHU_tracts_Right_IFOF-12':  {'atlas_fname': 'JHU_tracts_thr%(JHU_thr)s_Right_IFOF-12.nii', 'roi_list': 12, 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'JHU_tracts_Left_ILF-13': {'atlas_fname': 'JHU_tracts_thr%(JHU_thr)s_Left_ILF-13.nii', 'roi_list': 13, 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'JHU_tracts_Right_ILF-14': {'atlas_fname': 'JHU_tracts_thr%(JHU_thr)s_Right_ILF-14.nii', 'roi_list': 14, 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'JHU_tracts_Left_SLF-15': {'atlas_fname': 'JHU_tracts_thr%(JHU_thr)s_Left_SLF-15.nii', 'roi_list': 15, 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'JHU_tracts_Right_SLF-16': {'atlas_fname': 'JHU_tracts_thr%(JHU_thr)s_Right_SLF-16.nii', 'roi_list': 16, 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'JHU_tracts_Left_Unc-17': {'atlas_fname': 'JHU_tracts_thr%(JHU_thr)s_Left_Unc-17.nii', 'roi_list': 17, 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'JHU_tracts_Right_Unc-18': {'atlas_fname': 'JHU_tracts_thr%(JHU_thr)s_Right_Unc-18.nii', 'roi_list': 18, 'Sl_cmd': 'ModelMaker -l 1 -n '},

                'stats_vbm_WM_s2'  : {'atlas_fname': 'all_WM_mod_s2_n10000_exchbl_tfce_corrp_tstat2.nii.gz', 'roi_list': 1, 'Sl_cmd': 'UKFTractography --dwiFile %(fdwinrrd)s --seedsFile %(seed_fnamenrrd)s --labels 1 --maskFile %(mask_fnamenrrd)s --tracts %(dwif)s_UKF_whbr.vtk '
                                     '--seedsPerVoxel 1 --seedFALimit 0.18 --minFA 0.15 --minGA 0.2 --numThreads -1 --numTensor 2 --stepLength 0.3 --Qm 0 --recordLength 0.9 --maxHalfFiberLength 250 --recordNMSE --freeWater '
                                     '--recordFA --recordTrace --recordFreeWater --recordTensors --Ql 0 --Qw 0 --Qkappa 0.01 --Qvic 0.004 --Rs 0 --sigmaSignal 0 --maxBranchingAngle 0 --minBranchingAngle 0'},
                }
#main comand template dictionary for each fit method with %variables to be substituted later by cmdvars
cmds_d = {'UKF':  {'slicerpart1': [str(slicer_path) + 'UKFTractography --dwiFile %(fdwinrrd)s --seedsFile %(short_mask_fnamenrrd)s --labels 1 --maskFile %(mask_fnamenrrd)s --tracts %(dwif)s_UKF_whbr.vtk '
                                     '--seedsPerVoxel 1 --seedFALimit 0.18 --minFA 0.15 --minGA 0.2 --numThreads -1 --numTensor 2 --stepLength 0.3 --Qm 0 --recordLength 0.9 --maxHalfFiberLength 250 --recordNMSE --freeWater '
                                     '--recordFA --recordTrace --recordFreeWater --recordTensors --Ql 0 --Qw 0 --Qkappa 0.01 --Qvic 0.004 --Rs 0 --sigmaSignal 0 --maxBranchingAngle 0 --minBranchingAngle 0']
                    }
        }
#primary loop over subjects dwi
for dwif in dwi_fnames:
    execwdir = fs / project / dwif.split('_')[0] / dwif.split('_')[1] / 'dwi' / ec_meth / fitmeth
    fdwi = fs / project / dwif.split('_')[0] / dwif.split('_')[1] / 'dwi' / ec_meth / str(dwif+'.nhdr')
    mori_fname = fs / project / dwif.split('_')[0] / dwif.split('_')[1] / 'dwi' / str('_'.join(dwif.split('_')[:5])+'_mori.nii')
    mori_fname_nrrd =  execwdir / str(dwif+'_mori.nhdr')
    nii2nrrd(str(mori_fname), str(mori_fname_nrrd), ismask=True)
    if dwif in override_mask:
        mask_fname = str(override_mask[dwif])
        mask_fname_nrrd = execwdir / str(dwif.replace('.nii', '.nhdr'))
        nii2nrrd(str(mask_fname), str(mask_fname_nrrd), ismask=True)
    else:
        mask_fname = Path(*execwdir.parts[:-2]) / str(dwif.replace('_ec_thr1', '_S0_brain_mask.nii'))
        mask_fname_nrrd = execwdir / str(dwif.replace('_ec_thr1', '_S0_brain_mask.nhdr'))
        nii2nrrd(str(mask_fname), str(mask_fname_nrrd), ismask=True)
    # sets up variables to combine with cmds_d
    cmdvars = {'fdwi': str(fdwi), 'mask_fname': str(mask_fname_nrrd),
               'mask_fnamenrrd': str(mask_fname_nrrd),
               'label_mask_fnamenrrd': str(mori_fname_nrrd)}
    for labels in UKF_atlases:
        if 'JHU_' in labels:
            JHU_fname = fs / project / dwif.split('_')[0] / dwif.split('_')[1] / 'dwi' / str(UKF_atlases[labels]['atlas_fname'] % {'JHU_thr': JHU_thr})
            JHU_fname_nrrd = execwdir / str(UKF_atlases[labels]['atlas_fname'] % {'JHU_thr': JHU_thr}).replace('.nii', '.nhdr'))
            nii2nrrd(str(JHU_fname), str(JHU_fname_nrrd), ismask=True)
        if 'stats_' in labels:
            stats_fname = vbm_statsdir / str(UKF_atlases[labels]['atlas_fname'])
            sh
