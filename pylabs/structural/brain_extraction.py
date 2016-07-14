from collections import defaultdict
import subprocess
import numpy as np
import nibabel
import nibabel.nifti1 as nifti1
import niprov
from nipype.interfaces import fsl
fslbet = fsl.BET(output_type='NIFTI')
prov = niprov.ProvenanceContext()

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
    head_img = nibabel.load(fname)
    head_data = np.array(head_img.dataobj)
    head_data_zcrop = head_data
    head_data_zcrop[:,:,0:struc_betDict[key1][key2]['zcutoff']] = 0
    ncrop_img = nifti1.Nifti1Image(head_data_zcrop, head_img.affine)
    outfname = fname.split('.')[0] + '_zcrop.nii.gz'
    nibabel.save(ncrop_img, outfname)
    cmd = 'bet '+outfname+' '+fname.split('.')[0] + '_brain.nii.gz'+' -m -f '+str(frac)+' -c '
    cmd += ' '.join(map(str, struc_betDict[('sub-2013-C028', 'ses-1', 'anat')]['sub-2013-C028_ses-1_wemempr_1']['bet_com']))
    subprocess.check_call(cmd, shell=True)
    niftiDict[key1][key2]['brain_fname'] = fname.split('.')[0] + '_brain.nii.gz'
    niftiDict[key1][key2]['mask_fname'] = fname.split('.')[0] + '_brain_mask.nii.gz'
    niftiDict[key1][key2]['bet_com'] = struc_betDict[('sub-2013-C028', 'ses-1', 'anat')]['sub-2013-C028_ses-1_wemempr_1']['bet_com']
    niftiDict[key1][key2]['zcutoff'] = struc_betDict[key1][key2]['zcutoff']
    niprov.add(niftiDict[key1][key2]['brain_fname'])
    niprov.add(niftiDict[key1][key2]['mask_fname'])
    return niftiDict
