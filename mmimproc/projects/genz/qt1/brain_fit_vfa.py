import mmimproc
mmimproc.datadir.target = 'jaba'
import nibabel as nib
import numpy as np
from mmimproc.utils import *
from mmimproc.io.images import savenii
from mmimproc.alignment.ants_reg import subj2T1, subj2templ_applywarp
from mmimproc.structural.brain_extraction import extract_brain
from mmimproc.fmap_correction.b1_map_corr import calcb1map
from scipy import stats
from scipy.ndimage.filters import median_filter as medianf
# project, subject, and file objects to work on
from mmimproc.projects.genz.file_names import project, SubjIdPicks, get_vfa_names, Optsd, merge_ftempl_dicts
# set up provenance
prov = ProvenanceWrapper()
# setup paths and file names to process
fs = mmimproc.fs
# instantiate opts and subject id list container
subjids_picks = SubjIdPicks()
opts = Optsd()
# must set fas mannually when patch used. not reported in PAR file correctly.
picks = [
        # {'patch': True, 'project': project, 'subj': 'sub-genz102', 'session': 'ses-1', 'run': '1', 'fas': [4.0, 25.0],},
        # {'patch': True, 'project': project, 'subj': 'sub-genz103', 'session': 'ses-1', 'run': '1', 'fas': [4.0, 25.0],},
        # {'patch': True, 'project': project, 'subj': 'sub-genz104', 'session': 'ses-1', 'run': '1', 'fas': [4.0, 25.0],},
        # {'patch': True, 'project': project, 'subj': 'sub-genz105', 'session': 'ses-1', 'run': '1', 'fas': [4.0, 25.0],},
        # {'patch': True, 'project': project, 'subj': 'sub-genz106', 'session': 'ses-1', 'run': '1', 'fas': [4.0, 25.0],},
        # {'patch': True, 'project': project, 'subj': 'sub-genz201', 'session': 'ses-1', 'run': '1', 'fas': [4.0, 25.0],},
        # {'patch': True, 'project': project, 'subj': 'sub-genz202', 'session': 'ses-1', 'run': '1', 'fas': [4.0, 25.0],},
        # {'patch': True, 'project': project, 'subj': 'sub-genz203', 'session': 'ses-1', 'run': '1', 'fas': [4.0, 25.0],},
        ## {'patch': True, 'project': project, 'subj': 'sub-genz204', 'session': 'ses-1', 'run': '1', 'fas': [4.0, 25.0],},
        {'patch': True, 'project': project, 'subj': 'sub-genz205', 'session': 'ses-1', 'run': '1', 'fas': [4.0, 25.0],},
        {'patch': True, 'project': project, 'subj': 'sub-genz208', 'session': 'ses-1', 'run': '1', 'fas': [4.0, 25.0],},
        {'patch': True, 'project': project, 'subj': 'sub-genz209', 'session': 'ses-1', 'run': '1', 'fas': [4.0, 25.0],},
        {'patch': True, 'project': project, 'subj': 'sub-genz211', 'session': 'ses-1', 'run': '1', 'fas': [4.0, 25.0],},
        # #{'patch': True, 'project': project, 'subj': 'sub-genz301', 'session': 'ses-2', 'run': '1', 'fas': [4.0, 25.0],},
        {'patch': True, 'project': project, 'subj': 'sub-genz302', 'session': 'ses-1', 'run': '1', 'fas': [4.0, 25.0],},
        {'patch': True, 'project': project, 'subj': 'sub-genz303', 'session': 'ses-1', 'run': '1', 'fas': [4.0, 25.0],},
        {'patch': True, 'project': project, 'subj': 'sub-genz304', 'session': 'ses-1', 'run': '1', 'fas': [4.0, 25.0],},
        {'patch': True, 'project': project, 'subj': 'sub-genz305', 'session': 'ses-1', 'run': '1', 'fas': [4.0, 25.0],},
        {'patch': True, 'project': project, 'subj': 'sub-genz306', 'session': 'ses-1', 'run': '1', 'fas': [4.0, 25.0],},
        #{'patch': True, 'project': project, 'subj': 'sub-genz307', 'session': 'ses-1', 'run': '1', 'fas': [4.0, 25.0],},
        {'patch': True, 'project': project, 'subj': 'sub-genz308', 'session': 'ses-1', 'run': '1', 'fas': [4.0, 25.0],},
        {'patch': True, 'project': project, 'subj': 'sub-genz310', 'session': 'ses-1', 'run': '1', 'fas': [4.0, 25.0],},
        {'patch': True, 'project': project, 'subj': 'sub-genz311', 'session': 'ses-1', 'run': '1', 'fas': [4.0, 25.0],},
        {'patch': True, 'project': project, 'subj': 'sub-genz312', 'session': 'ses-1', 'run': '1', 'fas': [4.0, 25.0],},
        {'patch': True, 'project': project, 'subj': 'sub-genz313', 'session': 'ses-1', 'run': '1', 'fas': [4.0, 25.0],},
        {'patch': True, 'project': project, 'subj': 'sub-genz315', 'session': 'ses-1', 'run': '1', 'fas': [4.0, 25.0],},
        {'patch': True, 'project': project, 'subj': 'sub-genz401', 'session': 'ses-1', 'run': '1', 'fas': [4.0, 25.0],},
        {'patch': True, 'project': project, 'subj': 'sub-genz402', 'session': 'ses-1', 'run': '1', 'fas': [4.0, 25.0],},
        {'patch': True, 'project': project, 'subj': 'sub-genz404', 'session': 'ses-1', 'run': '1', 'fas': [4.0, 25.0],},
        {'patch': True, 'project': project, 'subj': 'sub-genz408', 'session': 'ses-1', 'run': '1', 'fas': [4.0, 25.0],},
        {'patch': True, 'project': project, 'subj': 'sub-genz410', 'session': 'ses-1', 'run': '1', 'fas': [4.0, 25.0],},
        {'patch': True, 'project': project, 'subj': 'sub-genz501', 'session': 'ses-1', 'run': '1', 'fas': [4.0, 25.0],},
        {'patch': True, 'project': project, 'subj': 'sub-genz502', 'session': 'ses-1', 'run': '1', 'fas': [4.0, 25.0],},
        {'patch': True, 'project': project, 'subj': 'sub-genz503', 'session': 'ses-1', 'run': '1', 'fas': [4.0, 25.0],},
        {'patch': True, 'project': project, 'subj': 'sub-genz504', 'session': 'ses-1', 'run': '1', 'fas': [4.0, 25.0],},
        {'patch': True, 'project': project, 'subj': 'sub-genz505', 'session': 'ses-1', 'run': '1', 'fas': [4.0, 25.0],},
        {'patch': True, 'project': project, 'subj': 'sub-genz506', 'session': 'ses-1', 'run': '1', 'fas': [4.0, 25.0],},
        {'patch': True, 'project': project, 'subj': 'sub-genz508', 'session': 'ses-1', 'run': '1', 'fas': [4.0, 25.0],},
        {'patch': True, 'project': project, 'subj': 'sub-genz510', 'session': 'ses-1', 'run': '1', 'fas': [4.0, 25.0],},
         ]
