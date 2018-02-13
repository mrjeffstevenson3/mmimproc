# first set global root data directory
import pylabs
pylabs.datadir.target = 'jaba'
from pathlib import *
import nibabel as nib
import numpy as np
import pandas as pd
from dipy.io import read_bvals_bvecs
from dipy.core.gradients import gradient_table
from pylabs.io.images import savenii

from pylabs.utils import *
# project and subjects and files to run on
from pylabs.projects.acdc.file_names import project, SubjIdPicks, get_dwi_names
from pylabs.diffusion.dti_qc import dwi_qc_1bv
#set up provenance
prov = ProvenanceWrapper()
#setup paths and file names to process

fs = Path(getnetworkdataroot())

antsRegistrationSyN = get_antsregsyn_cmd()
slicer_path = getslicercmd()

# instantiate subject id list container
subjids_picks = SubjIdPicks()
# list of subject ids to operate on
picks = [
         {'subj': 'sub-acdc103', 'session': 'ses-1', 'run': '1',  # subject selection info
          'dwi_badvols': np.array([]), 'topup_badvols': np.array([]), 'topdn_badvols': np.array([]),  # remove bad vols identified in qc
          },
         ]

setattr(subjids_picks, 'subjids', picks)

qc_str = ''
hdf_fname = fs / project / 'all_acdc_info.h5'

topup_fnames, topdn_fnames, dwi_fnames = get_dwi_names(subjids_picks)

# make multiindex DF for results by subj/ses/ivol index and ['iact_dwi', ivol_dwi_qc, iact_topup, ivol_topup_qc, iact_topdn, ivol_topdn_qc] cols
for p in picks:
    pd.MultiIndex()


# for testing
i = 0
topup, topdn, dwif = topup_fnames[i], topdn_fnames[i], dwi_fnames[i]

for i, (topup, topdn, dwif) in enumerate(zip(topup_fnames, topdn_fnames, dwi_fnames)):
    subject = dwif.split('_')[0]
    session = dwif.split('_')[1]
    dwipath = fs / project / subject / session / 'dwi'
    orig_dwif_fname = dwipath / str(dwif + qc_str + '.nii')
    orig_dwi_bvals_fname = dwipath / str(dwif + qc_str + '.bvals')
    orig_dwi_bvecs_fname = dwipath / str(dwif + qc_str + '.bvecs')
    topup_fname = dwipath / str(topup + qc_str + '.nii')
    topdn_fname = dwipath / str(topdn + qc_str + '.nii')
    bvals, bvecs = read_bvals_bvecs(str(orig_dwi_bvals_fname), str(orig_dwi_bvecs_fname))
    gtab = gradient_table(bvals, bvecs)
    orig_dwi_data = nib.load(str(orig_dwif_fname)).get_data()
    orig_topup_data = nib.load(str(topup_fname)).get_data()
    orig_topdn_data = nib.load(str(topdn_fname)).get_data()
    affine = nib.load(str(orig_dwif_fname)).affine
    #for testing
    #b = np.unique(gtab.bvals)[1]
    output = dwipath / 'qc' / (subject+'_'+session+'_topdn_dwiqc')
    dwi_qc_1bv(orig_topdn_data, affine, output, hdf_fname, subject/session/'dwi_qc')
    all_topup_data = np.append(orig_dwi_data[:,:,:,0, None] , orig_topup_data, axis=3)
    output = dwipath / 'qc' / (subject+'_'+session+'_topup_dwiqc')
    dwi_qc_1bv(all_topup_data, affine, output, hdf_fname, subject/session/'dwi_qc')


    for b in np.unique(gtab.bvals):
        if b == 0:
            continue
        ixb = np.isin(gtab.bvals, b)
        select_vols = orig_dwi_data[:,:,:,np.where(ixb)[0]]
        output = dwipath / 'qc' / (subject+'_'+session+'_dwiqc_b' + str(int(b)))
        dwi_qc_1bv(select_vols, affine, output, hdf_fname, subject/session/'dwi_qc')

