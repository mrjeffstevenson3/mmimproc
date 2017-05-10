## for f in `ls orig_S0_in_subject_space/*.nii`; do antsRegistrationSyN.sh -d 3 -m $f -f bbc_pairedLH_template_invT2c_resampled2dwi.nii.gz -o `basename ${f/.nii/}`_reg2dwiT2template_ -n 30 -t s -p f -j 1 -s 10 -r 1; done

from pathlib import *
from pylabs.projects.bbc.pairing import fmri_fnames
from pylabs.utils.paths import getnetworkdataroot
from pylabs.utils import run_subprocess, WorkingContext
#set up provenance
from pylabs.utils.provenance import ProvenanceWrapper
provenance = ProvenanceWrapper()
#setup paths and file names to process
fs = Path(getnetworkdataroot())

project = 'bbc'
regdir = fs/project/'reg'/'ants_fmri_in_template_space'
templdir = fs/project/'reg'/'ants_vbm_pairedLH_in_template_space'
ref = templdir/'bbc_pairedLH_template_invT2c_resampled2fmri.nii.gz'

if not regdir.is_dir():
    regdir.mkdir(Parents=True)

for fmri in fmri_fnames:
    results = ()
    subjdir = fs / project / fmri.split('_')[0] / fmri.split('_')[1] / 'fmri' / fmri.replace('.nii', '.feat')
    mov = subjdir/'example_func.nii.gz'
    out_fname = regdir/ fmri.replace('.nii', '_reg2fmriT2template_')
    with WorkingContext(str(regdir)):
        cmd = 'antsRegistrationSyN.sh -d 3 -m '+str(mov)+' -f '+str(ref)+' -o '+str(out_fname)
        cmd += ' -n 30 -t s -p f -j 1 -s 10 -r 1'
        results += run_subprocess(cmd)
