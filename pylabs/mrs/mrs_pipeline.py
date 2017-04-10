from pylabs.utils import paths
from pylabs.utils import run_subprocess, WorkingContext
from pathlib import *
from pylabs.utils.paths import getnetworkdataroot

fs = Path(getnetworkdataroot())
project = 'nbwr'
subject = 'sub-nbwr999b'
rt_actfname = 'NWBR999B_WIP_RTGABAMM_TE80_120DYN_5_2_raw_act.SDAT'
rt_reffname = 'NWBR999B_WIP_RTGABAMM_TE80_120DYN_5_2_raw_ref.SDAT'
lt_actfname = 'NWBR999B_WIP_LTGABAMM_TE80_120DYN_8_2_raw_act.SDAT'
lt_reffname = 'NWBR999B_WIP_LTGABAMM_TE80_120DYN_8_2_raw_ref.SDAT'
source_path = fs / project / subject / 'ses-1' / 'source_parrec'
results_dir = fs / project / subject / 'ses-1' / 'mrs'

if not source_path.is_dir():
    raise ValueError('source_parrec dir with mrs SDAT not found. '+str(source_path))

if not results_dir.is_dir():
    results_dir.mkdir(parents=True)

mpath = paths.getgannettpath()
rt_act = source_path / rt_actfname
rt_ref = source_path / rt_reffname
lt_act = source_path / lt_actfname
lt_ref = source_path / lt_reffname

rt_mcode = "addpath('{0}'); MRS_struct = GannetLoad({{'{1}'}},{{'{2}'}}); MRS_struct = GannetFit(MRS_struct); exit;".format(
        mpath, str(rt_act), str(rt_ref))
lt_mcode = "addpath('{0}'); MRS_struct = GannetLoad({{'{1}'}},{{'{2}'}}); MRS_struct = GannetFit(MRS_struct); exit;".format(
        mpath, str(lt_act), str(lt_ref))

rt_cmd = 'matlab -nodisplay -nosplash -nodesktop -r "{0}"'.format(rt_mcode)
lt_cmd = 'matlab -nodisplay -nosplash -nodesktop -r "{0}"'.format(lt_mcode)
output =()
with WorkingContext(str(results_dir)):
    try:
        output += run_subprocess(rt_cmd)
        output += run_subprocess(lt_cmd)
    except:
        print('an exception has occured.')
        print("({})".format(", ".join(output)))
    else:
        print("({})".format(", ".join(output)))
        print('GABA fits completed normally.')

# add provenance here. traverse gannett out dirs to find PDFs