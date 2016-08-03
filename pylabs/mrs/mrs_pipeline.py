from pylabs.utils._run import Shell
import subprocess
shell = Shell()

mpath = '/home/mrjeffs/Software/gannett_spectro/Gannet2/Gannet2.0-master'
act = '/mnt/users/js/tadpole/JONA_DAY1/TADPOLE_PR20160803_WIP_GABAMM_TE80_120DYN_3_2_raw_act.SDAT'
ref = '/mnt/users/js/tadpole/JONA_DAY1/TADPOLE_PR20160803_WIP_GABAMM_TE80_120DYN_3_2_raw_ref.SDAT'

mcode = "addpath('{0}'); MRS_struct = GannetLoad({{'{1}'}},{{'{2}'}}); MRS_struct = GannetFit(MRS_struct); exit;".format(
        mpath, act, ref)

cmd = 'matlab -nodisplay -nosplash -nodesktop -r "{0}"'.format(mcode)
subprocess.check_call(cmd, shell=True)
