import datetime
from pylabs.utils import paths
from pylabs.utils import run_subprocess, WorkingContext
from pathlib import *
from pylabs.utils.paths import getnetworkdataroot

fs = Path(getnetworkdataroot())
project = 'nbwr'
subject = 'sub-nbwr144'
rt_actfname = 'NBWR144_WIP_RTGABAMM_TE80_120DYN_8_2_raw_act.SDAT'
rt_reffname = 'NBWR144_WIP_RTGABAMM_TE80_120DYN_8_2_raw_ref.SDAT'
lt_actfname = 'NBWR144_WIP_LTGABAMM_TE80_120DYN_7_2_raw_act.SDAT'
lt_reffname = 'NBWR144_WIP_LTGABAMM_TE80_120DYN_7_2_raw_ref.SDAT'
source_path = fs / project / subject / 'ses-1' / 'source_sparsdat'
results_dir = fs / project / subject / 'ses-1' / 'mrs'

if not source_path.is_dir():
    raise ValueError('source_parrec dir with mrs SDAT not found. '+str(source_path))

if not results_dir.is_dir():
    results_dir.mkdir(parents=True)

gannettpath = paths.getgannettpath()
rt_act = source_path / rt_actfname
rt_ref = source_path / rt_reffname
lt_act = source_path / lt_actfname
lt_ref = source_path / lt_reffname

if not rt_act.is_file() or not rt_ref.is_file() or not lt_act.is_file() or not lt_ref.is_file():
    raise ValueError('one or more .SDAT files is missing. please check.')

rt_mcode = "addpath('{0}'); MRS_struct = GannetLoad({{'{1}'}},{{'{2}'}}); MRS_struct = GannetFit(MRS_struct); exit;".format(
        gannettpath, str(rt_act), str(rt_ref))
lt_mcode = "addpath('{0}'); MRS_struct = GannetLoad({{'{1}'}},{{'{2}'}}); MRS_struct = GannetFit(MRS_struct); exit;".format(
        gannettpath, str(lt_act), str(lt_ref))

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
        with open(results_dir/'mrs_gaba_error{:%Y%m%d%H%M}.json'.format(datetime.datetime.now()), mode='a') as logr:
            json.dump(output, logr, indent=2)
    else:
        print("({})".format(", ".join(output)))
        print('GABA fits completed normally.')
        with open(results_dir/'mrs_gaba_log{:%Y%m%d%H%M}.json'.format(datetime.datetime.now()), mode='a') as logr:
            json.dump(output, logr, indent=2)

# add provenance here. traverse gannett out dirs to find PDFs