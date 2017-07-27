import os, cPickle
from pathlib import *
from collections import defaultdict
from nipype.interfaces import fsl
import nibabel as nib
import numpy as np
from dipy.io import read_bvals_bvecs
from dipy.core.gradients import gradient_table
import shutil
from datetime import datetime
from cloud.serialization.cloudpickle import dumps
from scipy.ndimage.filters import median_filter as medianf
from pylabs.structural.brain_extraction import extract_brain
from pylabs.structural.brain_extraction import struc_bet
from pylabs.conversion.brain_convert import conv_subjs
from pylabs.conversion.nifti2nrrd import nii2nrrd
from pylabs.io.images import loadStack
from pylabs.io.images import savenii
from pylabs.utils import run_subprocess, WorkingContext, appendposix
from pylabs.utils.paths import getnetworkdataroot, test4working_gpu, get_antsregsyn_cmd, moriMNIatlas
from pylabs.correlation.atlas import mori_network_regions
from pylabs.utils.provenance import ProvenanceWrapper
prov = ProvenanceWrapper()
fs = Path(getnetworkdataroot())
#  define hostnames with working gpus for processing
flt = fsl.FLIRT(bins=640, interp='nearestneighbour', cost_func='mutualinfo', output_type='NIFTI_GZ')
applyxfm = fsl.ApplyXFM(output_type='NIFTI_GZ')
print(os.environ['FSLOUTPUTTYPE'])

antsRegistrationSyN = get_antsregsyn_cmd()

# project and subjects and files to run on
from pylabs.projects.nbwr.file_names import project, topup_fnames, topdn_fnames, dwi_fnames

