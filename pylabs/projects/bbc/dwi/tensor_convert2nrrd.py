import os, inspect
from pathlib import *
import numpy as np
import nibabel as nib
import niprov, pylabs
prov = niprov.ProvenanceContext()
from pylabs.projects.bbc.dwi.passed_qc import dwi_passed_qc, dwi_passed_101
from pylabs.utils.paths import getnetworkdataroot
from pylabs.utils import run_subprocess, WorkingContext
fs = Path(getnetworkdataroot())
pylabs_basepath = Path(*Path(inspect.getabsfile(pylabs)).parts[:-1])
project = 'bbc'
fname_templ = 'sub-bbc{sid}_ses-{snum}_{meth}_{runnum}'
dwi_fnames = [fname_templ.format(sid=str(s), snum=str(ses), meth=m, runnum=str(r)) for s, ses, m, r in dwi_passed_qc]

for dwif in dwi_fnames:
    ec_meth = 'cuda_repol_std2'
    dwipath = fs / project / dwif.split('_')[0] / dwif.split('_')[1] / 'dwi'
    fdwi_basen = dwif + '_eddy_corrected_repol_std2'
    mask_fname = dwipath / str(dwif + '_S0_brain_mask.nii')
    for m in ['WLS', 'OLS', 'RESTORE']:
        tenpath = dwipath / ec_meth / m
        if m == 'RESTORE':
            ten_fname = str(fdwi_basen + '_' + m.lower() + '_cam2fsl_tensor_medfilt.nii.gz'))

