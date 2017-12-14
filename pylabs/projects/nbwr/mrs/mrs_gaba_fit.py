# nbwr mega press edited gaba spectroscopy processing script

# first set global root data directory
import pylabs
pylabs.datadir.target = 'jaba'
from pathlib import *
import datetime, json
from pylabs.utils import ProvenanceWrapper, run_subprocess, WorkingContext, getnetworkdataroot, appendposix
from pylabs.projects.nbwr.file_names import project, SubjIdPicks, get_gaba_names
from pylabs.io.mixed import getgabavalue
prov = ProvenanceWrapper()

fs = Path(getnetworkdataroot())
gannettpath = pylabs.utils.paths.getgannettpath()

# instantiate subject id list container
subjids_picks = SubjIdPicks()
# list of subject ids to operate on
picks = ['447',] # only does one subj until bug fix
setattr(subjids_picks, 'subjids', picks)
setattr(subjids_picks, 'source_path', fs / project / 'sub-nbwr%(sid)s' / 'ses-1' / 'source_sparsdat')
# setattr(subjids_picks, 'source_path', fs / project / 'sub-tadpole%(sid)s' / 'ses-%(ses)s' / 'source_sparsdat')

rt_actfnames, rt_reffnames, lt_actfnames, lt_reffnames = get_gaba_names(subjids_picks)


for rt_act, rt_ref, lt_act, lt_ref in zip(rt_actfnames, rt_reffnames, lt_actfnames, lt_reffnames):
    # use only if rt side has motion like 215
    #toddpath = rt_act.parent/'toddtest'
    #rt_act = toddpath/'sub-nbwr215_WIP_RTGABAMM_TE80_120DYN_12_2_edited_dyn80_raw_act.SDAT'

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
                for d in sorted(old_dirs, reverse=True):
                    d.rename(appendposix(d, '_old'))
            print ('starting gaba fits for '+ results_dir.parts[-3])
            output += run_subprocess(rt_cmd)
            output += run_subprocess(lt_cmd)
        except:
            print('an exception has occured during fit of '+ results_dir.parts[-3])
            print("({})".format(", ".join(output)))
            with open(str(results_dir/'mrs_gaba_error{:%Y%m%d%H%M}.json'.format(datetime.datetime.now())), mode='a') as logr:
                json.dump(output, logr, indent=2)
        else:
            for x in results_dir.glob("MRS*"):
                if '_old' not in str(x):
                    for f in x.glob("*.pdf"):
                        if 'fit' in str(f.parts[-2]):
                            f.rename(appendposix(f, '_fit'))
                            if '_RT' in str(f.stem):
                                print (appendposix(f, '_fit'), appendposix(f, '_fit').is_file())
                                rt_gaba_value = getgabavalue(appendposix(f, '_fit'))
                                output += ('Right gaba results ' + str(rt_gaba_value),)
                            elif '_LT' in str(f.stem):
                                lt_gaba_value = getgabavalue(appendposix(f, '_fit'))
                                output += ('Left gaba results ' + str(lt_gaba_value),)
                        if 'output' in str(f.parts[-2]):
                            f.rename(appendposix(f, '_output'))
            print("({})".format(", ".join(output)))
            print('GABA fits completed normally for ' + results_dir.parts[-3])
            print ('Left gaba results = ' + str(lt_gaba_value) + ' and right side gaba = ' + str(rt_gaba_value))
            with open(str(results_dir/'mrs_gaba_log{:%Y%m%d%H%M}.json'.format(datetime.datetime.now())), mode='a') as logr:
                json.dump(output, logr, indent=2)
            for p in results_dir.rglob("*.pdf"):
                if '_RT' in str(p.stem):
                    prov.log(str(p), 'gannet gaba fit for right side', str(rt_act), script=__file__, provenance={'log': output})
                if '_LT' in str(p.stem):
                    prov.log(str(p), 'gannet gaba fit for left side', str(lt_act), script=__file__, provenance={'log': output})

