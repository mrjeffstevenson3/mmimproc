import os, inspect, itertools
from pathlib import *
import numpy as np
import nibabel as nib
import pylabs
from scipy.ndimage.measurements import center_of_mass as com
from collections import defaultdict
from pylabs.alignment.affinematfile import FslAffineMat
from pylabs.alignment.ants_reg import fsl2ants_affine
from pylabs.projects.bbc.pairing import dwipairing
from pylabs.utils.paths import getnetworkdataroot
from pylabs.utils import run_subprocess, WorkingContext
from pylabs.io.images import savenii
from pylabs.utils.provenance import ProvenanceWrapper
provenance = ProvenanceWrapper()
fs = Path(getnetworkdataroot())
pylabs_basepath = Path(*Path(inspect.getabsfile(pylabs)).parts[:-1])
project = 'bbc'
#eddy corrected method directory. should get from eddy.
ec_meth = 'cuda_repol_std2_v2'
#fit methods to loop over
fitmeth = ['wls_dipy_mf_FA.nii', 'ols_dipy_mf_FA.nii', 'ols_fsl_tensor_mf_FA.nii.gz', 'wls_fsl_tensor_mf_FA.nii.gz']

fname_templ = 'sub-bbc{sid}_ses-{snum}_{meth}_{runnum}'
dwi_fnames = [fname_templ.format(sid=str(s), snum=str(ses), meth=m, runnum=str(r)) for s, ses, m, r in dwipairing]

#start here
com_vox = {}
diff_com = {}
mm_diff_com = {}
diff_offcenter2com = {}
com_affine = {}
subj2com = {}
for f in dwi_fnames:
    for m in fitmeth:
        infpath = fs / project / f.split('_')[0] / f.split('_')[1] / 'dwi' / ec_meth / m[0:3].upper()
        fdwi_basen = f + '_eddy_corrected_repol_std2_thr1_'
        nfname = infpath / str(fdwi_basen + m)
        img = nib.load(str(nfname))
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
        outdir = fs / project / 'reg' / str('FA_'+m.split('.')[0][0:-3]+'_template') / str(str(nfname.name).split('.')[0] + '_com.nii')
        savenii(img_data, np.array(com_affine[f]), outdir, header=hdr,  minmax=(0, 1))
        #add save matfile class call and save
        savematf = FslAffineMat()
        savematf.data = subj2comxfm
        savematf.saveAs(str(outdir).replace('.nii', '.mat'))
        fsl2ants_affine(execwdir=str(outdir.parent), ref=str(outdir), src=str(nfname),
                        fslmatfilename=str(outdir).replace('.nii', '.mat'))
