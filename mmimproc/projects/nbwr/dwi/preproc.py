# first set global root data directory
import mmimproc
mmimproc.datadir.target = 'jaba'
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
from scipy.ndimage.filters import median_filter as medianf
from mmimproc.structural.brain_extraction import extract_brain
from mmimproc.conversion.brain_convert import conv_subjs
from mmimproc.conversion.nifti2nrrd import nii2nrrd
from mmimproc.alignment.ants_reg import subj2templ_applywarp
from mmimproc.correlation.atlas import mori_network_regions
from mmimproc.io.images import savenii
from mmimproc.utils import ProvenanceWrapper, run_subprocess, WorkingContext, appendposix, replacesuffix, getnetworkdataroot, test4working_gpu, get_antsregsyn_cmd, MNI1mm_T2_brain, getslicercmd, \
        moriMNIatlas, MNI1mm_T1_brain, getslicercmd
prov = ProvenanceWrapper()


fs = mmimproc.fs

#  define hostnames with working gpus for processing
flt = fsl.FLIRT(bins=640, interp='nearestneighbour', cost_func='mutualinfo', output_type='NIFTI_GZ')
if nipype.__version__ == '0.12.0':
    applyxfm = fsl.ApplyXfm(interp='nearestneighbour', output_type='NIFTI_GZ')
else:
    applyxfm = fsl.ApplyXFM(interp='nearestneighbour', output_type='NIFTI_GZ')

print(os.environ['FSLOUTPUTTYPE'])

antsRegistrationSyN = get_antsregsyn_cmd()
slicer_path = getslicercmd()

# project and subjects and files to run on
from mmimproc.projects.nbwr.file_names import project, SubjIdPicks, get_dwi_names, subjs_h5_info_fname
# instantiate subject id list container
subjids_picks = SubjIdPicks()
# list of subject ids to operate on
picks = ['447', ]

setattr(subjids_picks, 'subjids', picks)
# get file names
topup_fnames, topdn_fnames, dwi_fnames = get_dwi_names(subjids_picks)

eddy_corr_dir = 'eddy_cuda_repol_v1'   # output dir for eddy
fits_dir_name = 'fits_v1'    # dir for all fitting methods
filterS0_string = '_mf'

#stages to run
overwrite = True
convert = False
run_topup = True
subT2 = False   #wip
eddy_corr = True

dti_qc = False
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
        d = {k: default_to_regular(v) for k, v in d.items()}
    return d

def test4file(file):
    file = Path(file)
    if file.is_file():
        return True
    else:
        return False

#run conversion if needed
# if convert:
#     niftiDict = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
#
#     hdf_fname = fs / project / 'test.h5'
#     niftiDict, niftiDF = conv_subjs(project, subjects, hdf_fname)
# else:
#     with open(niipickle, 'rb') as f:
#         niftiDict = cPickle.load(f)


