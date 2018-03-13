#todo: finish writing qc results to df
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
# i = 0
# pick = dwi_picks[i]
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
    #affine = nib.load(str(orig_dwi_fname)).affine
    qc_DF = pd.DataFrame(data=gtab.bvecs, index=[range(len(gtab.bvals))], columns=['x_bvec', 'y_bvec', 'z_bvec'])
    qc_DF['bvals'] = gtab.bvals
    qc_DF.loc[:orig_topdn_data.shape[3], 'itopdn'] = range(orig_topdn_data.shape[3] + 1)
    qc_DF.loc[:orig_topup_data.shape[3], 'itopup'] = range(orig_topup_data.shape[3] + 1)
    qc_DF.loc[:orig_topup_data.shape[3]+1, 'alltopup_idx'] = range(orig_topup_data.shape[3] + 2)

    output_pname = dwipath / 'qc' / '_'.join([subject, session, 'b800-qc'])
    b800_dwi_data = orig_dwi_data[:, :, :, gtab.bvals == 800.0]
    b800_badvols = dwi_qc_1bv(b800_dwi_data, output_pname)

    output_pname = dwipath / 'qc' / '_'.join([subject, session, 'b2000-qc'])
    b2000_dwi_data = orig_dwi_data[:, :, :, gtab.bvals == 2000.0]
    b2000_badvols = dwi_qc_1bv(b2000_dwi_data, output_pname)

    output_pname = dwipath / 'qc' / '_'.join([subject, session, 'topup8b0-qc'])
    all_topup_data = np.append(orig_dwi_data[:, :, :, 0, None], orig_topup_data, axis=3)
    topup_badvols = dwi_qc_1bv(all_topup_data, output_pname)
    output_pname = dwipath / 'qc' / '_'.join([subject, session, 'topdn7b0-qc'])
    topdn_badvols = dwi_qc_1bv(orig_topdn_data, output_pname)

    #fill in qc results into df
    if topup_badvols.iloc[0,0] == 1:
        qc_DF.loc[0, 'dwi_qc'] = 1
    else:
        qc_DF.loc[0, 'dwi_qc'] = 0

    qc_DF.loc[:topdn_badvols.shape[0]-1, 'topdn_qc'] = topdn_badvols[1].values
    qc_DF.loc[:topup_badvols.shape[0]-1, 'topup_qc'] = topup_badvols[1].values
    # for b in np.unique(gtab.bvals):
    #     if b == 0:
    #         continue
    #     ixb = np.isin(gtab.bvals, b)
    #     select_vols = orig_dwi_data[:,:,:,np.where(ixb)[0]]
    #     output = dwipath / 'qc' / (subject+'_'+session+'_dwiqc_b' + str(int(b)))
    #     dwi_badvols = dwi_qc_1bv(select_vols, output)
    #     qc_DF.loc[ixb, 'dwi_qc'] = dwi_badvols[1].values
    #     try:
    #         jpg_out.rename(appendposix(output, '.jpg'))
    #     except OSError:
    #         print('dwi jpg file for b'+str(int(b))+' not found. moving on.')
    #     report_out.rename(appendposix(output, '_report.txt'))

    # write to hdf info file
    #qc_DF.to_hdf(str(info_fname), subject+'/'+session+'/dwi_qc', mode='a', append=False, format='t')