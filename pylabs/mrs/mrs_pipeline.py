from pylabs.utils import Shell, paths, InDir
import os, subprocess
from os.path import join
from pylabs.utils.paths import getnetworkdataroot
fs = getnetworkdataroot()
project = 'tadpole'
subject = 'JONAH_DAY2'
actfname = 'TADPOLE_PR20160804_WIP_GABAMM_TE80_120DYN_3_2_raw_act.SDAT'
reffname = 'TADPOLE_PR20160804_WIP_GABAMM_TE80_120DYN_3_2_raw_ref.SDAT'

shell = Shell()

try:
    os.makedirs(join(fs, project, subject, 'mrs'))
except OSError:
    if not os.path.isdir(join(fs, project, subject, 'mrs')):
        raise
tempdir = InDir(join(fs, project, subject, 'mrs'))

mpath = paths.getgannettpath()
act = join(fs, project, subject, 'source_parrec', actfname)
ref = join(fs, project, subject, 'source_parrec', reffname)

mcode = "addpath('{0}'); MRS_struct = GannetLoad({{'{1}'}},{{'{2}'}}); MRS_struct = GannetFit(MRS_struct); exit;".format(
        mpath, act, ref)

cmd = 'matlab -nodisplay -nosplash -nodesktop -r "{0}"'.format(mcode)
tempdir.__enter__()
subprocess.check_call(cmd, shell=True)
os.chdir(tempdir._orig_dir)
