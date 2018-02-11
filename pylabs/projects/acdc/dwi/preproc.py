# first set global root data directory
import pylabs
pylabs.datadir.target = 'jaba'
import os, cPickle
from pathlib import *
from collections import defaultdict
import nipype
from nipype.interfaces import fsl
import nibabel as nib
import numpy as np
from dipy.io import read_bvals_bvecs
from dipy.core.gradients import gradient_table
import shutil
import datetime
from cloud.serialization.cloudpickle import dumps
from scipy.ndimage.filters import median_filter as medianf
from pylabs.structural.brain_extraction import extract_brain
from pylabs.conversion.brain_convert import conv_subjs
from pylabs.conversion.nifti2nrrd import nii2nrrd
from pylabs.alignment.ants_reg import subj2templ_applywarp
from pylabs.correlation.atlas import mori_network_regions
from pylabs.io.images import savenii
from pylabs.utils import run_subprocess, WorkingContext, appendposix, replacesuffix
from pylabs.utils.paths import getnetworkdataroot, test4working_gpu, get_antsregsyn_cmd, MNI1mm_T2_brain, getslicercmd, \
        moriMNIatlas, MNI1mm_T1_brain
# project and subjects and files to run on
from pylabs.projects.acdc.file_names import project, SubjIdPicks, get_dwi_names
#set up provenance
from pylabs.utils.provenance import ProvenanceWrapper
prov = ProvenanceWrapper()
#setup paths and file names to process

fs = Path(getnetworkdataroot())

antsRegistrationSyN = get_antsregsyn_cmd()
slicer_path = getslicercmd()

# instantiate subject id list container
subjids_picks = SubjIdPicks()
# list of subject ids to operate on
picks = [
         {'subj': 'sub-acdc103', 'session': 'ses-1', 'run': '1',  # subject selection info
          'dwi_badvols': np.array([1, 3, 4, 5, 10, 53]), 'topup_badvols': np.array([]), 'topdn_badvols': np.array([]),  # remove bad vols identified in qc
          },
         ]

setattr(subjids_picks, 'subjids', picks)

#  define hostnames with working gpus for processing
flt = fsl.FLIRT(bins=640, interp='nearestneighbour', cost_func='mutualinfo', output_type='NIFTI_GZ')
if nipype.__version__ == '0.12.0':
    applyxfm = fsl.ApplyXfm(interp='nearestneighbour', output_type='NIFTI_GZ')
else:
    applyxfm = fsl.ApplyXFM(interp='nearestneighbour', output_type='NIFTI_GZ')

print(os.environ['FSLOUTPUTTYPE'])


topup_fnames, topdn_fnames, dwi_fnames = get_dwi_names(subjids_picks)

overwrite = True
convert = False
dti_qc = True
if dti_qc:
    qc_str = '_selected_vols' # set to blank string '' when not in use
else:
    qc_str = ''
run_topup = True
eddy_corr = True
eddy_corr_dir = 'eddy_cuda_repol_v1'   # output dir for eddy
fits_dir_name = 'fits_v1'    # dir for all fitting methods
mf_str = '_mf'    # set to blank string '' to disable
"""
i = 0
topup, topdn, dwif = topup_fnames[i], topdn_fnames[i], dwi_fnames[i]
dwipath = fs / project / picks[i]['subj'] / picks[i]['session'] / 'dwi'
orig_dwi_data = nib.load(str(dwipath / (dwi_fnames[i]+'.nii'))).get_data()
voli = range(orig_dwi_data.shape[3])
good_voli = list(set(voli) - set(picks[i]['dwi_badvols']))
good_dwi_data = orig_dwi_data[:,:,:,good_voli]
orig_bvecs = pd.read_csv(str(dwipath / (dwi_fnames[i]+'.bvecs')), header=None, delim_whitespace=True)
orig_bvals = pd.read_csv(str(dwipath / (dwi_fnames[i]+'.bvals')), header=None, delim_whitespace=True)
good_bvecs = orig_bvecs.iloc[:, good_voli]
good_bvals = orig_bvals.iloc[:, good_voli]
good_bvecs.to_csv(str(dwipath/ (dwi_fnames[i]+'_selected_vols.bvecs')), header=None, index=None, sep=' ', float_format='%.4f')
good_bvals.to_csv(str(dwipath/ (dwi_fnames[i]+'_selected_vols.bvals')), header=None, index=None, sep=' ', float_format='%.4f')
nib.save(nib.Nifti1Image(good_dwi_data,  nib.load(str(dwipath / (dwi_fnames[i]+'.nii'))).affine), str(dwipath / (dwi_fnames[i]+'_selected_vols.nii')))

orig_dwif_fname = dwipath / str(dwif + qc_str+'.nii')
dwi_bvals_fname = dwipath / str(dwif + qc_str+'.bvals')
dwi_bvecs_fname = dwipath / str(dwif + qc_str+'.bvecs')
# pick up at dwi_dwellt_fname below
"""

