import pylabs

from pathlib import *
import nibabel as nib
import numpy as np
import pandas as pd
from pylabs.io.spar import load as readspar
from pylabs.io.images import savenii
from pylabs.utils import ProvenanceWrapper, run_subprocess, WorkingContext, getnetworkdataroot, appendposix, replacesuffix
prov = ProvenanceWrapper()
fs = Path(getnetworkdataroot())

def make_voi_mask(spar_fname, matching_image_fname, out_voi_mask_fname):
    spar = readspar(str(spar_fname))
    match_img = nib.load(str(matching_image_fname))
    match_img_data = match_img.get_data()
    affine = match_img.affine
    mask_img = np.zeros(match_img_data.shape, dtype='int32')
    lr_diff = round((spar['lr_size'] / 2.) / match_img.header.get_zooms()[0])
    ap_diff = round((spar['ap_size'] / 2.) / match_img.header.get_zooms()[1])
    cc_diff = round((spar['cc_size'] / 2.) / match_img.header.get_zooms()[2])
    startx = int((match_img_data.shape[0] / 2.0) - lr_diff)
    endx = int((match_img_data.shape[0] / 2.0) + lr_diff)
    starty = int((match_img_data.shape[1] / 2.0) - ap_diff)
    endy = int((match_img_data.shape[1] / 2.0) + ap_diff)
    startz = int((match_img_data.shape[2] / 2.0) - cc_diff)
    endz = int((match_img_data.shape[2] / 2.0) + cc_diff)
    mask_img[startx:endx, starty:endy, startz:endz] = 1
    savenii(mask_img, affine, str(out_voi_mask_fname))
    prov.log(str(out_voi_mask_fname), 'binary voi mask file created for tissue fractions by make_voi_mask fn', str(spar_fname), script=__file__)
    return mask_img

def calc_tissue_fractions(voi_mask_fname, gm_seg_fname, wm_seg_fname, csf_seg_fname, region, method='SPM', thresh=0.0):
    subj = voi_mask_fname.parts[-4]
    mask_img_data = nib.load(str(voi_mask_fname)).get_data().astype(int)
    gm_seg_data = nib.load(str(gm_seg_fname)).get_data()
    gm_seg_data = np.where(gm_seg_data > thresh, gm_seg_data, 0)
    gm_voi = gm_seg_data * mask_img_data
    gm_num_vox = np.count_nonzero(gm_voi)
    wm_seg_data = nib.load(str(wm_seg_fname)).get_data()
    wm_seg_data = np.where(wm_seg_data > thresh, wm_seg_data, 0)
    wm_voi = wm_seg_data * mask_img_data
    wm_num_vox = np.count_nonzero(wm_voi)
    csf_seg_data = nib.load(str(csf_seg_fname)).get_data()
    csf_seg_data = np.where(csf_seg_data > thresh, csf_seg_data, 0)
    csf_voi = csf_seg_data * mask_img_data
    csf_num_vox = np.count_nonzero(csf_voi)
    mask_num_vox = float(np.count_nonzero(mask_img_data))
    results_d = {
        'subject': subj,
        'region': region,
        'frac_GM': gm_num_vox / mask_num_vox,
        'frac_WM': wm_num_vox / mask_num_vox,
        'frac_CSF': csf_num_vox / mask_num_vox,
        'method': method,
        'threshold': thresh,
        }
    results = pd.Series(results_d)
    return results
