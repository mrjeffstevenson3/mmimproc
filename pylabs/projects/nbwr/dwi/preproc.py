import os, cPickle
from pathlib import *
from collections import defaultdict
from nipype.interfaces import fsl
import subprocess
from datetime import datetime
from cloud.serialization.cloudpickle import dumps
from pylabs.structural.brain_extraction import struc_bet
from pylabs.conversion.brain_convert import conv_subjs
from pylabs.utils.paths import getnetworkdataroot, getlocaldataroot
prov = ProvenanceWrapper()
flt = fsl.FLIRT(bins=640, interp='nearestneighbour', cost_func='mutualinfo', output_type='NIFTI')
applyxfm = fsl.ApplyXFM(output_type='NIFTI')
fs = Path(getnetworkdataroot())

project = 'nbwr'

niipickle = fs / project / 'nbwrniftiDict_all_subj_201605232241.pickle'
#stages to run
convert = True
run_topup = True
subT2 = False   #wip
eddy_corr = True

dti_qc = False
b1corr = False
bet = False
prefilter = False
templating = False

# subjects and files to run on
from pylabs.projects.nbwr.file_names import topup_fname, topdn_fname, dwi_fname

def default_to_regular(d):
    if isinstance(d, defaultdict):
        d = {k: default_to_regular(v) for k, v in d.iteritems()}
    return d

#run conversion if needed
# if convert:
#     niftiDict = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
#     niftiDict, niftiDF = conv_subjs(project, subjects, niftiDict)
# else:
#     with open(niipickle, 'rb') as f:
#         niftiDict = cPickle.load(f)

if run_topup:
    for i, (topup, topdn, dwif) in enumerate(zip(topup_fname, topdn_fname, dwi_fname)):
        dwipath = fs / project / dwif.split('_')[0] / dwif.split('_')[1] / 'dwi'
        ec_dir = dwipath / 'cuda_orig_v1'
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

        with open(str(topup_dwellt_fname), 'r') as tud:
            topup_dwellt = tud.read().replace('\n', '')

        with open(str(topdn_dwellt_fname), 'r') as tdd:
            topdn_dwellt = tdd.read().replace('\n', '')

        with open(str(infpath / 'acq_params.txt'), 'w') as f:
            f.write('0 1 0 ' + dwell)

        with open(str(infpath / 'index.txt'), 'w') as f:
            f.write('1 ' * len(gtab.bvals))




'''
acqparams.txt file

0 -1 0 0.062
0 -1 0 0.062
0 1 0 0.062
0 1 0 0.062
'''
