import pylabs
from pathlib import *
import nibabel as nib
import numpy as np
from pylabs.utils import *
from pylabs.io.images import savenii, loadStack
from pylabs.alignment.ants_reg import subj2T1, subj2templ_applywarp
from pylabs.structural.brain_extraction import extract_brain
from pylabs.fmap_correction.b1_map_corr import calcb1map
from scipy import stats
from scipy.ndimage.filters import median_filter as medianf
# project, subject, and file objects to work on
from pylabs.projects.scs.file_names import project, SubjIdPicks, get_spgr_names, Optsd, merge_ftempl_dicts
# set up provenance
prov = ProvenanceWrapper()
# setup paths and file names to process
fs = Path('/media/DiskArray/shared_data/js/')
# instantiate opts and subject id list container
opts = Optsd()

subjids_picks = SubjIdPicks()
# must set fas mannually when patch used. not reported in PAR file correctly.
picks = [
        {'subjnum': 317, 'subj': 'SCS_317',},

         ]
setattr(subjids_picks, 'subjids', picks)

spgr_picks = get_spgr_names(subjids_picks)

opts.test = True
if opts.test:
    i = 0
    spgr_picks = [spgr_picks[i]]

# loop over subjects
for pick in spgr_picks:
    ses_dir = fs/'{project}/scs{subjnum}'.format(**pick)
    b1_data = nib.load(str(pick['b1map_fname'])).get_data().astype(np.float64)
    b1_affine = nib.load(str(pick['b1map_fname'])).affine
    spgrs, spgr_affine = loadStack([str(pick['spgr_02_fname']), str(pick['spgr_10_fname']), str(pick['spgr_20_fname'])])
    if not (ses_dir/'qt1').is_dir():
        Path(ses_dir/'qt1').mkdir(parents=True)
    with WorkingContext(ses_dir/'qt1'):
        spgr20_brain, spgr20_brain_mask, spgr20_cropped = extract_brain(str(pick['spgr_20_fname']), f_factor=0.25)

        # calc b1map
        S1 = medianf(b1_data[:,:,:,0], size=7)
        S2 = medianf(b1_data[:,:,:,1], size=7)
        b1map = calcb1map(S1, S2, pick['b1maptr'])
        b1map_out_fname = ses_dir/'fmap'/'scs{subjnum}_b1map_phase_mf.nii'.format(**pick)
        savenii(b1map, b1_affine, str(b1map_out_fname))
        savenii(S2, b1_affine, appendposix(pick['b1map_fname'], '_mag120_mf'))
        b1map120_brain, b1map120_brain_mask, b1map120_cropped = extract_brain(appendposix(pick['b1map_fname'], '_mag120_mf'), f_factor=0.6)

        # reg b1map and spgr and apply to mask
        subj2T1(b1map120_brain, spgr20_brain, replacesuffix(b1map120_brain, '_reg2spgr_'))
        subj2templ_applywarp(b1map_out_fname, spgr20_brain, appendposix(b1map_out_fname, '_reg2spgr'),
                             [str(appendposix(b1map120_brain, '_reg2spgr_1Warp')),], '.',
                             affine_xform=[str(replacesuffix(b1map120_brain, '_reg2spgr_0GenericAffine.mat')),])
        reg_b1map = nib.load(str(appendposix(b1map_out_fname, '_reg2spgr'))).get_data().astype(np.float64)

        # fit 3 flip angle spgr and make b1corrected qt1 img

        k = np.prod(spgrs.shape[1:4])
        data = np.zeros([len(pick['fas']), k])
        data[0, :] = spgrs[0,:,:,:].flatten()
        data[1, :] = spgrs[1,:,:,:].flatten()
        data[2, :] = spgrs[2,:,:,:].flatten()
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
        mask = nib.load(str(b1map120_brain_mask)).get_data().astype('bool').flatten()
        for v in range(k):
            if mask[v]:
                m[v], intercept, r, p, std = stats.linregress(x[:, v], y[:, v])
        qT1_linregr = -pick['spgrtr'][0]/np.log(m)
        qT1_linregr_data = qT1_linregr.reshape(spgrs.shape[1:4])
        qT1_linregr_data[np.logical_or(qT1_linregr_data < 1.0, ~np.isfinite(qT1_linregr_data))] = 0
        qT1_linregr_data[qT1_linregr_data > 6000] = 6000
        qT1_linregr_data_clean = np.nan_to_num(qT1_linregr_data, copy=True)
        pick['mod'] = 'qt1'
        qt1out_fname = ses_dir/'qt1'/'scs{subjnum}_spgr_{mod}_b1corrmf_vlinregr-fit_clamped.nii'.format(**pick)
        savenii(qT1_linregr_data_clean, spgr_affine, str(qt1out_fname))
        pick['mod'] = 'R1'
        qt1out_fname = ses_dir/'qt1'/'scs{subjnum}_spgr_{mod}_b1corrmf_vlinregr-fit_clamped.nii'.format(**pick)
        with np.errstate(divide='ignore', invalid='ignore'):
            R1 = np.true_divide(1.0, qT1_linregr_data_clean)
            R1[ ~ np.isfinite(R1)] = 0
            R1 = R1 * 1000.0
            savenii(R1, spgr_affine, str(qt1out_fname), minmax=(0,1))
