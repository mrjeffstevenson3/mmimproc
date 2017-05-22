from pathlib import *
from collections import defaultdict
import subprocess
from nipype.interfaces import fsl
fslbet = fsl.BET(output_type='NIFTI')

import pylabs
import inspect
import niprov
import nipype

import numpy as np
import nibabel as nib
from scipy.ndimage.measurements import center_of_mass as com
from dipy.segment.mask import applymask
from pylabs.utils.paths import getnetworkdataroot
fs = getnetworkdataroot()
from nipype.interfaces.fsl import Eddy
eddy = Eddy(num_threads=24, output_type='NIFTI')
from nipype.interfaces import fsl
flt = fsl.FLIRT(bins=640, interp='nearestneighbour', cost_func='mutualinfo', output_type='NIFTI')
if nipype.__version__ >= '0.12.0':
    applyxfm = fsl.ApplyXfm(interp='nearestneighbour', output_type='NIFTI')
else:
    applyxfm = fsl.ApplyXFM(interp='nearestneighbour', output_type='NIFTI')

bet = fsl.BET(output_type='NIFTI')
prov = niprov.ProvenanceContext()


import pylabs, os, inspect
from os.path import split
from os.path import join

pylabs_basepath = Path(*Path(inspect.getabsfile(pylabs)).parts[:-2])
mnicom = pylabs_basepath/'data'/'atlases'/'MNI152_T1_1mm_8kcomroi.nii'
mnimask = pylabs_basepath/'data'/'atlases'/'MNI152_T1_1mm_mask.nii'

# new universal (hopefully) brain extraction method
def extract_brain(file, f_factor=0.3):
    '''
    simplest form pass a pathlib file name and brain extraction is performed
    :param file: pathlib path and file name to be extracted
    :param dti: if dti=True S0 will be found and extracted and then brain extracted
    :param args: list of addl args
    :param kwargs: list of key word: values for addle specific args like f factor
    :param f_factor: threshold factor for brain extraction
    :return: 
    '''
    # remove ext if .nii or .nii.gz
    file = Path(file)
    if not file.is_file():
        raise ValueError(str(file)+' file is not found. please check')
    ext = file.suffixes
    ext = ''.join(ext)
    if not ext in '.nii' or not ext in '.nii.gz':
        raise ValueError(str(file) + ' file is not nifti with .nii or .nii.gz ext. please check')
    # make mat file for center of mass ROI and mask in MNI template
    flt.inputs.in_file = str(mnicom)
    flt.inputs.reference = str(file)
    flt.inputs.out_matrix_file = str(file.stem) + '_comroi.mat'
    flt.inputs.out_file = str(file.stem) + '_comroi.nii'
    res = flt.run()
    # apply mat file to MNI mask file to cut off neck
    applyxfm.inputs.in_matrix_file = str(file.stem) + '_comroi.mat'
    applyxfm.inputs.in_file = str(mnimask)
    applyxfm.inputs.out_file = str(file.stem)+'_mask.nii'
    applyxfm.inputs.reference = str(file)
    applyxfm.inputs.apply_xfm = True
    result = applyxfm.run()
    # crop neck with warped MNI mask
    file_data = nib.load(str(file)).get_data()
    com_data = nib.load(str(file.stem) + '_comroi.nii').get_data()
    mask_data = nib.load(str(file.stem)+'_mask.nii').get_data().astype(int)
    crop_file_data = applymask(file_data, mask_data)
    # get com for fsl bet
    com_data_bmask = com_data > 2500
    com_data_mask = np.zeros(com_data.shape)
    com_data_mask[com_data_bmask] = 1
    bet_com = np.round(com(com_data_mask)).astype(int)
    # save files
    crop_img = nib.Nifti1Image(crop_file_data, nib.load(str(file)).affine)
    crop_img.set_qform(crop_img.affine, code=1)
    crop_img.set_sform(crop_img.affine, code=1)
    nib.save(crop_img, str(file.stem) + '_cropped.nii')
    # extract brain and make fsl brain mask
    brain_outfname = str(file.stem)+'_brain'
    bet.inputs.in_file = str(file.stem) + '_cropped.nii'
    bet.inputs.center = list(bet_com)
    bet.inputs.frac = f_factor
    bet.inputs.mask = True
    bet.inputs.skull = True
    bet.inputs.out_file = brain_outfname + '.nii'
    betres = bet.run()
    prov.log(brain_outfname + '.nii', 'generic fsl bet brain', str(file), script=__file__, provenance={'f factor': f_factor, 'com': list(bet_com)})
    prov.log(brain_outfname + '_mask.nii', 'generic fsl bet brain mask', str(file), script=__file__, provenance={'f factor': f_factor, 'com': list(bet_com)})
    return


