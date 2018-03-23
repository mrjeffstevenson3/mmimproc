# use all_topup_idx, topdn_idx, auto_dwi_vol_idx for mapping qc index to image vol index
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
from pylabs.diffusion.dti_qc import dwi_qc_1bv
# project and subjects and files to run on
from pylabs.projects.acdc.file_names import project, SubjIdPicks, get_dwi_names, Optsd

#set up provenance
prov = ProvenanceWrapper()
#setup paths and file names to process
# set up root data directory
fs = Path(getnetworkdataroot())
# instantiate project level nomenclature options object
opts = Optsd()
# instantiate subject id list object
subjids_picks = SubjIdPicks()
# list of dicts of subject ids and info to operate on
picks = [
         {'subj': 'sub-acdc112', 'session': 'ses-1', 'run': '1',  # subject selection info
          },
         ]

setattr(subjids_picks, 'subjids', picks)

dwi_picks = get_dwi_names(subjids_picks)

# for testing
if opts.test:
    i = 0
    dwi_picks = [dwi_picks[i]]

for i, pick in enumerate(dwi_picks):
    # read in data and prep results df
    subject = pick['subj']
    session = pick['session']
    dwif = pick['dwi_fname']
    topup = pick['topup_fname']
    topdn = pick['topdn_fname']
    dwipath = fs / project / subject / session / 'dwi'
    orig_dwi_fname = dwipath / '{dwi_fname}.nii'.format(**pick)
    orig_dwi_bvals_fname = dwipath / '{dwi_fname}.bvals'.format(**pick)
    orig_dwi_bvecs_fname = dwipath / '{dwi_fname}.bvecs'.format(**pick)
    topup_fname = dwipath / '{topup_fname}.nii'.format(**pick)
    topdn_fname = dwipath / '{topdn_fname}.nii'.format(**pick)
    bvals, bvecs = read_bvals_bvecs(str(orig_dwi_bvals_fname), str(orig_dwi_bvecs_fname))
    gtab = gradient_table(bvals, bvecs)
    orig_dwi_data = nib.load(str(orig_dwi_fname)).get_data()
    orig_topup_data = nib.load(str(topup_fname)).get_data()
    orig_topdn_data = nib.load(str(topdn_fname)).get_data()

    qc_DF = pd.DataFrame(data=gtab.bvecs, index=[range(len(gtab.bvals))], columns=['x_bvec', 'y_bvec', 'z_bvec'], dtype=np.float)
    qc_DF['bvals'] = gtab.bvals.astype('int')

    qc_DF.loc[:orig_topdn_data.shape[3] - 1, 'itopdn'] = np.arange(orig_topdn_data.shape[3], dtype=np.int).astype('int')
    qc_DF.loc[:orig_topup_data.shape[3] - 1, 'itopup'] = np.arange(orig_topup_data.shape[3], dtype=np.int)
    qc_DF.loc[:orig_topup_data.shape[3], 'alltopup_idx'] = np.arange(orig_topup_data.shape[3] + 1, dtype=np.int)
    qc_DF.loc[0, 'dwi_fname'] = orig_dwi_fname
    qc_DF.loc[0, 'topup_fname'] = topup_fname
    qc_DF.loc[0, 'topdn_fname'] = topdn_fname

    # start 3 shell dwi hardi
    b = 800.0   # dwi qc
    output_pname = dwipath / 'qc' / '{subj}_{session}_b800-qc'.format(**pick)
    b800_dwi_data = orig_dwi_data[:, :, :, gtab.bvals == b]
    b800_badvols = dwi_qc_1bv(b800_dwi_data, output_pname)
    for i in range(b800_badvols.shape[0]):
        b800_badvols.loc[i, 'orig_dwi_idx'] = int(np.where(bvals == b)[0][i])
    b800_badvols['orig_dwi_idx'] = b800_badvols['orig_dwi_idx'].astype('int')
    b800_badvols.set_index('orig_dwi_idx', inplace=True)
    for v_idx, v_ser in enumerate(b800_badvols.iterrows()):
        qc_DF.loc[v_ser[0], 'auto_dwi_qc'] = b800_badvols.loc[v_ser[0], 1].astype('int')
        qc_DF.loc[v_ser[0], 'auto_dwi_vol_idx'] = v_idx

    b = 2000.0   # dwi qc
    output_pname = dwipath / 'qc' / '{subj}_{session}_b2000-qc'.format(**pick)
    b2000_dwi_data = orig_dwi_data[:, :, :, gtab.bvals == b]
    b2000_badvols = dwi_qc_1bv(b2000_dwi_data, output_pname)
    for i in range(b2000_badvols.shape[0]):
        b2000_badvols.loc[i, 'orig_dwi_idx'] = int(np.where(bvals == b)[0][i])
    b2000_badvols['orig_dwi_idx'] = b2000_badvols['orig_dwi_idx'].astype('int')
    b2000_badvols.set_index('orig_dwi_idx', inplace=True)
    for v_idx, v_ser in enumerate(b2000_badvols.iterrows()):
        qc_DF.loc[v_ser[0], 'auto_dwi_qc'] = b2000_badvols.loc[v_ser[0], 1]
        qc_DF.loc[v_ser[0], 'auto_dwi_vol_idx'] = v_idx

    # topup qc
    output_pname = dwipath / 'qc' / '{subj}_{session}_topup8b0-qc'.format(**pick)
    all_topup_data = np.append(orig_dwi_data[:, :, :, 0, None], orig_topup_data, axis=3)
    topup_badvols = dwi_qc_1bv(all_topup_data, output_pname)
    qc_DF.loc[:(topup_badvols.shape[0] - 1), 'topup_qc'] = topup_badvols[1].values

    # topdown qc
    output_pname = dwipath / 'qc' / '{subj}_{session}_topdn7b0-qc'.format(**pick)
    topdn_badvols = dwi_qc_1bv(orig_topdn_data, output_pname)
    qc_DF.loc[:(topdn_badvols.shape[0] - 1), 'topdn_qc'] = topdn_badvols[1].values

    #fill in dwi b0 qc results into df
    if topup_badvols.iloc[0,0] == 1:
        qc_DF.loc[0, 'auto_dwi_qc'] = 1
    else:
        qc_DF.loc[0, 'auto_dwi_qc'] = 0
    qc_DF.loc[0, 'auto_dwi_vol_idx'] = 0
    # write results to project info hdf file
    intcols = [u'bvals', u'itopup', u'alltopup_idx', u'topup_qc', u'itopdn', u'topdn_qc', u'auto_dwi_vol_idx', u'auto_dwi_qc']
    qc_DF[intcols] = qc_DF[intcols].fillna(-9999).astype('int')
    qc_DF.replace({-9999: 'NaN'})
    cols = [u'x_bvec', u'y_bvec', u'z_bvec'] + intcols + ['dwi_fname', 'topup_fname', 'topdn_fname']
    qc_DF = qc_DF[cols]
    df2h5(qc_DF.reset_index(level=0), opts.info_fname, '/{subj}/{session}/dwi/auto_qc'.format(**pick), append=False)

