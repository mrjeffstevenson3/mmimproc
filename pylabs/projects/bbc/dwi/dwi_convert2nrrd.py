import os, inspect
from pathlib import *
import niprov, pylabs
prov = niprov.ProvenanceContext()
from pylabs.projects.bbc.pairing import dwipairing
from pylabs.utils.paths import getnetworkdataroot
from pylabs.conversion.nifti2nrrd import nii2nrrd
fs = Path(getnetworkdataroot())
pylabs_basepath = Path(*Path(inspect.getabsfile(pylabs)).parts[:-1])
project = 'bbc'
ec_meth = 'cuda_repol_std2_v2'
fname_templ = 'sub-bbc{sid}_ses-{snum}_{meth}_{runnum}'
dwi_fnames = [fname_templ.format(sid=str(s), snum=str(ses), meth=m, runnum=str(r)) for s, ses, m, r in dwipairing]

for dwif in dwi_fnames:
    dwipath = fs / project / dwif.split('_')[0] / dwif.split('_')[1] / 'dwi'
    fdwi_basen = dwif + '_eddy_corrected_repol_std2'
    infpath = dwipath / ec_meth
    fdwi_basen = dwif + '_eddy_corrected_repol_std2'
    fdwi = infpath / str(fdwi_basen + '_thr1.nii.gz')
    fbvecs = infpath / str(fdwi_basen + '.eddy_rotated_bvecs')
    fbvals = dwipath / str(dwif + '.bvals')
    mask_fname = dwipath / str(dwif + '_S0_brain_mask.nii')
    nii2nrrd(fdwi, dwipath / str(fdwi_basen + '_thr1.nhdr'), bvalsf=fbvals, bvecsf=fbvecs)