setattr(subjids_picks, 'subjids', picks)

vfa_picks =  get_vfa_names(subjids_picks)
opts.test = False
if opts.test:
    i = 0
    vfa_picks = [vfa_picks[i]]

# loop over subjects
for pick in vfa_picks:
    print('working on {project}/{subj}/{session}'.format(**pick))
    ses_dir = fs/'{project}/{subj}/{session}'.format(**pick)
    b1_data = nib.load(str(ses_dir/'fmap'/pick['b1map_fname'])+'.nii').get_data().astype(np.float64)
    b1_affine = nib.load(str(ses_dir/'fmap'/pick['b1map_fname'])+'.nii').affine
    vfa_data = nib.load(str(ses_dir/'qt1'/pick['vfa_fname'])+'.nii').get_data().astype(np.float64)
    vfa_affine = nib.load(str(ses_dir/'qt1'/pick['vfa_fname'])+'.nii').affine
    savenii(vfa_data[:, :, :, 2], vfa_affine, ses_dir / 'qt1' / (pick['vfa_fname'] + '_fa25ec1.nii'))
    vfa_brain, vfa_brain_mask, vfa_cropped = extract_brain(ses_dir / 'qt1' / (pick['vfa_fname'] + '_fa25ec1.nii'), f_factor=0.25)
    with WorkingContext(ses_dir/'qt1'):
        # calc b1map
        S1 = medianf(b1_data[:,:,:,0], size=7)
        S2 = medianf(b1_data[:,:,:,1], size=7)
        b1map = calcb1map(S1, S2, pick['b1maptr'])
        b1map_out_fname = ses_dir/'fmap'/'{subj}_{session}_b1map_phase_mf.nii'.format(**pick)
        savenii(b1map, b1_affine, str(b1map_out_fname))
        savenii(S2, b1_affine, pick['b1map_fname'] + '_tr2_mf_mag.nii')
        b1map_brain, b1map_brain_mask, b1map_cropped = extract_brain(pick['b1map_fname'] + '_tr2_mf_mag.nii', f_factor=0.6)

        # reg b1map and vfa and apply to mask
        subj2T1(b1map_brain, vfa_brain, replacesuffix(b1map_brain, '_reg2vfa_'))
        subj2templ_applywarp(b1map_out_fname, vfa_brain, appendposix(b1map_out_fname, '_reg2vfa'),
                             [str(appendposix(b1map_brain, '_reg2vfa_1Warp')),], '.',
                             affine_xform=[str(replacesuffix(b1map_brain, '_reg2vfa_0GenericAffine.mat')),])
        reg_b1map = nib.load(str(appendposix(b1map_out_fname, '_reg2vfa'))).get_data().astype(np.float64)

        # fit 2 echo 2 flip angle vfa and make b1corrected qt1 img
        vfa_fa1 = vfa_data[:, :, :, :2]
        vfa_fa2 = vfa_data[:, :, :, 2:4]
        vfa_fa1_rms = np.sqrt(np.mean(np.square(vfa_fa1), axis=3))
        vfa_fa2_rms = np.sqrt(np.mean(np.square(vfa_fa2), axis=3))
        k = np.prod(vfa_fa1_rms.shape)
        data = np.zeros([len(pick['fas']), k])
        data[0, :] = vfa_fa1_rms.flatten()
        data[1, :] = vfa_fa2_rms.flatten()
        fa_uncorr = np.zeros(data.shape)
        fa_b1corr = np.zeros(data.shape)
        for i, fa in enumerate(pick['fas']):
            fa_uncorr[i, :] = fa
        fa_b1corr = fa_uncorr * reg_b1map.flatten()  # uses broadcasting
        fa_b1corr[fa_b1corr == np.inf] = np.nan
        fa_b1corr_rad = np.radians(fa_b1corr)
        y = data / np.sin(fa_b1corr_rad)
        x = data / np.tan(fa_b1corr_rad)
        m = np.zeros(k)
        mask = nib.load(str(vfa_brain_mask)).get_data().astype('bool').flatten()
        for v in range(k):
            if mask[v]:
                m[v], intercept, r, p, std = stats.linregress(x[:, v], y[:, v])
        qT1_linregr = -pick['vfatr'][0]/np.log(m)
        qT1_linregr_data = qT1_linregr.reshape(vfa_fa1_rms.shape)
        qT1_linregr_data[np.logical_or(qT1_linregr_data < 1.0, ~np.isfinite(qT1_linregr_data))] = 0
        qT1_linregr_data[qT1_linregr_data > 6000] = 6000
        qT1_linregr_data_clean = np.nan_to_num(qT1_linregr_data, copy=True)
        pick['mod'] = 'qt1'
        qt1out_fname = ses_dir/'qt1'/'{subj}_{session}_vfa_{mod}_b1corrmf_vlinregr-fit_clamped.nii'.format(**pick)
        savenii(qT1_linregr_data_clean, vfa_affine, str(qt1out_fname))
        pick['mod'] = 'R1'
        qt1out_fname = ses_dir/'qt1'/'{subj}_{session}_vfa_{mod}_b1corrmf_vlinregr-fit_clamped.nii'.format(**pick)
        with np.errstate(divide='ignore', invalid='ignore'):
            R1 = np.true_divide(1.0, qT1_linregr_data_clean)
            R1[ ~ np.isfinite(R1)] = 0
            R1 = R1 * 1000.0
            savenii(R1, vfa_affine, str(qt1out_fname), minmax=(0,1))
