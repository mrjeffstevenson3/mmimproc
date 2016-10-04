import os, cPickle
from os.path import join
import numpy as np
from scipy.ndimage.measurements import center_of_mass as com
import nibabel
from collections import defaultdict
from pylabs.utils.paths import getnetworkdataroot
from pylabs.utils import run_subprocess
from pylabs.alignment.affinematfile import FslAffineMat
from pylabs.utils.provenance import ProvenanceWrapper
prov = ProvenanceWrapper()
fs = getnetworkdataroot()

#should move to bbc proj now that it works
project = 'bbc'
niipickle = join(fs, project, 'bbc_niftiDict_all_subj_201608021057.pickle')
fpath = join(fs, project, 'myvbm', 'ants_vbm_template', 'orig_vbm')
subtemplate = 'sub-bbc{sid}'
subjid = [101, 105, 106, 108, 113, 116, 118, 119, 120, 202, 208, 209, 211, 212, 215, 218, 219, 231, 236, 241, 243, 249, 252, 253]
#pairedsid = [101, 209, 105, 211, 106, 208, 108, 202, 113, 249, 116, 241, 118, 243, 119, 231, 120, 253]
sespassqc = []
for i in range(len(subjid)):
    if i != 7 and i != 12 and i != 13:
        sespassqc = sespassqc[:i] + [1]
    elif i == 12 or i == 13:
        sespassqc = sespassqc[:i] + [2]
    elif i == 7:
        sespassqc = sespassqc[:i] + [3]
methodpassqc = []
for i in range(len(subjid)):
    if i == 5:
        methodpassqc = methodpassqc[:i] + ['wempr']
    else:
        methodpassqc = methodpassqc[:i] + ['mpr']
runpassqc = []
for i in range(len(subjid)):
    if i != 0 and i != 6 and i != 14 and i != 19:
        runpassqc = runpassqc[:i] + [1]
    elif i == 6 or i == 14 or i == 19:
        runpassqc = runpassqc[:i] + [2]
    elif i == 0:
        runpassqc = runpassqc[:i] + [3]
fname_templ = 'sub-bbc{sid}_ses-{snum}_{meth}_{runnum}'
fname = [fname_templ.format(sid=str(s), snum=str(ses), meth=m, runnum=str(r)) for s, ses, m, r in zip(subjid, sespassqc, methodpassqc, runpassqc)]

with open(niipickle, 'rb') as f:
        niftiDict = cPickle.load(f)
#end of bbc specific setup start of function
#def com2center(niftiDict, filelist, indir=None, outdir=None)

#may not need anymore
offsets = {}
offcenter = {}
for f in fname:
    subject = f.split('_')[0]
    session = f.split('_')[1]
    offsets[f] = niftiDict[(subject, session, 'anat')][f]['orig_affine'][:3,3]
    offcenter[f] = niftiDict[(subject, session, 'anat')][f]['off_center']  #note y coord [0] index is inverted per philips
#reorder offcenter to xyz with y in RAS coord system eg A is positive
for k, v in offcenter.items():
    offcenter[k] = np.asarray([v[2], -v[0], v[1]])
#start here
com_vox = {}
diff_com = {}
mm_diff_com = {}
diff_offcenter2com = {}
com_affine = {}
subj2com = {}
for f in fname:
    nfname = join(fpath, f + '_brain_susan_nl.nii.gz')
    subject = f.split('_')[0]
    session = f.split('_')[1]
    img = nibabel.load(nfname)
    hdr = img.header
    img_data = img.get_data()
    affine = img.affine
    zooms = hdr.get_zooms()
    com_vox[f] = np.round(com(img_data)).astype(int)
    diff_com[f] = np.asarray([s / 2. - c for s, c in zip(img_data.shape, com_vox[f])])
    mm_diff_com[f] = np.asarray([d * z for d, z in zip(diff_com[f], zooms)])
    subj2comxfm = np.eye(4)
    for i, t in enumerate(mm_diff_com[f]):
        affine[i][3] = affine[i][3] + t
        subj2comxfm[i][3] = t
    com_affine[f] = affine
    subj2com[f] = subj2comxfm
    for i, r in enumerate(diff_com[f]):
        img_data = np.roll(img_data, int(r), axis=i)
    nimg = nibabel.nifti1.Nifti1Image(img_data, np.array(com_affine[f]), hdr)
    nhdr = nimg.header
    nhdr.set_qform(com_affine[f], code=1)
    nhdr.set_sform(com_affine[f], code=1)
    # assert np.allclose(nhdr.get_qform(), new_affine[f], 4), 'qform and new affine do not match for ' + f
    nibabel.save(nimg, join(fpath, f + '_brain_susan_nl_com2center.nii.gz'))
    #add save matfile class call and save
    savematf = FslAffineMat()
    savematf.data = subj2comxfm
    savematf.saveAs(join(fpath, f + '_brain_susan_nl_com2center.mat'))
    cmd = 'c3d_affine_tool -ref ' + join(fpath, f + '_brain_susan_nl_com2center.nii.gz') + ' -src '
    cmd += nfname + ' ' + join(fpath, f + '_brain_susan_nl_com2center.mat') + ' -fsl2ras -oitk '
    cmd += join(fpath, f + '_brain_susan_nl_com2center.txt')
    run_subprocess(cmd)

