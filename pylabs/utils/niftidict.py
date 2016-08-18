import os, niprov, cPickle
from os.path import join
import numpy as np
from scipy import spatial
import nibabel
from collections import defaultdict
from datetime import datetime
from pylabs.utils.paths import getnetworkdataroot, getlocaldataroot
#prov = niprov.ProvenanceContext()
fs = getnetworkdataroot()
orig = np.asarray([0, 0, 0])
project = 'bbc'
niipickle = join(fs, project, 'bbc_niftiDict_all_subj_201608021057.pickle')
fpath = join(fs, project, 'myvbm', 'ants_vbm_template', 'orig_vbm')
subtemplate = 'sub-bbc{sid}'
subjid = [101, 105, 106, 108, 113, 116, 118, 119, 120, 202, 208, 209, 211, 212, 215, 218, 219, 231, 236, 241, 243, 249, 252, 253]
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
    if i != 5 and i != 16:
        methodpassqc = methodpassqc[:i] + ['mpr']
    elif i == 5 or i == 16:
        methodpassqc = methodpassqc[:i] + ['wempr']
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
offsets = {}
offcenter = {}

for f in fname:
    subject = f.split('_')[0]
    session = f.split('_')[1]
    offsets[f] = niftiDict[(subject, session, 'anat')][f]['orig_affine'][:3,3]
    offcenter[f] = niftiDict[(subject, session, 'anat')][f]['off_center']  #note y coord [0] index is inverted per philips

min_offcenter = np.asarray(offcenter.values())[spatial.KDTree(np.asarray(offcenter.values())).query(orig)[1]]
target_midkey = [key for key, value in offcenter.items() if np.array_equal(np.asarray(value), min_offcenter)][0]
target_outkey = (target_midkey.split('_')[0], target_midkey.split('_')[1], 'anat')
tfname = join(fpath, target_midkey + '_brain_susan_nl.nii.gz')
target_img = nibabel.load(tfname)
target_hdr = target_img.header
target_shape = target_img.shape
target_zooms = target_hdr.get_zooms()

diff_affine = {}
diff_offcenter = {}
for f in fname:
    subject = f.split('_')[0]
    session = f.split('_')[1]
    diffa = niftiDict[(subject, session, 'anat')][f]['orig_affine'][:3, 3] - median_offsets
    diff_affine[f] = np.zeros((4,4))
    for i in range(3):
        diff_affine[f][i][3]= diffa[0][i]
    diffo = niftiDict[(subject, session, 'anat')][f]['off_center'] - median_offcenter
    diff_offcenter[f] = [o - m for o, m in zip(offcenter[f], median_offcenter)]

new_affine = {}
for f in fname:
    subject = f.split('_')[0]
    session = f.split('_')[1]
    new_affine[f] = np.array(niftiDict[(subject, session, 'anat')][f]['orig_affine']) - diff_affine[f]

for f in fname:
    nfname = join(fpath, f + '_brain_susan_nl.nii.gz')
    subject = f.split('_')[0]
    session = f.split('_')[1]
    oimg = nibabel.load(nfname)
    ohdr = oimg.header
    oaffine = oimg.affine
    assert np.allclose(niftiDict[(subject, session, 'anat')][f]['orig_affine'], oaffine, 6), 'affines are not the same for ' + f
    xyzroll = [int(round(diff_affine[f][i, 3] / z)) for i, z in enumerate(ohdr.get_zooms())]
    oimg_data = oimg.get_data()
    rimg_data = oimg_data
    for i, r in enumerate(xyzroll):
        if r > 0:
            rimg_data = np.roll(rimg_data, r, axis=i)
        if r < 0:
            rimg_data = np.roll(rimg_data, rimg_data.shape[i] - r, axis=i)

    nimg = nibabel.nifti1.Nifti1Image(rimg_data, np.array(new_affine[f]), ohdr)
    nhdr = nimg.header
    nhdr.set_qform(new_affine[f], code=1)
    nhdr.set_sform(new_affine[f], code=1)
    #assert np.allclose(nhdr.get_qform(), new_affine[f], 4), 'qform and new affine do not match for ' + f
    nibabel.save(nimg, join(fpath, f + '_brain_susan_nl_medroll.nii.gz'))