# other future stages to run
subT2 = False   #wip
b1corr = False
bet = False
prefilter = False
templating = False




'''
to do:
UKF command to modify 
/home/toddr/.config/NA-MIC/Extensions-26072/UKFTractography/lib/Slicer-4.7/cli-modules/UKFTractography 
--dwiFile /tmp/Slicer/CGGHB_vtkMRMLDiffusionWeightedVolumeNodeB.nhdr --seedsFile /tmp/Slicer/CGGHB_vtkMRMLLabelMapVolumeNodeB.nhdr --labels 1 --maskFile /tmp/Slicer/CGGHB_vtkMRMLLabelMapVolumeNodeB.nhdr --tracts /tmp/Slicer/CGGHB_vtkMRMLFiberBundleNodeB.vtp --seedsPerVoxel 1 --seedFALimit 0.18 --minFA 0.15 --minGA 0.1 --numThreads -1 --numTensor 2 --stepLength 0.3 --Qm 0 --recordLength 1.8 --maxHalfFiberLength 250 --recordNMSE --freeWater --recordFA --recordTrace --recordFreeWater --recordTensors --Ql 0 --Qw 0 --Qkappa 0.01 --Qvic 0.004 --Rs 0 --sigmaSignal 0 --maxBranchingAngle 0 --minBranchingAngle 0 
NODDI Command to modify
/home/toddr/.config/NA-MIC/Extensions-26072/UKFTractography/lib/Slicer-4.7/cli-modules/UKFTractography --dwiFile /tmp/Slicer/CECH_vtkMRMLDiffusionWeightedVolumeNodeB.nhdr --seedsFile /tmp/Slicer/CECH_vtkMRMLLabelMapVolumeNodeB.nhdr --labels 1 --maskFile /tmp/Slicer/CECH_vtkMRMLLabelMapVolumeNodeB.nhdr --tracts /tmp/Slicer/CECH_vtkMRMLFiberBundleNodeB.vtp --seedsPerVoxel 1 --seedFALimit 0.18 --minFA 0.15 --minGA 0.1 --numThreads -1 --numTensor 1 --stepLength 0.3 --Qm 0 --recordLength 1.8 --maxHalfFiberLength 250 --Ql 0 --Qw 0 --noddi --recordVic --recordKappa --recordViso --Qkappa 0.01 --Qvic 0.004 --Rs 0 --sigmaSignal 0 --maxBranchingAngle 0 --minBranchingAngle 0 
'''
# slicer UKF commands and default parameters to run
ukfcmds =  {'UKF_whbr': str(slicer_path) + 'UKFTractography --dwiFile %(fdwinrrd)s --seedsFile %(mask_fnamenrrd)s --labels 1 --maskFile %(mask_fnamenrrd)s --tracts %(dwif)s_UKF_whbr.vtk '
                    '--seedsPerVoxel 1 --seedFALimit 0.18 --minFA 0.15 --minGA 0.2 --numThreads -1 --numTensor 2 --stepLength 0.3 --Qm 0 --recordLength 1.8 --maxHalfFiberLength 250 --recordNMSE --freeWater '
                    '--recordFA --recordTrace --recordFreeWater --recordTensors --Ql 0 --Qw 0 --Qkappa 0.01 --Qvic 0.004 --Rs 0 --sigmaSignal 0 --maxBranchingAngle 0 --minBranchingAngle 0',
            'NODDI': str(slicer_path) + 'UKFTractography --dwiFile %(fdwinrrd)s --seedsFile %(mask_fnamenrrd)s --labels 1 --maskFile %(mask_fnamenrrd)s --tracts %(dwif)s_whbr_1tensor_noddi.vtk '
                    '--seedsPerVoxel 1 --seedFALimit 0.18 --minFA 0.15 --minGA 0.1 --numThreads -1 --numTensor 1 --stepLength 0.3 --Qm 0 --recordLength 1.8 --maxHalfFiberLength 250 --Ql 0 --Qw 0 --noddi --recordVic --recordKappa --recordViso --Qkappa 0.01 --Qvic 0.004 --Rs 0 --sigmaSignal 0 --maxBranchingAngle 0 --minBranchingAngle 0'
            }

