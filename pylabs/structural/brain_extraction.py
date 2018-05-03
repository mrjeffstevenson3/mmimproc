# todo: make ants version that works with dti cropped topup_dn_mean_brain images.
# extract brain and mask function. now uses pylabs.opts to set file ext
import pylabs
pylabs.datadir.target = 'jaba'
from pathlib import *
from collections import defaultdict
import subprocess
import inspect
import nipype
import numpy as np
import nibabel as nib
from scipy.ndimage.measurements import center_of_mass as com
from dipy.segment.mask import applymask
from pylabs.io.images import savenii, gz2nii
from pylabs.utils import *
from pylabs.utils.paths import mnicom, mnimask, mniT2com
from nipype.interfaces import fsl
flt = fsl.FLIRT(bins=640, interp='nearestneighbour', cost_func='mutualinfo', output_type=pylabs.opts.nii_ftype)
if nipype.__version__ == '0.12.0':
    applyxfm = fsl.ApplyXfm(interp='nearestneighbour', output_type=pylabs.opts.nii_ftype)
else:
    applyxfm = fsl.ApplyXFM(interp='nearestneighbour', output_type=pylabs.opts.nii_ftype)

bet = fsl.BET(output_type=pylabs.opts.nii_ftype)
prov = ProvenanceWrapper()
fs = getnetworkdataroot()  # should pick up datadir.target
ext = pylabs.opts.nii_fext

# new universal (hopefully) brain extraction method
def extract_brain(file, f_factor=0.3, mmzshift=0.0, mode='T1', nii=False, dwi=False, robust=False, cleanup=True):
    '''
    simplest form pass a pathlib file name and brain extraction is performed
    :param file: pathlib path and file name to be extracted
    :param mode: T2 uses MNI T2 contrast head as com. dti=True undeveloped at this time
    :param args: list of addl args
    :param kwargs: list of key word: values for additional specific bet2 args
    :param f_factor: threshold factor for brain extraction
    :param nii: True will force conversion from .nii.gz compressed to .nii uncompressed
    :param dwi: True will use croppped mniT2 instad of whole head mniT2
    :return: 
    '''
    # remove ext if .nii or .nii.gz output_type='NIFTI_GZ'
    ext = pylabs.opts.nii_fext
    file = Path(file)
    if not file.is_file():
        raise ValueError(str(file)+' file is not found. please check')
    if not any(ex in ['.nii', '.nii.gz'] for ex in file.suffixes):
        raise ValueError(str(file) + ' file is not nifti with .nii or .nii.gz ext. please check')
    else:
        if ''.join(file.suffixes) == '.nii' and ext == '.nii':
            nifti = True  # uncompressed original
        else:
            nifti = False   # compressed original
    # make mat file for center of mass ROI and mask in MNI template
    # develop method to deal with dti S0 cropped images
    if mode == 'T1':
        flt.inputs.in_file = str(mnicom)
        flt.inputs.cost_func = 'mutualinfo'
    elif dwi and mode == 'T2':
        flt.inputs.in_file = str(mniT2comdwi)
        flt.inputs.cost_func = 'mutualinfo'
    elif mode == 'T2' and not dwi:
        flt.inputs.in_file = str(mniT2com)
        flt.inputs.cost_func = 'mutualinfo'
    flt.inputs.reference = str(file)
    flt.inputs.out_matrix_file = str(file.parent/appendposix(Path(file.stem).stem, '_comroi.mat'))
    flt.inputs.out_file = str(replacesuffix(file, '_comroi'+ext))
    flt.inputs.searchr_x = [-30, 30]
    flt.inputs.searchr_y = [-30, 30]
    flt.inputs.searchr_z = [-30, 30]
    flt.inputs.interp = 'nearestneighbour'
    res = flt.run()
    # apply mat file to MNI mask file to cut off neck
    mat_fname = file.parent/appendposix(Path(file.stem).stem, '_comroi.mat')
    affine_xfm = np.fromfile(str(mat_fname), dtype='float', count=-1, sep=' ').reshape(4, 4)
    affine_xfm[2,3] = affine_xfm[2,3] - (mmzshift * nib.load(str(file)).header.get_zooms()[2])
    np.savetxt(str(appendposix(mat_fname, '_zshift'+str(mmzshift))), affine_xfm, fmt='%.9f', delimiter=' ', newline='\n')
    applyxfm.inputs.in_matrix_file = str(appendposix(mat_fname, '_zshift'+str(mmzshift)))
    applyxfm.inputs.in_file = str(meg_head_mask)
    applyxfm.inputs.out_file = str(replacesuffix(file, '_mask'+ext))
    applyxfm.inputs.reference = str(file)
    applyxfm.inputs.apply_xfm = True
    result = applyxfm.run()
    # crop neck with warped MNI mask and save
    file_data = nib.load(str(file)).get_data().astype(np.float64)
    com_data = nib.load(str(replacesuffix(file, '_comroi'+ext))).get_data().astype(np.float64)
    mask_data = nib.load(str(replacesuffix(file, '_mask'+ext))).get_data().astype(np.uint32)
    crop_file_data = applymask(file_data, mask_data)
    savenii(crop_file_data, nib.load(str(file)).affine, str(replacesuffix(file, '_cropped'+ext)))
    # get com for fsl bet
    com_data_bmask = com_data > 2500
    com_data_mask = np.zeros(com_data.shape)
    com_data_mask[com_data_bmask] = 1
    bet_com = np.round(com(com_data_mask)).astype(int)
    # extract brain and make fsl brain mask
    brain_outfname = str(replacesuffix(file, '_brain'))
    bet.inputs.in_file = str(replacesuffix(file, '_cropped'+ext))
    bet.inputs.center = list(bet_com)
    bet.inputs.frac = f_factor
    bet.inputs.mask = True
    bet.inputs.skull = True
    if robust:
        bet.inputs.robust = True
    bet.inputs.out_file = brain_outfname
    betres = bet.run()
    if nii:
        ext = '.nii'
        gz2nii(brain_outfname+'.nii.gz', delete_gz=True)
        gz2nii(brain_outfname + '_mask.nii.gz', delete_gz=True)
        gz2nii(replacesuffix(file, '_cropped.nii.gz'), delete_gz=True)
    prov.log(brain_outfname+ext, 'generic fsl bet brain', str(file), script=__file__, provenance={'f factor': f_factor, 'com': list(bet_com), })
    prov.log(str(replacesuffix(file, '_brain_mask'+ext)), 'generic fsl bet brain mask', str(file), script=__file__, provenance={'f factor': f_factor, 'com': list(bet_com)})
    prov.log(str(replacesuffix(file, '_cropped'+ext)), 'generic fsl bet brain mask', str(file), script=__file__,
             provenance={'f factor': f_factor, 'com': list(bet_com)})
    if cleanup:
        Path(replacesuffix(file, '_comroi'+ext)).unlink()
        Path(replacesuffix(file, '_comroi.mat')).unlink()
        Path(replacesuffix(file, '_brain_skull'+ext)).unlink()
        Path(replacesuffix(file, '_mask'+ext)).unlink()
        if mmzshift == 0:
            Path(appendposix(mat_fname, '_zshift'+str(mmzshift))).unlink()
    return replacesuffix(file, '_brain'+ext), replacesuffix(file, '_brain_mask'+ext), replacesuffix(file, '_cropped'+ext)


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

