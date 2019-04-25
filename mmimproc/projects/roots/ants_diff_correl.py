import os
from os.path import join
from collections import defaultdict
import nibabel
import nibabel.nifti1 as nifti1
import numpy as np
from mmimproc.alignment.ants_reg import subj2templ_applywarp as reg2templ
from mmimproc.utils.paths import getlocaldataroot, getnetworkdataroot
from mmimproc.conversion.brain_convert import conv_subjs
from mmimproc.utils.provenance import ProvenanceWrapper
prov = ProvenanceWrapper()
prov.dryrun = True
prov.verbose = True
convert = False
fs = getnetworkdataroot()
#fs = getlocaldataroot()
project = 'roots_of_empathy'
workdir = 'ants_diff_correlations/FA'
sub_nmbrs = [28, 29, 30, 37, 53, 65]
diff_mods = ['FA', 'RA', 'MD', 'F2']
subjname_templ = 'sub-2013-C0{sub_nmbr}'
diff_fname_templ = '{subj_name}_nomo_mf_{diff_mod}_clamped.nii.gz'
sub_names = [str(subjname_templ).format(sub_nmbr=x) for x in sub_nmbrs]
FA_fnames = [str(diff_fname_templ).format(subj_name=x, diff_mod=diff_mods[0]) for x in sub_names]
nonFA_fnames = [str(diff_fname_templ).format(subj_name=x, diff_mod=y) for x in sub_names for y in diff_mods[1:]]
FA2T1_warp_fnm_templ = '{subj_name}_FA_reg2T1_1Warp.nii.gz'
FA2T1_affine_templ = '{subj_name}_FA_reg2T1_0GenericAffine.mat'
warpfname1_templ = 'T1we_susanthr200{subj_name}_ses-{ses}_wemempr_{run}_rms_b1corr_brain_susan200Warp.nii.gz'
affinefname_templ = 'T1we_susanthr200{subj_name}_ses-{ses}_wemempr_{run}_rms_b1corr_brain_susan200Affine.txt'
reffname_templ = 'T1we_susanthr200{subj_name}_ses-{ses}_wemempr_{run}_rms_b1corr_brain_susan200deformed.nii.gz'

imgdict = defaultdict(lambda: defaultdict(list))
a = [('sub-2013-C028_ses-1_wemempr_1_rms_b1corr_brain_susan200.nii.gz', {'zcutoff': 90, 'outfile': 'sub-2013-C028_ses-1_wemempr_1_rms_b1corr_brain_susan200_zcrop.nii.gz'}),
     ('sub-2013-C030_ses-1_wemempr_1_rms_b1corr_brain_susan200.nii.gz', {'zcutoff': 100, 'outfile': 'sub-2013-C030_ses-1_wemempr_1_rms_b1corr_brain_susan200_zcrop.nii.gz'}),
     ('sub-2013-C053_ses-1_wemempr_1_rms_b1corr_brain_susan200.nii.gz', {'zcutoff': 101, 'outfile': 'sub-2013-C053_ses-1_wemempr_1_rms_b1corr_brain_susan200_zcrop.nii.gz'}),
     ('sub-2013-C029_ses-2_wemempr_1_rms_b1corr_brain_susan200.nii.gz', {'zcutoff': 114, 'outfile': 'sub-2013-C029_ses-2_wemempr_1_rms_b1corr_brain_susan200_zcrop.nii.gz'}),
     ('sub-2013-C037_ses-1_wemempr_1_rms_b1corr_brain_susan200.nii.gz', {'zcutoff': 106, 'outfile': 'sub-2013-C037_ses-1_wemempr_1_rms_b1corr_brain_susan200_zcrop.nii.gz'}),
     ('sub-2013-C065_ses-1_wemempr_1_rms_b1corr_brain_susan200.nii.gz', {'zcutoff': 90, 'outfile': 'sub-2013-C065_ses-1_wemempr_1_rms_b1corr_brain_susan200_zcrop.nii.gz'})]
for i in a:
    imgdict[join(fs, project, workdir, 'T1', i[0])] = i[1]


if convert:
    niftiDict = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    niftiDict, niftiDF = conv_subjs(project, sub_names, niftiDict)
# else:
#     with open(join(fs, project, 'niftiDict_all_subj_201605181335.pickle'), 'rb') as f:
#         niftiDict = cPickle.load(f)


for i in imgdict:
    t1_img = nibabel.load(i)
    t1_hdr = t1_img.header
    t1_affine = t1_img.affine
    t1_data = np.array(t1_img.dataobj)
    t1_data_zcrop = t1_data
    t1_data_zcrop[:,:,0:int(imgdict[i]['zcutoff'])] = 0
    outfilename = join(fs, project, workdir, 'T1', imgdict[i]['outfile'])
    nimg = nifti1.Nifti1Image(t1_data_zcrop, t1_affine, t1_hdr)
    nibabel.save(nimg, outfilename)



