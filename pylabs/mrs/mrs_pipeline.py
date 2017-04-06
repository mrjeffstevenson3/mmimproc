from pylabs.utils import Shell, paths, InDir
import os, subprocess
from pylabs.utils import run_subprocess, WorkingContext
from pathlib import *
from os.path import join
from pylabs.utils.paths import getnetworkdataroot
fs = Path(getnetworkdataroot())
project = 'nbwr'
subject = 'sub-nbwr999b'
rt_actfname = 'NWBR999B_WIP_RTGABAMM_TE80_120DYN_5_2_raw_act.SPAR'
rt_reffname = 'NWBR999B_WIP_RTGABAMM_TE80_120DYN_5_2_raw_ref.SPAR'
lt_actfname = 'NWBR999B_WIP_LTPRESS_TE80_GLU_48MEAS_9_2_raw_act.SPAR'
lt_reffname = 'NWBR999B_WIP_LTPRESS_TE80_GLU_48MEAS_9_2_raw_ref.SPAR'
source_path = fs / project / subject / 'ses-1' / 'source_parrec'
results_dir = fs / project / subject / 'ses-1' / 'mrs'

if not source_path.is_dir():
    raise ValueError('source_parrec dir with mrs SPAR not found. '+str(source_path))

if not results_dir.is_dir():
    results_dir.mkdir(parents=True)

shell = Shell()


mpath = paths.getgannettpath()
act = source_path / rt_actfname
ref = source_path / rt_reffname

mcode = "addpath('{0}'); MRS_struct = GannetLoad({{'{1}'}},{{'{2}'}}); MRS_struct = GannetFit(MRS_struct); exit;".format(
        mpath, str(act), str(ref))

cmd = 'matlab -nodisplay -nosplash -nodesktop -r "{0}"'.format(mcode)
with WorkingContext(str(results_dir)):
    subprocess.check_call(cmd, shell=True)

