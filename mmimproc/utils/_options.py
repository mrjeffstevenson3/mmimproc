import mmimproc
import os


class MmimprocOptions(object):
    """General settings for mmimproc.

    Attributes:
        pthresh (float): 1 minus p value threshold for determining statistical significance. Default=0.95
        rthreshpos (float): minimum positive r value for plot display. Default=0.7
        rthreshneg (float): minimum negative r value for plot display. Default=-0.7
    """
    verbose = True
    init_verbose = False
    p_thresh = 0.95
    r_thresh_pos = 0.7
    r_thresh_neg = -0.7
    spm_seg_thr = 0.5
    nii_ftype = 'NIFTI_GZ'
    if nii_ftype == 'NIFTI_GZ':
        nii_fext = '.nii.gz'
    elif nii_ftype == 'NIFTI':
        nii_fext = '.nii'
    else:
        nii_fext = None
    fslmultifilequit = 'FALSE'
    orientation = 'LAS+'
    overwrite = False
    fsldir = str(os.environ.get('FSLDIR'))
    # seconds to wait before retry access to h5 file
    h5wait_interval = 30
    # total h5 access wait time about 5 min else something is wrong
    max_intervals = 10
