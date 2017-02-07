import os, inspect, copy
from pathlib import *
import datetime
import pylabs
from pylabs.correlation.atlas import make_mask_fm_atlas_parts, make_mask_fm_tracts
from pylabs.alignment.ants_reg import subj2templ_applywarp
from pylabs.projects.bbc.pairing import vbmpairing, dwipairing
from pylabs.utils.paths import getnetworkdataroot
from pylabs.utils import run_subprocess, WorkingContext
#set up provenance
from pylabs.utils.provenance import ProvenanceWrapper
provenance = ProvenanceWrapper()
#setup paths and file names to process
fs = Path(getnetworkdataroot())
pylabs_atlasdir = Path(*Path(inspect.getabsfile(pylabs)).parts[:-2]) / 'data' / 'atlases'
slicer_path = Path(*Path(inspect.getabsfile(pylabs)).parts[:-3]) / 'Slicer-4.5.0-2016-05-02-linux-amd64' / 'Slicer --launch '
fs_cmd = 'recon-all -openmp %(omp)s -subject %(sid)s -all'
overwrite=True
#set project specific files
project = 'bbc'
dwi_fnames = [dwi_templ.format(sid=str(s), snum=str(ses), meth=m, runnum=str(r)) for s, ses, m, r in dwipairing]
vbm_templ = 'sub-bbc{sid}_ses-{snum}_{meth}_{runnum}_brain_susan_nl_comroll'
vbm_fnames = [vbm_templ.format(sid=str(s), snum=str(ses), meth=m, runnum=str(r)) for s, ses, m, r in vbmpairing]
templdir = fs / project / 'reg' / 'ants_vbm_pairedLH_in_template_space'
vbm_statsdir = templdir / 'stats' / 'exchblks'
MNI2templ_invwarp = templdir / 'bbc_pairedLH_template_reg2MNI_1InverseWarp.nii.gz'
MNI2templ_aff = templdir / 'bbc_pairedLH_template_reg2MNI_0GenericAffine.mat'
dwi2vbmsubjdir = fs / project / 'reg' / 'reg_subFA2suborigvbmpaired_run2'
dwi_reg_append = '_eddy_corrected_repol_std2_wls_fsl_tensor_mf_FA_ero_reg2sorigvbm_'

for vbmf in vbm_fnames:
    subject = vbmf.split('_')[0]
    curr_env = copy.copy(os.environ)
    fssd = fs / project / vbmf.split('_')[0]
    vbmdir = fs / project / subject / vbmf.split('_')[1] / 'anat'
    run_subprocess(['recon-all', '-openmp', '%.0f' % mp, '-subject', subject, '-all'], env=this_env)