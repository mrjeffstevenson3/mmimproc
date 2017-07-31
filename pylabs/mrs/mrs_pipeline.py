import datetime, json
from pylabs.utils import paths
from pylabs.utils import run_subprocess, WorkingContext
from pathlib import *
from pylabs.utils.paths import getnetworkdataroot
from pylabs.utils.provenance import ProvenanceWrapper
prov = ProvenanceWrapper()

fs = Path(getnetworkdataroot())
project = 'nbwr'
subject = 'sub-nbwr404'
rt_actfname = 'sub-nbwr404c_WIP_RTGABAMM_TE80_120DYN_8_2_raw_act.SDAT'
rt_reffname = 'sub-nbwr404c_WIP_RTGABAMM_TE80_120DYN_8_2_raw_ref.SDAT'
lt_actfname = 'sub-nbwr404c_WIP_LTGABAMM_TE80_120DYN_7_2_raw_act.SDAT'
lt_reffname = 'sub-nbwr404c_WIP_LTGABAMM_TE80_120DYN_7_2_raw_ref.SDAT'
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
        with open(str(results_dir/'mrs_gaba_error{:%Y%m%d%H%M}.json'.format(datetime.datetime.now())), mode='a') as logr:
            json.dump(output, logr, indent=2)
    else:
        for x in results_dir.rglob("MRS*"):
            for f in x.glob("*.pdf"):
                if 'fit' in str(x):
                    f.rename(Path(str(f).replace('.pdf', '_fit.pdf')))
                if 'output' in str(x):
                    f.rename(Path(str(f).replace('.pdf', '_output.pdf')))
        print("({})".format(", ".join(output)))
        print('GABA fits completed normally.')
        with open(str(results_dir/'mrs_gaba_log{:%Y%m%d%H%M}.json'.format(datetime.datetime.now())), mode='a') as logr:
            json.dump(output, logr, indent=2)
        for p in results_dir.rglob("*.pdf"):
            if '_RT' in str(p.stem):
                prov.log(str(p), 'gannet gaba fit for right side', str(rt_act), providence={'log': output})
            if '_LT' in str(p.stem):
                prov.log(str(p), 'gannet gaba fit for left side', str(lt_act), providence={'log': output})

