from pathlib import *
import numpy as np
import nibabel as nib
import nipype.interfaces.fsl as fsl
from pylabs.structural.brain_extraction import extract_brain
from pylabs.qt1.fitting import t1fit
from pylabs.utils.paths import getnetworkdataroot
from pylabs.utils import appendposix
from pylabs.projects.nbwr.file_names import project, spgr_fa5_fname, spgr_fa15_fname, spgr_fa30_fname, b1map_fname
from pylabs.utils.provenance import ProvenanceWrapper
prov = ProvenanceWrapper()

fs = Path(getnetworkdataroot())
flt = fsl.FLIRT(bins=640, interp='nearestneighbour', cost_func='mutualinfo', output_type='NIFTI')
applyxfm = fsl.ApplyXfm(output_type='NIFTI')

for b1map, spgr05, spgr15, spgr30 in zip(b1map_fname, spgr_fa5_fname, spgr_fa15_fname, spgr_fa30_fname):
    b1map_dir = fs/project/b1map.split('_')[0] / b1map.split('_')[1] / 'fmap'
    spgr_dir = fs/project/spgr30.split('_')[0] / spgr30.split('_')[1] / 'qt1'
    b1magcmd = 'fslroi '+str(b1map_dir/b1map)+'.nii '+str()
    b1phasecmd = 'fslroi '
