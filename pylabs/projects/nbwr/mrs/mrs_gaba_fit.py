# nbwr mega press edited gaba spectroscopy processing script

# first set global root data directory
import pylabs
pylabs.datadir.target = 'jaba'
from pathlib import *
import datetime, json
from pylabs.utils import run_subprocess, WorkingContext, getnetworkdataroot, appendposix
from pylabs.utils.provenance import ProvenanceWrapper
from pylabs.projects.nbwr.file_names import project, SubjIdPicks, get_gaba_names
prov = ProvenanceWrapper()
# set root data directory to jaba.

fs = Path(getnetworkdataroot())
gannettpath = paths.getgannettpath()

# instantiate subject id list container
subjids_picks = SubjIdPicks()
# list of subject ids to operate on
picks = ['107', '407', '088']
setattr(subjids_picks, 'subjids', picks)
setattr(subjids_picks, 'source_path', fs / project / 'sub-nbwr%(sid)s' / 'ses-1' / 'source_sparsdat')

rt_actfnames, rt_reffnames, lt_actfnames, lt_reffnames = get_gaba_names(subjids_picks)


for rt_act, rt_ref, lt_act, lt_ref in zip(rt_actfnames, rt_reffnames, lt_actfnames, lt_reffnames):

    results_dir = rt_act.parents[1].joinpath('mrs')

    if not results_dir.is_dir():
        results_dir.mkdir(parents=True)

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
            p = Path('.')
            old_dirs = [x for x in p.iterdir() if x.is_dir() and ('MRSfit' in str(x) or 'MRSload' in str(x))]
            if len(old_dirs) != 0:
                for d in old_dirs:
                    d.rename(appendposix(d, '_old'))
            output += run_subprocess(rt_cmd)
            output += run_subprocess(lt_cmd)
        except:
            print('an exception has occured.')
            print("({})".format(", ".join(output)))
            with open(str(results_dir/'mrs_gaba_error{:%Y%m%d%H%M}.json'.format(datetime.datetime.now())), mode='a') as logr:
                json.dump(output, logr, indent=2)
        else:
            for x in results_dir.rglob("MRS*"):
                if '_old' not in str(x):
                    for f in x.glob("*.pdf"):
                        if 'fit' in str(x):
                            appendposix(f, '_fit')))
                        if 'output' in str(x):
                            appendposix(f, '_output')
            print("({})".format(", ".join(output)))
            print('GABA fits completed normally.')
            with open(str(results_dir/'mrs_gaba_log{:%Y%m%d%H%M}.json'.format(datetime.datetime.now())), mode='a') as logr:
                json.dump(output, logr, indent=2)
            for p in results_dir.rglob("*.pdf"):
                if '_RT' in str(p.stem):
                    prov.log(str(p), 'gannet gaba fit for right side', str(rt_act), script=__file__, provenance={'log': output})
                if '_LT' in str(p.stem):
                    prov.log(str(p), 'gannet gaba fit for left side', str(lt_act), script=__file__, provenance={'log': output})