# old method with manual neck removal and center of mass
struc_betDict = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
struc_betDict[('sub-2013-C028', 'ses-1', 'anat')]['sub-2013-C028_ses-1_wemempr_1']['bet_com'] = (104, 145, 190)
struc_betDict[('sub-2013-C028', 'ses-1', 'anat')]['sub-2013-C028_ses-1_wemempr_1']['zcutoff'] = 73
struc_betDict[('sub-2013-C029', 'ses-2', 'anat')]['sub-2013-C029_ses-2_wemempr_1']['bet_com'] = (104, 142, 213)
struc_betDict[('sub-2013-C029', 'ses-2', 'anat')]['sub-2013-C029_ses-2_wemempr_1']['zcutoff'] = 95
struc_betDict[('sub-2013-C030', 'ses-1', 'anat')]['sub-2013-C030_ses-1_wemempr_1']['bet_com'] = (104, 144, 198)
struc_betDict[('sub-2013-C030', 'ses-1', 'anat')]['sub-2013-C030_ses-1_wemempr_1']['zcutoff'] = 66
struc_betDict[('sub-2013-C037', 'ses-1', 'anat')]['sub-2013-C037_ses-1_wemempr_1']['bet_com'] = (104, 124, 212)
struc_betDict[('sub-2013-C037', 'ses-1', 'anat')]['sub-2013-C037_ses-1_wemempr_1']['zcutoff'] = 100
struc_betDict[('sub-2013-C053', 'ses-1', 'anat')]['sub-2013-C053_ses-1_wemempr_1']['bet_com'] = (104, 115, 191)
struc_betDict[('sub-2013-C053', 'ses-1', 'anat')]['sub-2013-C053_ses-1_wemempr_1']['zcutoff'] = 75
struc_betDict[('sub-2013-C065', 'ses-1', 'anat')]['sub-2013-C065_ses-1_wemempr_1']['bet_com'] = (104, 132, 182)
struc_betDict[('sub-2013-C065', 'ses-1', 'anat')]['sub-2013-C065_ses-1_wemempr_1']['zcutoff'] = 57

struc_betDict[('sub-2013-C028', 'ses-1', 'anat')]['sub-2013-C028_ses-1_vbmmempr_1']['bet_com'] = (104, 145, 190)
struc_betDict[('sub-2013-C028', 'ses-1', 'anat')]['sub-2013-C028_ses-1_vbmmempr_1']['zcutoff'] = 73
struc_betDict[('sub-2013-C029', 'ses-2', 'anat')]['sub-2013-C029_ses-2_vbmmempr_1']['bet_com'] = (104, 142, 213)
struc_betDict[('sub-2013-C029', 'ses-2', 'anat')]['sub-2013-C029_ses-2_vbmmempr_1']['zcutoff'] = 95
struc_betDict[('sub-2013-C030', 'ses-1', 'anat')]['sub-2013-C030_ses-1_vbmmempr_1']['bet_com'] = (104, 144, 198)
struc_betDict[('sub-2013-C030', 'ses-1', 'anat')]['sub-2013-C030_ses-1_vbmmempr_1']['zcutoff'] = 66
struc_betDict[('sub-2013-C037', 'ses-1', 'anat')]['sub-2013-C037_ses-1_vbmmempr_1']['bet_com'] = (104, 124, 212)
struc_betDict[('sub-2013-C037', 'ses-1', 'anat')]['sub-2013-C037_ses-1_vbmmempr_1']['zcutoff'] = 100
struc_betDict[('sub-2013-C053', 'ses-1', 'anat')]['sub-2013-C053_ses-1_vbmmempr_1']['bet_com'] = (104, 115, 191)
struc_betDict[('sub-2013-C053', 'ses-1', 'anat')]['sub-2013-C053_ses-1_vbmmempr_1']['zcutoff'] = 75
struc_betDict[('sub-2013-C065', 'ses-1', 'anat')]['sub-2013-C065_ses-1_vbmmempr_1']['bet_com'] = (104, 132, 182)
struc_betDict[('sub-2013-C065', 'ses-1', 'anat')]['sub-2013-C065_ses-1_vbmmempr_1']['zcutoff'] = 57