for i, (topup, topdn, dwif) in enumerate(zip(topup_fnames, topdn_fnames, dwi_fnames)):
    result = ()
    subjid = dwif.split('_')[0]
    session = dwif.split('_')[1]
    dwipath = fs / project / dwif.split('_')[0] / dwif.split('_')[1] / 'dwi'
    regpath = fs / project / dwif.split('_')[0] / dwif.split('_')[1] / 'reg' / 'MNI2dwi'
    ec_dir = dwipath / eddy_corr_dir
    bedpost_dir = dwipath / 'bedpost'
    fits_dir = dwipath / fits_dir_name
    if not ec_dir.is_dir():
        ec_dir.mkdir(parents=True)
    if not regpath.is_dir():
        regpath.mkdir(parents=True)
    orig_dwif_fname = dwipath / str(dwif + '.nii')
    dwi_bvals_fname = dwipath / str(dwif + '.bvals')
    dwi_bvecs_fname = dwipath / str(dwif + '.bvecs')
    dwi_dwellt_fname = dwipath / str(dwif + '.dwell_time')
    topup_fname = dwipath / str(topup + '.nii')
    topup_bvals_fname = dwipath / str(topup + '.bvals')
    topup_bvecs_fname = dwipath / str(topup + '.bvecs')
    topup_dwellt_fname = dwipath / str(topup + '.dwell_time')
    topdn_fname = dwipath / str(topdn + '.nii')
    topdn_bvals_fname = dwipath / str(topdn + '.bvals')
    topdn_bvecs_fname = dwipath / str(topdn + '.bvecs')
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
    bvals, bvecs = read_bvals_bvecs(str(dwi_bvals_fname), str(dwi_bvecs_fname))
    gtab = gradient_table(bvals, bvecs)
    acqparams_fname = dwipath / 'acq_params.txt'
    index_fname = dwipath / 'index.txt'
    with open(str(acqparams_fname), 'w') as ap:
        for x in range(topup_numlines):
            ap.write('0 1 0 ' + topup_dwellt + '\n')
        for x in range(topdn_numlines):
            ap.write('0 -1 0 ' + topdn_dwellt + '\n')


    # topup distortion correction
    if not test4file(dwipath / str(topup + '_topdn_concat_unwarped_mean.nii.gz')) or (test4file(dwipath / str(topup + '_topdn_concat_unwarped_mean.nii.gz')) & overwrite):
        topup_img = nib.load(str(topup_fname))
        topup_data = topup_img.get_data()
        topup_affine = topup_img.affine
        topdn_img = nib.load(str(topdn_fname))
        topdn_data = topdn_img.get_data()
        topdn_affine = topdn_img.affine
        topup_dn_data_concat = np.concatenate((topup_data, topdn_data), axis=3)
        topup_dn_concat_img = nib.Nifti1Image(topup_dn_data_concat, topup_affine)
        topup_dn_concat_img.set_sform(topup_affine, code=1)
        topup_dn_concat_img.set_qform(topup_affine, code=1)
        nib.save(topup_dn_concat_img, str(dwipath / str(topup + '_topdn_concat.nii.gz')))
        prov.log(str(dwipath / str(topup + '_topdn_concat.nii.gz')), 'concatenated topup-dn S0 vols', [str(topup_fname), str(topdn_fname)])

        with WorkingContext(str(dwipath)):
            with open(str(index_fname), 'w') as f:
                f.write('1 ' * len(gtab.bvals))
            if overwrite or not Path(topup + '_topdn_concat_unwarped_mean.nii.gz').is_file():
                cmd = 'topup --imain=' + str(dwipath / str(topup + '_topdn_concat.nii.gz'))
                cmd += ' --datain='+str(acqparams_fname)+' --config=b02b0.cnf --out='
                cmd += str(dwipath / str(topup + '_topdn_concat'))
                cmd += ' --iout=' + str(dwipath / str(topup + '_topdn_concat_unwarped.nii.gz'))
                cmd += ' --fout=' + str(dwipath / str(topup + '_topdn_concat_warp_field.nii.gz'))
                result += run_subprocess(cmd)
                result += run_subprocess('fslmaths '+topup + '_topdn_concat_unwarped'+' -Tmean '+topup + '_topdn_concat_unwarped_mean.nii.gz')

    # eddy current correction
    ec_dwi_name = ec_dir / str(dwif + '_topdn_unwarped_ec')
    dwi_bvecs_ec_rot_fname = Path(str(ec_dwi_name) + '.eddy_rotated_bvecs')
    if not test4file(replacesuffix(ec_dwi_name, filterS0_string+'_clamp1.nii.gz')) or (test4file(replacesuffix(ec_dwi_name, filterS0_string+'_clamp1.nii.gz')) & overwrite):
        with WorkingContext(str(ec_dir)):
            b0_brain_fname, b0_brain_mask_fname, b0_brain_cropped_fname = extract_brain(dwipath/str(topup + '_topdn_concat_unwarped_mean.nii.gz'))
            eddy_cmd = 'eddy_cuda7.5 --imain='+str(orig_dwif_fname)+' --mask='+str(b0_brain_mask_fname)
            eddy_cmd += ' --acqp='+str(acqparams_fname)+'  --index='+str(index_fname)+' --bvecs='+str(dwi_bvecs_fname)
            eddy_cmd += ' --bvals='+str(dwi_bvals_fname)+' --topup='+str(dwipath / str(topup + '_topdn_concat'))
            eddy_cmd += '  --repol --out='+str(ec_dwi_name)
            result += run_subprocess(eddy_cmd)
            # clamp, filter, and make nrrd
            ec_data = nib.load(str(ec_dwi_name)+'.nii.gz').get_data()
            ec_data_affine = nib.load(str(ec_dwi_name)+'.nii.gz').affine
            bvals, bvecs = read_bvals_bvecs(str(dwi_bvals_fname), str(dwi_bvecs_ec_rot_fname))
            gtab = gradient_table(bvals, bvecs)
            if filterS0_string != '':
                S0 = ec_data[:, :, :, gtab.b0s_mask]
                S0_mf = medianf(S0, size=3)
                ec_data[:, :, :, gtab.b0s_mask] = S0_mf
            ec_data[ec_data <= 1] = 0
            savenii(ec_data, ec_data_affine, str(ec_dwi_name)+filterS0_string+'_clamp1.nii.gz')
            nii2nrrd(str(ec_dwi_name)+filterS0_string+'_clamp1.nii.gz', str(ec_dwi_name)+filterS0_string+'_clamp1.nhdr', bvalsf=str(dwi_bvals_fname), bvecsf=str(dwi_bvecs_ec_rot_fname))
            # add fsl fits here

    # bedpost input files and execute (hopefully) on gpu
    if overwrite or not test4file(appendposix(bedpost_dir, '.bedpostX') / 'mean_S0samples.nii.gz'):
        with WorkingContext(str(dwipath)):
            # set up files in bedpost dir
            shutil.copy(str(ec_dwi_name) + filterS0_string + '_clamp1.nii.gz', str(bedpost_dir))
            os.rename(str(bedpost_dir/ec_dwi_name.name) + filterS0_string + '_clamp1.nii.gz', str(bedpost_dir/'data.nii.gz'))
            shutil.copy(str(dwi_bvecs_ec_rot_fname), str(bedpost_dir))
            os.rename(str(bedpost_dir/dwi_bvecs_ec_rot_fname.name), str(bedpost_dir/'bvecs'))
            shutil.copy(str(dwi_bvals_fname), str(bedpost_dir))
            os.rename(str(bedpost_dir/dwi_bvals_fname.name), str(bedpost_dir/'bvals'))
            shutil.copy(str(dwipath/str(topup + '_topdn_concat_unwarped_mean_brain_mask.nii.gz')), str(bedpost_dir))
            os.rename(str(bedpost_dir/str(topup + '_topdn_concat_unwarped_mean_brain_mask.nii.gz')), str(bedpost_dir/'nodif_brain_mask.nii.gz'))
            # run dtifit, bedpost, probtracks, network, UKF, NODDI, and DKI here
            if not (dwipath/'fsldtifit').is_dir():
                (dwipath / 'fsldtifit').mkdir(parents=True)
            with WorkingContext(str(bedpost_dir)):
                result += run_subprocess(['dtifit -k data.nii.gz -o ../fsldtifit/'+subjid+'_'+session+'_dwi_topupdn_ec_fsl'+' -m nodif_brain_mask.nii.gz -r bvecs -b bvals --save_tensor --sse -w'])
            if test4working_gpu():
                result += run_subprocess('bedpostx_gpu bedpost -n 3 --model=2')
                # what cleanup is required?
            else:
                result += run_subprocess('bedpostx bedpost -n 3 --model=2')

    # use ants to warp mori atlas into subj space
    if not test4file(regpath/replacesuffix(moriMNIatlas.name, '_reg2dwi.nii.gz')) or (test4file(regpath/replacesuffix(moriMNIatlas.name, '_reg2dwi.nii.gz')) & overwrite):
        with WorkingContext(str(regpath)):
            MNI2b0_brain_antscmd = [str(antsRegistrationSyN), '-d 3 -m', str(MNI1mm_T2_brain), '-f',str(b0_brain_fname), '-o',
                                    str(regpath / replacesuffix(MNI1mm_T2_brain, '_reg2dwi_').name),'-n 30 -t s -p f -j 1 -s 10 -r 1']
            result += run_subprocess([' '.join(MNI2b0_brain_antscmd)])
            warpfiles = [str(regpath/replacesuffix(moriMNIatlas, '_reg2dwi_1Warp.nii.gz')),]
            affines = [str(regpath/replacesuffix(moriMNIatlas, '_reg2dwi_0GenericAffine.mat')),]
            subj2templ_applywarp(str(moriMNIatlas), str(b0_brain_fname), str(regpath/replacesuffix(moriMNIatlas.name, '_reg2dwi.nii.gz')), warpfiles, str(regpath), affine_xform=affines)
            subj2templ_applywarp(str(MNI1mm_T1_brain), str(b0_brain_fname), str(regpath/replacesuffix(MNI1mm_T1_brain.name, '_reg2dwi.nii.gz')), warpfiles, str(regpath), affine_xform=affines)




    cmdvars = {'fdwinrrd': str(ec_dwi_name)+filterS0_string+'_clamp1.nhdr',
               'mask_fnamenrrd': str(dwipath/str(topup + '_topdn_concat_unwarped_mean_brain_mask.nii.gz')),
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