eddy_corr_dir = 'eddy_cuda_repol_v2'
filterS0_string = '_mf'
niipickle = fs / project / 'nbwrniftiDict_201706221132.pickle'
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
/home/toddr/.config/NA-MIC/Extensions-26072/UKFTractography/lib/Slicer-4.7/cli-modules/UKFTractography --dwiFile /tmp/Slicer/CGGHB_vtkMRMLDiffusionWeightedVolumeNodeB.nhdr --seedsFile /tmp/Slicer/CGGHB_vtkMRMLLabelMapVolumeNodeB.nhdr --labels 1 --maskFile /tmp/Slicer/CGGHB_vtkMRMLLabelMapVolumeNodeB.nhdr --tracts /tmp/Slicer/CGGHB_vtkMRMLFiberBundleNodeB.vtp --seedsPerVoxel 1 --seedFALimit 0.18 --minFA 0.15 --minGA 0.1 --numThreads -1 --numTensor 2 --stepLength 0.3 --Qm 0 --recordLength 1.8 --maxHalfFiberLength 250 --recordNMSE --freeWater --recordFA --recordTrace --recordFreeWater --recordTensors --Ql 0 --Qw 0 --Qkappa 0.01 --Qvic 0.004 --Rs 0 --sigmaSignal 0 --maxBranchingAngle 0 --minBranchingAngle 0 
NODDI Command to modify
/home/toddr/.config/NA-MIC/Extensions-26072/UKFTractography/lib/Slicer-4.7/cli-modules/UKFTractography --dwiFile /tmp/Slicer/CECH_vtkMRMLDiffusionWeightedVolumeNodeB.nhdr --seedsFile /tmp/Slicer/CECH_vtkMRMLLabelMapVolumeNodeB.nhdr --labels 1 --maskFile /tmp/Slicer/CECH_vtkMRMLLabelMapVolumeNodeB.nhdr --tracts /tmp/Slicer/CECH_vtkMRMLFiberBundleNodeB.vtp --seedsPerVoxel 1 --seedFALimit 0.18 --minFA 0.15 --minGA 0.1 --numThreads -1 --numTensor 1 --stepLength 0.3 --Qm 0 --recordLength 1.8 --maxHalfFiberLength 250 --Ql 0 --Qw 0 --noddi --recordVic --recordKappa --recordViso --Qkappa 0.01 --Qvic 0.004 --Rs 0 --sigmaSignal 0 --maxBranchingAngle 0 --minBranchingAngle 0 
'''


# testing and selecting
start_pick = 2
end_pick = 3
assert start_pick < end_pick
topup_fnames, topdn_fnames, dwi_fnames = [topup_fnames[start_pick:end_pick]], [topdn_fnames[start_pick:end_pick]], [dwi_fnames[start_pick:end_pick]]

def default_to_regular(d):
    if isinstance(d, defaultdict):
        d = {k: default_to_regular(v) for k, v in d.iteritems()}
    return d

def test4file(file):
    if isinstance(file, PurePath):
        if file.is_file():
            return True
        else:
            raise ValueError(str(file) + ' not found.')
    else:
        raise ValueError(str(file) + ' is not a pathlib PosixPath object.')



#run conversion if needed
# if convert:
#     niftiDict = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
#     niftiDict, niftiDF = conv_subjs(project, subjects, niftiDict)
# else:
#     with open(niipickle, 'rb') as f:
#         niftiDict = cPickle.load(f)

if run_topup:
    for i, (topup, topdn, dwif) in enumerate(zip(topup_fnames, topdn_fnames, dwi_fnames)):
        dwipath = fs / project / dwif.split('_')[0] / dwif.split('_')[1] / 'dwi'
        regpath = fs / project / dwif.split('_')[0] / dwif.split('_')[1] / 'reg' / 'reg_MNI2dwi'
        ec_dir = dwipath / eddy_corr_dir
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

        with open(str(dwipath / 'acq_params.txt'), 'w') as ap:
            for x in range(topup_numlines):
                ap.write('0 1 0 ' + topup_dwellt + '\n')
            for x in range(topdn_numlines):
                ap.write('0 -1 0 ' + topdn_dwellt + '\n')

        bvals, bvecs = read_bvals_bvecs(str(dwi_bvals_fname), str(dwi_bvecs_fname))
        gtab = gradient_table(bvals, bvecs)
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
        result = ()
        with WorkingContext(str(dwipath)):
            with open('index.txt', 'w') as f:
                f.write('1 ' * len(gtab.bvals))
            if overwrite or not Path(topup + '_topdn_concat_unwarped_mean.nii.gz').is_file():
                cmd = 'topup --imain=' + str(dwipath / str(topup + '_topdn_concat.nii.gz'))
                cmd += ' --datain=acq_params.txt --config=b02b0.cnf --out='
                cmd += str(dwipath / str(topup + '_topdn_concat'))
                cmd += ' --iout=' + str(dwipath / str(topup + '_topdn_concat_unwarped.nii.gz'))
                cmd += ' --fout=' + str(dwipath / str(topup + '_topdn_concat_warp_field.nii.gz'))
                result += run_subprocess(cmd)
                result += run_subprocess('fslmaths '+topup + '_topdn_concat_unwarped'+' -Tmean '+topup + '_topdn_concat_unwarped_mean.nii.gz')

            ec_dwi_name = ec_dir/str(dwif + '_topdn_unwarped_ec')
            extract_brain(dwipath/str(topup + '_topdn_concat_unwarped_mean.nii.gz'))
            b0_brain_fname = dwipath/str(topup + '_topdn_concat_unwarped_mean_brain.nii.gz')
            eddy_cmd = 'eddy_cuda7.5 --imain='+str(orig_dwif_fname)+' --mask='+str(appendposix(b0_brain_fname, '_mask'))
            eddy_cmd += ' --acqp=acq_params.txt  --index=index.txt --bvecs='+str(dwi_bvecs_fname)
            eddy_cmd += ' --bvals='+str(dwi_bvals_fname)+' --topup='+str(dwipath / str(topup + '_topdn_concat'))
            eddy_cmd += '  --repol --out='+str(ec_dwi_name)
            result += run_subprocess(eddy_cmd)
            dwi_bvecs_ec_rot_fname = str(ec_dwi_name)+'.eddy_rotated_bvecs'
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
            # use ec to make bedpost file, populate input files and execute on cluster
            bedpost_dir = dwipath/'bedpost'
            savenii(ec_data, ec_data_affine, str(bedpost_dir/'data.nii.gz'))
            shutil.copy(str(dwi_bvecs_ec_rot_fname), str(bedpost_dir))
            os.rename(str(bedpost_dir/dwi_bvecs_ec_rot_fname.name), str(bedpost_dir/'bvecs'))
            shutil.copy(str(dwi_bvals_fname), str(bedpost_dir))
            os.rename(str(bedpost_dir/dwi_bvals_fname.name), str(bedpost_dir/'bvals'))
            shutil.copy(str(dwipath/str(topup + '_topdn_concat_unwarped_mean_brain_mask.nii.gz')), str(bedpost_dir))
            os.rename(str(bedpost_dir/str(topup + '_topdn_concat_unwarped_mean_brain_mask.nii.gz')), str(bedpost_dir/'nodif_brain_mask.nii.gz'))
            if test4working_gpu():
                run_subprocess('bedpostx_gpu bedpost -n 3 --model=2')
            else:
                run_subprocess('bedpostx bedpost -n 3 --model=2')

            MNI2b0_brain_antscmd = [str(antsRegistrationSyN), '-d 3 -m',
                                 str(moriMNIatlas), '-f',
                                 str(b0_brain_fname), '-o',
                                 str(dwipath/str(topup + '_topdn_concat_unwarped_mean_brain.nii.gz')_reg2spgr30_')),
                                 '-n 30 -t s -p f -j 1 -s 10 -r 1']



