from pylabs.utils import Shell, paths
import subprocess
shell = Shell()

mpath = paths.getgannettpath()
act = '/mnt/users/js/tadpole/JONAH_DAY2/source_parrec/TADPOLE_PR20160804_WIP_GABAMM_TE80_120DYN_3_2_raw_act.SPAR'
ref = '/mnt/users/js/tadpole/JONAH_DAY2/source_parrec/TADPOLE_PR20160804_WIP_GABAMM_TE80_120DYN_3_2_raw_ref.SPAR'

mcode = "addpath('{0}'); MRS_struct = GannetLoad({{'{1}'}},{{'{2}'}}); MRS_struct = GannetFit(MRS_struct); exit;".format(
        mpath, act, ref)

cmd = 'matlab -nodisplay -nosplash -nodesktop -r "{0}"'.format(mcode)
subprocess.check_call(cmd, shell=True)
