from pylabs.utils._run import Shell
import subprocess
shell = Shell()

#mpath = '/home/toddr/Software/gannett_spectro/Gannet2/Gannet2.0-master'
#act = '/media/DiskArray/shared_data/js/tadpole/TADPOLE_999A/SPARSDAT/TADPOLE_999A_WIP_AM_GABA_21_2_raw_act.SDAT'
#ref = '/media/DiskArray/shared_data/js/tadpole/TADPOLE_999A/SPARSDAT/TADPOLE_999A_WIP_AM_GABA_21_2_raw_ref.SDAT'
mpath = '/Users/mrjeffs/Software/Gannet2.0-master'
#act = '/Users/mrjeffs/data/tadpole/TADPOLE_998B/SPARSDAT/TADPOLE_998b_WIP_GABA_MACRO_TE80_1P9_1P5_23MSPULSE_128N_9_2_raw_act.SDAT'
#ref = '/Users/mrjeffs/data/tadpole/TADPOLE_998B/SPARSDAT/TADPOLE_998b_WIP_GABA_MACRO_TE80_1P9_1P5_23MSPULSE_128N_9_2_raw_ref.SDAT'
act = '/Users/mrjeffs/Documents/Research/tadpole/TADPOLE901_GABA/TADPOLE901_WIP_GABAMM_TE80_12_2_raw_act.SDAT'
ref = '/Users/mrjeffs/Documents/Research/tadpole/TADPOLE901_GABA/TADPOLE901_WIP_GABAMM_TE80_12_2_raw_ref.SPAR'



mcode = "addpath('{0}'); MRS_struct = GannetLoad({{'{1}'}},{{'{2}'}}); MRS_struct = GannetFit(MRS_struct); exit;".format(
        mpath, act, ref)

cmd = 'matlab -nodisplay -nosplash -nodesktop -r "{0}"'.format(mcode)
subprocess.check_call(cmd, shell=True)