import pylabs
pylabs.datadir.target = 'jaba'
import nibabel as nib
import numpy as np
from pylabs.utils import *
from pylabs.io.images import savenii
from pylabs.alignment.ants_reg import subj2T1, subj2templ_applywarp
from pylabs.structural.brain_extraction import extract_brain
from pylabs.fmap_correction.b1_map_corr import calcb1map
from scipy import stats
from scipy.ndimage.filters import median_filter as medianf
# project, subject, and file objects to work on
from pylabs.projects.genz.file_names import project, SubjIdPicks, get_vfa_names, Optsd, merge_ftempl_dicts
# set up provenance
prov = ProvenanceWrapper()
# setup paths and file names to process
fs = Path(getnetworkdataroot())
# instantiate opts and subject id list container
subjids_picks = SubjIdPicks()
opts = Optsd()
# must set fas mannually when patch used. not reported in PAR file correctly.
picks = [{'patch': True, 'project': project, 'subj': 'sub-genz501', 'session': 'ses-1', 'run': '1', 'fas': [4.0, 25.0],},
         ]
setattr(subjids_picks, 'subjids', picks)

vfa_picks =  get_vfa_names(subjids_picks)
opts.test = True
if opts.test:
    i = 0
    vfa_picks = [vfa_picks[i]]

# loop over subjects
for pick in vfa_picks:
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
        savenii(S2, b1_affine, ses_dir / 'qt1' / (pick['b1map_fname'] + '_tr2_mf_mag.nii'))
        b1map_brain, b1map_brain_mask, b1map_cropped = extract_brain(ses_dir / 'qt1' / (pick['b1map_fname'] + '_tr2_mf_mag.nii'), f_factor=0.4)
        b1map = calcb1map(S1, S2, pick['b1maptr'])
        b1map_out_fname = ses_dir/'fmap'/'{subj}_{session}_b1map_phase_mf.nii'.format(**pick)
        savenii(b1map, b1_affine, str(b1map_out_fname))

        # reg b1map and vfa and apply to mask
        subj2T1(b1map_brain, vfa_brain, appendposix(b1map_brain, '_reg2vfa_'))
        subj2templ_applywarp(b1map_out_fname, vfa_brain, appendposix(b1map_out_fname, '_reg2vfa'),
                             [appendposix(b1map_brain, '_reg2vfa_Warp1'),], '.',
                             affine_xform=[appendposix(b1map_brain, '_reg2vfa_Affine0')])

        # fit vfa and make b1corrected qt1 img
        vy_vfa2_ec1 = vfa_data[:,:,:,:2]
        vy_vfa2_ec2 = vfa_data[:,:,:,2:4]
        vy_vfa2_ec1_rms = np.sqrt(np.sum(np.square(vy_vfa2_ec1), axis=3)/vy_vfa2_ec1.shape[3])
        vy_vfa2_ec2_rms = np.sqrt(np.sum(np.square(vy_vfa2_ec2), axis=3)/vy_vfa2_ec2.shape[3])
        k = np.prod(vy_vfa2_ec1_rms.shape)
        data = np.zeros([len(pick['fas']), k])
        data[0,:] = vy_vfa2_ec1_rms.flatten()
        data[1,:] = vy_vfa2_ec2_rms.flatten()
        fa_uncorr = np.zeros(data.shape)
        fa_b1corr = np.zeros(data.shape)
        for i, fa in enumerate(pick['fas']):
            fa_uncorr[i, :] = fa
        fa_b1corr = fa_uncorr * b1map.flatten()  # uses broadcasting
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
        qT1_linregr_data = qT1_linregr.reshape(vy_vfa2_ec1_rms.shape)
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
