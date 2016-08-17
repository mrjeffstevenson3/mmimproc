import os, niprov, cPickle
from os.path import join
import numpy as np
from collections import defaultdict
from datetime import datetime
from pylabs.utils.paths import getnetworkdataroot, getlocaldataroot
#prov = niprov.ProvenanceContext()
fs = getnetworkdataroot()
project = 'bbc'
niipickle = join(fs, project, 'bbc_niftiDict_all_subj_201608021057.pickle')
fpath = join(fs, project, 'myvbm', 'ants_vbm_template')
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
for f in fname:
    subject = f.split('_')[0]
    session = f.split('_')[1]
    offsets[f] = niftiDict[(subject, session, 'anat')][f]['orig_affine'][:3,3]

median_offsets = np.median(offsets.values(), axis=0, keepdims=True)

diff_affine = {}
for f in fname:
    subject = f.split('_')[0]
    session = f.split('_')[1]
    diff = niftiDict[(subject, session, 'anat')][f]['orig_affine'][:3, 3] - median_offsets
    diff_affine[f] = np.zeros((4,4))
    for i in range(3):
        diff_affine[f][i][3]= diff[0][i]

new_affine = {}
for f in fname:
    subject = f.split('_')[0]
    session = f.split('_')[1]
    new_affine[f] = np.array(niftiDict[(subject, session, 'anat')][f]['orig_affine']) + diff_affine[f]

for f in fname:
    nfname = join(fpath, fname + '_brain_susan_nl.nii.gz')
    subject = f.split('_')[0]
    session = f.split('_')[1]
    oimg = nibabel.load(nfname)
    ohdr = oimg.header
    oaffine = oimg.get_affine()
    assert np.allclose(niftiDict[(subject, session, 'anat')][fname]['orig_affine'], oaffine), 'affines are not the same'
    zooms = ohdr.get_zooms()
    xyzroll = [int(round(diff_affine[fname[0]][i, 3] / z)) for i, z in enumerate(hdr.get_zooms())]