struc_betDict[('sub-2013-C028', 'ses-1', 'anat')]['sub-2013-C028_ses-1_3dt2_1']['bet_com'] = (80, 107, 150)
struc_betDict[('sub-2013-C028', 'ses-1', 'anat')]['sub-2013-C028_ses-1_3dt2_1']['zcutoff'] = 60
struc_betDict[('sub-2013-C029', 'ses-2', 'anat')]['sub-2013-C029_ses-2_3dt2_1']['bet_com'] = (79, 109, 172)
struc_betDict[('sub-2013-C029', 'ses-2', 'anat')]['sub-2013-C029_ses-2_3dt2_1']['zcutoff'] = 79
struc_betDict[('sub-2013-C030', 'ses-1', 'anat')]['sub-2013-C030_ses-1_3dt2_1']['bet_com'] = (79, 108, 153)
struc_betDict[('sub-2013-C030', 'ses-1', 'anat')]['sub-2013-C030_ses-1_3dt2_1']['zcutoff'] = 53
struc_betDict[('sub-2013-C037', 'ses-1', 'anat')]['sub-2013-C037_ses-1_3dt2_1']['bet_com'] = (79, 95, 171)
struc_betDict[('sub-2013-C037', 'ses-1', 'anat')]['sub-2013-C037_ses-1_3dt2_1']['zcutoff'] = 81
struc_betDict[('sub-2013-C053', 'ses-1', 'anat')]['sub-2013-C053_ses-1_3dt2_1']['bet_com'] = (79, 93, 156)
struc_betDict[('sub-2013-C053', 'ses-1', 'anat')]['sub-2013-C053_ses-1_3dt2_1']['zcutoff'] = 61
struc_betDict[('sub-2013-C065', 'ses-1', 'anat')]['sub-2013-C065_ses-1_3dt2_1']['bet_com'] = (79, 104, 148)
struc_betDict[('sub-2013-C065', 'ses-1', 'anat')]['sub-2013-C065_ses-1_3dt2_1']['zcutoff'] = 47



def struc_bet(key1, key2, key3, niftiDict, frac=0.25):
    # if key1 not in struc_betDict:
    #     raise ValueError(key1+' not in struc_betDict! Please check.')
    # if key1 in struc_betDict and key2 not in struc_betDict[key1]:
    #     raise ValueError(key2+' not in 2nd level struc_betDict! Please check.')
    fname = niftiDict[key1][key2][key3]
    head_img = nib.load(fname)
    head_data = np.array(head_img.dataobj)
    head_data_zcrop = head_data
    head_data_zcrop[:,:,0:struc_betDict[key1][key2]['zcutoff']] = 0
    ncrop_img = nib.Nifti1Image(head_data_zcrop, head_img.affine)
    outfname = fname.split('.')[0] + '_zcrop.nii.gz'
    nib.save(ncrop_img, outfname)
    cmd = 'bet '+outfname+' '+fname.split('.')[0] + '_brain.nii.gz'+' -m -f '+str(frac)+' -c '
    cmd += ' '.join(map(str, struc_betDict[('sub-2013-C028', 'ses-1', 'anat')]['sub-2013-C028_ses-1_wemempr_1']['bet_com']))
    subprocess.check_call(cmd, shell=True)
    niftiDict[key1][key2]['brain_fname'] = fname.split('.')[0] + '_brain.nii.gz'
    niftiDict[key1][key2]['mask_fname'] = fname.split('.')[0] + '_brain_mask.nii.gz'
    niftiDict[key1][key2]['bet_com'] = struc_betDict[('sub-2013-C028', 'ses-1', 'anat')]['sub-2013-C028_ses-1_wemempr_1']['bet_com']
    niftiDict[key1][key2]['zcutoff'] = struc_betDict[key1][key2]['zcutoff']
    prov.add(niftiDict[key1][key2]['brain_fname'])
    prov.add(niftiDict[key1][key2]['mask_fname'])
    return niftiDict

