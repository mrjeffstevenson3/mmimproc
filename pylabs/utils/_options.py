from pylabs.utils.provenance import ProvenanceWrapper
import os


class PylabsOptions(object):
    """General settings for pylabs.

    Attributes:
        pthresh (float): 1 minus p value threshold for determining statistical significance. Default=0.95
        rthreshpos (float): minimum positive r value for plot display. Default=0.7
        rthreshneg (float): minimum negative r value for plot display. Default=-0.7
    """
    p_thresh = 0.95
    r_thresh_pos = 0.7
    r_thresh_neg = -0.7
    spm_seg_thr = 0.19
    nii_ftype = 'NIFTI_GZ'
    if nii_ftype == 'NIFTI_GZ':
        nii_fext = '.nii.gz'
    elif nii_ftype == 'NIFTI':
        nii_fext = '.nii'
    else:
        nii_fext = None
    fslmultifilequit = 'TRUE'
    orientation = 'LAS+'
    overwrite = False
    fsldir = str(os.environ.get('FSLDIR'))