def default_to_regular(d):
    if isinstance(d, defaultdict):
        d = {k: default_to_regular(v) for k, v in d.iteritems()}
    return d

def test4file(file):
    file = Path(file)
    if file.is_file():
        return True
    else:
        raise ValueError(str(file) + ' not found.')


# run conversion if needed
# if convert:
#     subjects = [x['subj'] for x in subjids_picks.subjids]
#     niftiDict = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
#     niftiDict, niftiDF = conv_subjs(project, subjects, niftiDict)
# else:
#     with open(niipickle, 'rb') as f:
#         niftiDict = cPickle.load(f)


for i, (topup, topdn, dwif) in enumerate(zip(topup_fnames, topdn_fnames, dwi_fnames)):
    result = ()
    dwipath = fs / project / dwif.split('_')[0] / dwif.split('_')[1] / 'dwi'
    regpath = fs / project / dwif.split('_')[0] / dwif.split('_')[1] / 'reg' / 'MNI2dwi'
    ec_dir = dwipath / eddy_corr_dir
    bedpost_dir = dwipath / 'bedpost'
    fits_dir = dwipath / fits_dir_name
    if not ec_dir.is_dir():
        ec_dir.mkdir(parents=True)
    if not regpath.is_dir():
        regpath.mkdir(parents=True)

    orig_dwif_fname = dwipath / str(dwif + qc_str + '.nii')
    dwi_bvals_fname = dwipath / str(dwif + qc_str + '.bvals')
    dwi_bvecs_fname = dwipath / str(dwif + qc_str + '.bvecs')
    topup_fname = dwipath / str(topup + qc_str + '.nii')
    topup_bvals_fname = dwipath / str(topup + qc_str + '.bvals')
    topup_bvecs_fname = dwipath / str(topup + qc_str + '.bvecs')
    topdn_fname = dwipath / str(topdn + qc_str + '.nii')
    topdn_bvals_fname = dwipath / str(topdn + qc_str + '.bvals')
    topdn_bvecs_fname = dwipath / str(topdn + qc_str + '.bvecs')
    dwi_dwellt_fname = dwipath / str(dwif + '.dwell_time')
    topup_dwellt_fname = dwipath / str(topup + '.dwell_time')
    topdn_dwellt_fname = dwipath / str(topdn + '.dwell_time')

    for f in [orig_dwif_fname, dwi_bvals_fname, dwi_bvecs_fname, dwi_dwellt_fname, topup_fname, topup_bvals_fname, \
              topup_bvecs_fname, topup_dwellt_fname, topdn_fname, topdn_bvals_fname, topdn_bvecs_fname, topdn_dwellt_fname]:
        test4file(f)

    with open(str(topup_dwellt_fname), 'r') as tud:
        topup_dwellt = tud.read().replace('\n', '')

    with open(str(topdn_dwellt_fname), 'r') as tdd:
        topdn_dwellt = tdd.read().replace('\n', '')

    topup_numlines = (nib.load(str(topup_fname))).header['dim'][4]
    topdn_numlines = (nib.load(str(topdn_fname))).header['dim'][4]

    with open(str(dwipath / 'acq_params.txt'), 'w') as ap:
        for x in range(topup_numlines):
            ap.write('0 1 0 ' + topup_dwellt + '\n')
        for x in range(topdn_numlines):
            ap.write('0 -1 0 ' + topdn_dwellt + '\n')

    bvals, bvecs = read_bvals_bvecs(str(dwi_bvals_fname), str(dwi_bvecs_fname))
    gtab = gradient_table(bvals, bvecs)
    # topup distortion correction
    if not test4file(dwipath / str(topup + '_topdn_concat_mf_unwarped_mean.nii.gz')) or (test4file(dwipath / str(topup + '_topdn_concat_mf_unwarped_mean.nii.gz')) & overwrite):
        topup_img = nib.load(str(topup_fname))
        topup_data = topup_img.get_data()
        topup_affine = topup_img.affine
        topdn_img = nib.load(str(topdn_fname))
        topdn_data = topdn_img.get_data()
        topdn_affine = topdn_img.affine
        topup_dn_data_concat = np.concatenate((topup_data, topdn_data), axis=3)
        topup_dn_data_concat_mf = medianf(topup_dn_data_concat, size=3)
        savenii(topup_dn_data_concat_mf, topup_affine, str(dwipath / str(topup + '_topdn_concat_mf.nii.gz')))
        prov.log(str(dwipath / str(topup + '_topdn_concat_mf.nii.gz')), 'concatenated topup-dn S0 vols', [str(topup_fname), str(topdn_fname)])

        with WorkingContext(str(dwipath)):
            with open('index.txt', 'w') as f:
                f.write('1 ' * len(gtab.bvals))
            if overwrite or not Path(topup + '_topdn_concat_mf_unwarped_mean.nii.gz').is_file():
                cmd = 'topup --imain=' + str(dwipath / str(topup + '_topdn_concat_mf.nii.gz'))
                cmd += ' --datain=acq_params.txt --config=b02b0.cnf --out='
                cmd += str(dwipath / str(topup + '_topdn_concat_mf'))
                cmd += ' --iout=' + str(dwipath / str(topup + '_topdn_concat_mf_unwarped.nii.gz'))
                cmd += ' --fout=' + str(dwipath / str(topup + '_topdn_concat_mf_warp_field.nii.gz'))
                result += run_subprocess(cmd)
                result += run_subprocess('fslmaths '+topup + '_topdn_concat_mf_unwarped'+' -Tmean '+topup + '_topdn_concat_mf_unwarped_mean.nii.gz')
                prov.log(str(dwipath / str(topup + '_topdn_concat_mf_unwarped_mean.nii.gz')), 'median filtered mean of topup-dn S0 vols',
                         [str(topup_fname), str(topdn_fname)])
    # eddy current correction
    ec_dwi_name = ec_dir / str(dwif +qc_str+ '_topdn_unwarped_ec')
    dwi_bvecs_ec_rot_fname = str(ec_dwi_name) + '.eddy_rotated_bvecs'
    if not test4file(replacesuffix(ec_dwi_name, mf_str+'_clamp1.nii.gz')) or (test4file(replacesuffix(ec_dwi_name, mf_str+'_clamp1.nii.gz')) & overwrite):
        with WorkingContext(str(ec_dir)):
            b0_brain_fname, b0_brain_mask_fname, b0_brain_cropped_fname = extract_brain(dwipath/str(topup + '_topdn_concat_mf_unwarped_mean.nii.gz'))
            eddy_cmd = 'eddy_cuda7.5 --imain='+str(orig_dwif_fname)+' --mask='+str(b0_brain_mask_fname)
            eddy_cmd += ' --acqp=acq_params.txt  --index=index.txt --bvecs='+str(dwi_bvecs_fname)
            eddy_cmd += ' --bvals='+str(dwi_bvals_fname)+' --topup='+str(dwipath / str(topup + '_topdn_concat_mf'))
            eddy_cmd += '  --repol --out='+str(ec_dwi_name)
            result += run_subprocess(eddy_cmd)
            # clamp, filter, and make nrrd
            ec_data = nib.load(str(ec_dwi_name)+'.nii.gz').get_data()
            ec_data_affine = nib.load(str(ec_dwi_name)+'.nii.gz').affine
            bvals, bvecs = read_bvals_bvecs(str(dwi_bvals_fname), str(dwi_bvecs_ec_rot_fname))
            gtab = gradient_table(bvals, bvecs)
            if mf_str != '':
                S0 = ec_data[:, :, :, gtab.b0s_mask]
                S0_mf = medianf(S0, size=3)
                ec_data[:, :, :, gtab.b0s_mask] = S0_mf
            ec_data[ec_data <= 0.1] = 0
            savenii(ec_data, ec_data_affine, str(ec_dwi_name)+mf_str+'_clamp1.nii.gz')
            prov.log(str(ec_dwi_name)+mf_str+'_clamp1.nii.gz', 'median filtered mean of topup-dn S0 vols', str(ec_dwi_name)+mf_str+'_clamp1.nii.gz')
            nii2nrrd(str(ec_dwi_name)+mf_str+'_clamp1.nii.gz', str(ec_dwi_name)+mf_str+'_clamp1.nhdr', bvalsf=str(dwi_bvals_fname), bvecsf=str(dwi_bvecs_ec_rot_fname))
            prov.log(str(ec_dwi_name)+mf_str+'_clamp1.nii.gz', 'median filtered mean of topup-dn S0 vols', str(ec_dwi_name)+mf_str+'_clamp1.nhdr')

    # bedpost input files and execute (hopefully) on gpu
    if not test4file(appendposix(bedpost_dir, '.bedpostX') / 'mean_S0samples.nii.gz') or (test4file(appendposix(bedpost_dir, '.bedpostX') / 'mean_S0samples.nii.gz') & overwrite):
        with WorkingContext(str(bedpost_dir)):
            shutil.copy(str(ec_dir/ec_dwi_name) + mf_str + '_clamp1.nii.gz', str(bedpost_dir))
            os.rename(str(ec_dwi_name) + mf_str + '_clamp1.nii.gz', str(bedpost_dir/'data.nii.gz'))
            shutil.copy(str(dwi_bvecs_ec_rot_fname), str(bedpost_dir))
            os.rename(str(bedpost_dir/dwi_bvecs_ec_rot_fname.name), str(bedpost_dir/'bvecs'))
            shutil.copy(str(dwi_bvals_fname), str(bedpost_dir))
            os.rename(str(bedpost_dir/dwi_bvals_fname.name), str(bedpost_dir/'bvals'))
            shutil.copy(str(dwipath/str(topup + '_topdn_concat_mf_unwarped_mean_brain_mask.nii.gz')), str(bedpost_dir))
            os.rename(str(bedpost_dir/str(topup + '_topdn_concat_mf_unwarped_mean_brain_mask.nii.gz')), str(bedpost_dir/'nodif_brain_mask.nii.gz'))
            # run bedpost, probtracks, network, UKF, NODDI, and DKI here
            if test4working_gpu():
                result += run_subprocess('bedpostx_gpu bedpost -n 3 --model=2')
                # what cleanup is required?
            else:
                result += run_subprocess('bedpostx bedpost -n 3 --model=2')

    # use ants to warp mori atlas into subj space
    if not test4file(regpath/replacesuffix(moriMNIatlas.name, '_reg2dwi.nii.gz')) or (test4file(regpath/replacesuffix(moriMNIatlas.name, '_reg2dwi.nii.gz')) & overwrite):
        with WorkingContext(regpath):
            MNI2b0_brain_antscmd = [str(antsRegistrationSyN), '-d 3 -m', str(MNI1mm_T2_brain), '-f',str(b0_brain_fname), '-o',
                                    str(regpath / replacesuffix(MNI1mm_T2_brain, '_reg2dwi_').name),'-n 30 -t s -p f -j 1 -s 10 -r 1']
            result += run_subprocess(' '.join(MNI2b0_brain_antscmd))
            warpfiles = [regpath/replacesuffix(moriMNIatlas, '_reg2dwi_1Warp.nii.gz'),]
            affines = [regpath/replacesuffix(moriMNIatlas, '_reg2dwi_0GenericAffine.mat'),]
            subj2templ_applywarp(str(moriMNIatlas), str(b0_brain_fname), str(regpath/replacesuffix(moriMNIatlas.name, '_reg2dwi.nii.gz')), warpfiles=warpfiles, regpath, affine_xform=affines)
            subj2templ_applywarp(str(MNI1mm_T1_brain), str(b0_brain_fname), str(regpath/replacesuffix(MNI1mm_T1_brain.name, '_reg2dwi.nii.gz')), warpfiles=warpfiles, regpath, affine_xform=affines)




    cmdvars = {'fdwinrrd': str(ec_dwi_name)+mf_str+'_clamp1.nhdr',
               'mask_fnamenrrd': str(dwipath/str(topup + '_topdn_concat_mf_unwarped_mean_brain_mask.nii.gz')),
               'dwif': str(fits_dir/dwif)}



'''
warp MNI_T1 to dwi for mricros :done
loop over mori to gen seed bin mask and dilate and get com coord and put subject.node 
probtracts cmd:
probtrackx2 --network -x listseeds.txt  -l --onewaycondition --omatrix1 -c 0.2 -S 1000 --steplength=0.5 -P 1000 --fibthresh=0.01 --distthresh=0.0 --sampvox=0.0 --forcedir --opd -s bedpost.bedpostX/merged -m bedpost.bedpostX/nodif_brain_mask  --dir=probtrackoutput


subject.node is row by row x y z center of mass coordinate for each seed plus 3 3 3 (space separated
150 130 48 3 3 3\n # for seed001.nii.gz
matrix2 = for loop by row matrix / waytotal to normalise and rename to .edge
this is the input for mricros 
'''