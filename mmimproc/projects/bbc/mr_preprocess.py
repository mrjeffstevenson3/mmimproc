import os, cPickle
from os.path import join
from collections import defaultdict
from nipype.interfaces import fsl
import subprocess
from datetime import datetime
from mmimproc.structural.brain_extraction import struc_bet
from mmimproc.conversion.brain_convert import conv_subjs
from mmimproc.utils.paths import getnetworkdataroot, getlocaldataroot
prov = ProvenanceWrapper()
flt = fsl.FLIRT(bins=640, interp='nearestneighbour', cost_func='mutualinfo', output_type='NIFTI')
applyxfm = fsl.ApplyXFM(output_type='NIFTI')
fs = getnetworkdataroot()
project = 'bbc'
subtemplate = 'sub-bbc{sid}'
subjid = [101, 105, 106, 108, 109, 113, 116, 118, 119, 120, 202, 208, 209, 211, 212, 215, 218, 219, 231, 236, 241, 243, 249, 252, 253]
subjects = [subtemplate.format(sid=str(s)) for s in subjid]
#subjects = ['sub-bbc105']

niipickle = join(fs, project, 'bbcniftiDict_all_subj_201605232241.pickle')
#stages to run
convert = True
dti_qc = False
b1corr = False
bet = False
prefilter = False
templating = False

def default_to_regular(d):
    if isinstance(d, defaultdict):
        d = {k: default_to_regular(v) for k, v in d.items()}
    return d

#run conversion if needed
if convert:
    niftiDict = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    niftiDict, niftiDF = conv_subjs(project, subjects, niftiDict)
else:
    with open(niipickle, 'rb') as f:
        niftiDict = cPickle.load(f)

if dti_qc:
    print('dti qc runs here.')

#todo: make h5 file write to save data
niftidict = default_to_regular(niftiDict)
# with open(join(fs, project, "bbc_niftiDict_all_subj_{:%Y%m%d%H%M}.pickle".format(datetime.now())), "wb") as f:
#     f.write(dumps(niftiDict))
# with open(join(fs, project, "bbc_niftidict_all_subj_{:%Y%m%d%H%M}.pickle".format(datetime.now())), "wb") as f:
#     f.write(dumps(niftidict))
