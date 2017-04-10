import os, cPickle
from pathlib import *
from collections import defaultdict
from nipype.interfaces import fsl
import nibabel as nib
import numpy as np
import subprocess
from datetime import datetime
from cloud.serialization.cloudpickle import dumps
from pylabs.structural.brain_extraction import struc_bet
from pylabs.conversion.brain_convert import conv_subjs
from pylabs.io.images import loadStack
from pylabs.utils import run_subprocess, WorkingContext
from pylabs.utils.paths import getnetworkdataroot
# prov = ProvenanceWrapper()
flt = fsl.FLIRT(bins=640, interp='nearestneighbour', cost_func='mutualinfo', output_type='NIFTI')
applyxfm = fsl.ApplyXFM(output_type='NIFTI')
fs = Path(getnetworkdataroot())

project = 'nbwr'

niipickle = fs / project / 'nbwrniftiDict_dev_subj999b_201704101132.pickle'
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
        nib.save(topup_dn_concat_img, str(dwipath / str(topup + '_topdn_concat.nii')))
        cmd = 'topup --imain='+str(dwipath / str(topup + '_topdn_concat.nii'))
        cmd += ' --datain=acq_params.txt --config=b02b0.cnf --out='
        cmd += str(dwipath / str(topup + '_topdn_concat_unwarped.nii'))
        result = ()
        with WorkingContext(str(dwipath)):
            result = run_subprocess(cmd)


        # with open(str(dwipath / 'index.txt'), 'w') as f:
        #     f.write('1 ' * len(gtab.bvals))
        #

