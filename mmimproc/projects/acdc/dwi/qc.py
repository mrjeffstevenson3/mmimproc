# assumes 3 shell dwi of 0, 800, 2000 with only 1 B0 as 1st vol
# first set global root data directory
import mmimproc
mmimproc.datadir.target = 'jaba'
from pathlib import *
import nibabel as nib
import numpy as np
import pandas as pd
from dipy.io import read_bvals_bvecs
from dipy.core.gradients import gradient_table
from mmimproc.io.mixed import df2h5
from mmimproc.io.images import savenii
from mmimproc.utils import *
from mmimproc.diffusion.dti_qc import dwi_qc_1bv
# project and subjects and files to run on
from mmimproc.projects.acdc.file_names import project, SubjIdPicks, get_dwi_names, Optsd

#set up provenance
prov = ProvenanceWrapper()
#setup paths and file names to process
# set up root data directory
fs = mmimproc.fs_local
# instantiate project level nomenclature options object
opts = Optsd()
opts.test = False
# instantiate subject id list object
subjids_picks = SubjIdPicks()
# list of dicts of subject ids and info to operate on
picks = [
         {'subj': 'sub-acdctest_jan17', 'session': 'ses-1', 'run': '1',},
         ]

setattr(subjids_picks, 'subjids', picks)

dwi_picks = get_dwi_names(subjids_picks)

# for testing
if opts.test:
    i = 0
    dwi_picks = [dwi_picks[i]]

for i, pick in enumerate(dwi_picks):
    orig_dwi_fname = pick['dwi_path'] / '{dwi_fname}.nii'.format(**pick)
    orig_dwi_bvals_fname = pick['dwi_path'] / '{dwi_fname}.bvals'.format(**pick)
    orig_dwi_bvecs_fname = pick['dwi_path'] / '{dwi_fname}.bvecs'.format(**pick)
    topup_fname = pick['dwi_path'] / '{topup_fname}.nii'.format(**pick)
    topdn_fname = pick['dwi_path'] / '{topdn_fname}.nii'.format(**pick)
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
    output_pname = pick['dwi_path'] / 'qc/{subj}_{session}_b800-qc'.format(**pick)
    b800_dwi_data = orig_dwi_data[:, :, :, gtab.bvals == b]
    b800_badvols = dwi_qc_1bv(b800_dwi_data, output_pname, alpha=opts.dwi_qc_b800_alpha)
    for i in range(b800_badvols.shape[0]):
        b800_badvols.loc[i, 'orig_dwi_idx'] = int(np.where(bvals == b)[0][i])
    b800_badvols['orig_dwi_idx'] = b800_badvols['orig_dwi_idx'].astype('int')
    b800_badvols.set_index('orig_dwi_idx', inplace=True)
    for v_idx, v_ser in enumerate(b800_badvols.iterrows()):
        qc_DF.loc[v_ser[0], 'auto_dwi_qc'] = b800_badvols.loc[v_ser[0], 1].astype('int')
        qc_DF.loc[v_ser[0], 'auto_dwi_vol_idx'] = v_idx

    b = 2000.0   # dwi qc
    output_pname = pick['dwi_path'] / 'qc/{subj}_{session}_b2000-qc'.format(**pick)
    b2000_dwi_data = orig_dwi_data[:, :, :, gtab.bvals == b]
    b2000_badvols = dwi_qc_1bv(b2000_dwi_data, output_pname, alpha=opts.dwi_qc_b2000_alpha)
    for i in range(b2000_badvols.shape[0]):
        b2000_badvols.loc[i, 'orig_dwi_idx'] = int(np.where(bvals == b)[0][i])
    b2000_badvols['orig_dwi_idx'] = b2000_badvols['orig_dwi_idx'].astype('int')
    b2000_badvols.set_index('orig_dwi_idx', inplace=True)
    for v_idx, v_ser in enumerate(b2000_badvols.iterrows()):
        qc_DF.loc[v_ser[0], 'auto_dwi_qc'] = b2000_badvols.loc[v_ser[0], 1]
        qc_DF.loc[v_ser[0], 'auto_dwi_vol_idx'] = v_idx

    # topup qc
    output_pname = pick['dwi_path'] / 'qc/{subj}_{session}_topup8b0-qc'.format(**pick)
    all_topup_data = np.append(orig_dwi_data[:, :, :, 0, None], orig_topup_data, axis=3)
    topup_badvols = dwi_qc_1bv(all_topup_data, output_pname, alpha=opts.dwi_qc_b0_alpha)
    qc_DF.loc[:(topup_badvols.shape[0] - 1), 'topup_qc'] = topup_badvols[1].values

    # topdown qc
    output_pname = pick['dwi_path'] / 'qc/{subj}_{session}_topdn7b0-qc'.format(**pick)
    topdn_badvols = dwi_qc_1bv(orig_topdn_data, output_pname, alpha=opts.dwi_qc_b0_alpha)
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

    # add mask of bad slices here: read in b800 and b2000 reports and set mask vol/slice to alpha value
    with open(str(fs / '{project}/{subj}/{session}/dwi/qc/{subj}_{session}_b2000-qc_report.txt'.format(**pick)), 'r') as qc_report:
        b2000_badvols = qc_report.read()
    with open(str(fs / '{project}/{subj}/{session}/dwi/qc/{subj}_{session}_b800-qc_report.txt'.format(**pick)), 'r') as qc_report:
        b800_badvols = qc_report.read()
    bad_vols_data = np.zeros(nib.load(str(pick['dwi_path']/(pick['dwi_fname']+'.nii'))).shape)
    for line in b2000_badvols.splitlines():
        if 'bad slice volume' in line:
            bad_vols_data[:, :, int(float(line.split()[4])) - 1, int(float(line.split()[5])) + np.sum(gtab.b0s_mask)] = float(line.split()[3])
    for line in b800_badvols.splitlines():
        if 'bad slice volume' in line:
            bad_vols_data[:, :, int(float(line.split()[4])) - 1, int(float(line.split()[5])) + np.sum(gtab.bvals == 2000) + np.sum(gtab.b0s_mask)] = float(line.split()[3])
    savenii(bad_vols_data, nib.load(str(pick['dwi_path']/(pick['dwi_fname']+'.nii'))).affine, '{dwi_path}/{dwi_fname}_badvols_mask.nii.gz'.format(**pick), minmax=(1,3))
