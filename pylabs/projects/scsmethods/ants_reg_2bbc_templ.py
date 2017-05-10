## for f in `ls orig_S0_in_subject_space/*.nii`; do antsRegistrationSyN.sh -d 3 -m $f -f bbc_pairedLH_template_invT2c_resampled2dwi.nii.gz -o `basename ${f/.nii/}`_reg2dwiT2template_ -n 30 -t s -p f -j 1 -s 10 -r 1; done

from pathlib import *
from pylabs.projects.bbc.pairing import fmri_fnames
from pylabs.utils.paths import getnetworkdataroot
from pylabs.utils import run_subprocess, WorkingContext, appendposix
#set up provenance
from pylabs.utils.provenance import ProvenanceWrapper
provenance = ProvenanceWrapper()
#setup paths and file names to process
fs = Path(getnetworkdataroot())

project = 'bbc'
source_data = 'self_control'
regdir = fs/project/'reg'/'ants_scsqT1_in_template_space'
templdir = fs/project/'reg'/'ants_vbm_pairedLH_in_template_space'
ref = templdir/'bbc_pairedLH_template_invT2c_resampled2fscsqT1.nii.gz'
qT1_fname_templ = 'orig_scs{sid}_qT1.nii'
subj_ids = []
qT1_fnames = [qT1_fname_templ.format(sid=s) for s in subj_ids]

if not regdir.is_dir():
    regdir.mkdir(Parents=True)

for qT1f in qT1_fnames:
    results = ()
    subjdir = fs / source_data / 'hbm_group_data' / 'qT1' / 'b_by_date'
    mov = subjdir/ qT1f
    out_fname = regdir/ appendposix(qT1f, '_reg2scsqT1T2template')
    with WorkingContext(str(regdir)):
        cmd = 'antsRegistrationSyN.sh -d 3 -m '+str(mov)+' -f '+str(ref)+' -o '+str(out_fname)
        cmd += ' -n 30 -t s -p f -j 1 -s 10 -r 1'
        results += run_subprocess(cmd)
