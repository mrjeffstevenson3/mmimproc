# first set global root data directory
import pylabs
pylabs.datadir.target = 'jaba'
import os, cPickle
from pathlib import *
from collections import defaultdict
import nipype
from nipype.interfaces import fsl
import nibabel as nib
import numpy as np
from dipy.io import read_bvals_bvecs
from dipy.core.gradients import gradient_table
import shutil
import datetime
from cloud.serialization.cloudpickle import dumps
from scipy.ndimage.filters import median_filter as medianf
from pylabs.structural.brain_extraction import extract_brain
from pylabs.conversion.brain_convert import conv_subjs
from pylabs.conversion.nifti2nrrd import nii2nrrd
from pylabs.alignment.ants_reg import subj2templ_applywarp
from pylabs.correlation.atlas import mori_network_regions
from pylabs.io.images import savenii
from pylabs.utils import run_subprocess, WorkingContext, appendposix, replacesuffix
from pylabs.utils.paths import getnetworkdataroot, test4working_gpu, get_antsregsyn_cmd, MNI1mm_T2_brain, getslicercmd, \
        moriMNIatlas, MNI1mm_T1_brain
# project and subjects and files to run on
from pylabs.projects.acdc.file_names import project, SubjIdPicks, get_dwi_names
#set up provenance
from pylabs.utils.provenance import ProvenanceWrapper
prov = ProvenanceWrapper()
#setup paths and file names to process

fs = Path(getnetworkdataroot())

antsRegistrationSyN = get_antsregsyn_cmd()
slicer_path = getslicercmd()

# instantiate subject id list container
subjids_picks = SubjIdPicks()
# list of subject ids to operate on
picks = [
         {'subj': 'sub-acdc103', 'session': 'ses-1', 'run': '1',  # subject selection info
          'dwi_badvols': np.array([1, 3, 4, 5, 10, 53]), 'topup_badvols': np.array([]), 'topdn_badvols': np.array([]),  # remove bad vols identified in qc
          },
         ]

setattr(subjids_picks, 'subjids', picks)

#  define hostnames with working gpus for processing
flt = fsl.FLIRT(bins=640, interp='nearestneighbour', cost_func='mutualinfo', output_type='NIFTI_GZ')
if nipype.__version__ == '0.12.0':
    applyxfm = fsl.ApplyXfm(interp='nearestneighbour', output_type='NIFTI_GZ')
else:
    applyxfm = fsl.ApplyXFM(interp='nearestneighbour', output_type='NIFTI_GZ')

print(os.environ['FSLOUTPUTTYPE'])


topup_fnames, topdn_fnames, dwi_fnames = get_dwi_names(subjids_picks)
