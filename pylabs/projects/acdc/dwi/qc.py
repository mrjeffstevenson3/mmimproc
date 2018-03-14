#todo: fix index floats to int
# first set global root data directory
import pylabs
pylabs.datadir.target = 'jaba'
from pathlib import *
import nibabel as nib
import numpy as np
import pandas as pd
from dipy.io import read_bvals_bvecs
from dipy.core.gradients import gradient_table
from pylabs.io.mixed import df2h5
from pylabs.utils import *
# project and subjects and files to run on
from pylabs.projects.acdc.file_names import project, SubjIdPicks, get_dwi_names, Opts
from pylabs.diffusion.dti_qc import dwi_qc_1bv
#set up provenance
prov = ProvenanceWrapper()
#setup paths and file names to process

fs = Path(getnetworkdataroot())

antsRegistrationSyN = get_antsregsyn_cmd()
slicer_path = getslicercmd()
opts = Opts()
qc_str = opts.dwi_pass_qc
# instantiate subject id list object
subjids_picks = SubjIdPicks()
# list of dicts of subject ids and info to operate on
picks = [
         {'subj': 'sub-acdc117', 'session': 'ses-1', 'run': '1',  # subject selection info
          'dwi_badvols': np.array([]), 'topup_badvols': np.array([]), 'topdn_badvols': np.array([]),  # remove bad vols identified in qc
          },
         ]

setattr(subjids_picks, 'subjids', picks)


dwi_picks = get_dwi_names(subjids_picks)

# for testing
#i = 0
#pick = dwi_picks[i]
#topup, topdn, dwif = topup_fnames[i], topdn_fnames[i], dwi_fnames[i]

for i, pick in enumerate(dwi_picks):
    # read in data and prep results df
    subject = pick['subj']
    session = pick['session']
    dwif = pick['dwi_fname']
    topup = pick['topup_fname']
    topdn = pick['topdn_fname']
    dwipath = fs / project / subject / session / 'dwi'
    orig_dwi_fname = dwipath / str(dwif + '.nii')
    orig_dwi_bvals_fname = dwipath / str(dwif + '.bvals')
    orig_dwi_bvecs_fname = dwipath / str(dwif + '.bvecs')
    topup_fname = dwipath / str(topup + '.nii')
    topdn_fname = dwipath / str(topdn + '.nii')
    bvals, bvecs = read_bvals_bvecs(str(orig_dwi_bvals_fname), str(orig_dwi_bvecs_fname))
    gtab = gradient_table(bvals, bvecs)
    orig_dwi_data = nib.load(str(orig_dwi_fname)).get_data()
    orig_topup_data = nib.load(str(topup_fname)).get_data()
    orig_topdn_data = nib.load(str(topdn_fname)).get_data()
    col_dtyps = {'x_bvec': np.float, 'y_bvec': np.float, 'z_bvec': np.float, 'bvals': np.int, 'itopdn': np.int, 'itopup': np.int, 'alltopup_idx': np.int,
                 'auto_dwi_qc': np.int, 'topup_qc': np.int, 'topdn_qc': np.int,}
    qc_DF = pd.DataFrame(columns=pd.Index(col_dtyps.keys()), dtype='int64')
    for k, v in col_dtyps.iteritems():
        qc_DF[k] = qc_DF[k].astype(v)
    qc_DF = pd.DataFrame(data=gtab.bvecs, index=[range(len(gtab.bvals))], columns=['x_bvec', 'y_bvec', 'z_bvec'], dtype=np.float)
    qc_DF['bvals'] = gtab.bvals.astype('int')

    qc_DF.loc[:orig_topdn_data.shape[3], 'itopdn'] = np.arange(orig_topdn_data.shape[3] + 1, dtype=np.int).astype('int')
    qc_DF.loc[:orig_topup_data.shape[3], 'itopup'] = np.arange(orig_topup_data.shape[3] + 1, dtype=np.int)
    qc_DF.loc[:orig_topup_data.shape[3] + 1, 'alltopup_idx'] = np.arange(orig_topup_data.shape[3] + 2, dtype=np.int)

    b = 800.0
    output_pname = dwipath / 'qc' / '{subj}_{session}_b800-qc'.format(**pick)
    b800_dwi_data = orig_dwi_data[:, :, :, gtab.bvals == b]
    b800_badvols = dwi_qc_1bv(b800_dwi_data, output_pname)
    for i in range(b800_badvols.shape[0]):
        b800_badvols.loc[i, 'orig_dwi_idx'] = int(np.where(bvals == b)[0][i])
    b800_badvols['orig_dwi_idx'] = b800_badvols['orig_dwi_idx'].astype('int')
    b800_badvols.set_index('orig_dwi_idx', inplace=True)
    for i in b800_badvols.iterrows():
        qc_DF.loc[i[0], 'auto_dwi_qc'] = b800_badvols.loc[i[0], 1]

    b = 2000.0
    output_pname = dwipath / 'qc' / '{subj}_{session}_b2000-qc'.format(**pick)
    b2000_dwi_data = orig_dwi_data[:, :, :, gtab.bvals == b]
    b2000_badvols = dwi_qc_1bv(b2000_dwi_data, output_pname)
    for i in range(b2000_badvols.shape[0]):
        b2000_badvols.loc[i, 'orig_dwi_idx'] = int(np.where(bvals == b)[0][i])
    b2000_badvols['orig_dwi_idx'] = b2000_badvols['orig_dwi_idx'].astype('int')
    b2000_badvols.set_index('orig_dwi_idx', inplace=True)
    # append cmd
    for i in b2000_badvols.iterrows():
        qc_DF.loc[i[0], 'auto_dwi_qc'] = b2000_badvols.loc[i[0], 1]

    output_pname = dwipath / 'qc' / '{subj}_{session}_topup8b0-qc'.format(**pick)
    all_topup_data = np.append(orig_dwi_data[:, :, :, 0, None], orig_topup_data, axis=3)
    topup_badvols = dwi_qc_1bv(all_topup_data, output_pname)
    qc_DF.loc[:topup_badvols.shape[0] - 1, 'topup_qc'] = topup_badvols[1].values
    output_pname = dwipath / 'qc' / '{subj}_{session}_topdn7b0-qc'.format(**pick)
    topdn_badvols = dwi_qc_1bv(orig_topdn_data, output_pname)
    qc_DF.loc[:topdn_badvols.shape[0] - 1, 'topdn_qc'] = topdn_badvols[1].values

    #fill in dwi b0 qc results into df
    if topup_badvols.iloc[0,0] == 1:
        qc_DF.loc[0, 'auto_dwi_qc'] = 1
    else:
        qc_DF.loc[0, 'auto_dwi_qc'] = 0
    df2h5(qc_DF.reset_index(level=0), opts.info_fname, '/{subj}/{session}/dwi/auto_qc'.format(**pick), append=False)

