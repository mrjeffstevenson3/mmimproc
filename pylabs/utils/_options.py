from pylabs.utils.provenance import ProvenanceWrapper
import os


class PylabsOptions(object):
    """General settings for pylabs.

    Attributes:
        pthresh (float): 1 minus p value threshold for determining statistical significance. Default=0.95
        rthreshpos (float): minimum positive r value for plot display. Default=0.7
        rthreshneg (float): minimum negative r value for plot display. Default=-0.7
    """
    pthresh = 0.95
    rthreshpos = 0.7
    rthreshneg = -0.7
    niifiletype = '.nii.gz'
    orientation = 'LAS+'
    fsldir = str(os.environ.get('FSLDIR'))
