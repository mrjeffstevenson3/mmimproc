# genz mega press edited gaba spectroscopy processing script

# first set global root data directory
import pylabs
pylabs.datadir.target = 'jaba'
from pathlib import *
import datetime, json
import pandas as pd
from pylabs.utils import ProvenanceWrapper, run_subprocess, WorkingContext, getnetworkdataroot, appendposix
from pylabs.projects.genz.file_names import project, SubjIdPicks, get_gaba_names, Opts
from pylabs.io.mixed import getgabavalue, df2h5
prov = ProvenanceWrapper()

fs = Path(getnetworkdataroot())
gannettpath = pylabs.utils.paths.getgannettpath()

# instantiate subject id list container
subjids_picks = SubjIdPicks()
# list of subject ids to operate on

picks = [{'subj': 'sub-genz996', 'session': 'ses-2', 'run': '1',},
         #{'subj': 'sub-genz901', 'session': 'ses-1', 'run': '1',},
         #{'subj': 'sub-genz923', 'session': 'ses-1', 'run': '1',},
         #{'subj': 'sub-genz997', 'session': 'ses-2', 'run': '1',},
         ]

setattr(subjids_picks, 'subjids', picks)
setattr(subjids_picks, 'source_path', fs / project / '{subj}' / '{session}' / 'source_sparsdat')
# setattr(subjids_picks, 'source_path', fs / project / 'sub-tadpole%(sid)s' / 'ses-%(ses)s' / 'source_sparsdat')

opts = Opts()

acc_actfnames, acc_reffnames = get_gaba_names(subjids_picks)
# i = 0   # for testing
# acc_act, acc_ref = acc_actfnames[i], acc_reffnames[i]

for acc_act, acc_ref in zip(acc_actfnames, acc_reffnames):

    results_dir = acc_act.parents[1].joinpath('mrs')
    subj_info = {'subj': results_dir.parts[-3],
                 'session': results_dir.parts[-2],
                 'modality': results_dir.parts[-1]}

    if not results_dir.is_dir():
        results_dir.mkdir(parents=True)

    if not acc_act.is_file() or not acc_ref.is_file():
        raise ValueError('one or more .SDAT files is missing. please check.')

    acc_mcode = "addpath('{0}'); MRS_struct = GannetLoad({{'{1}'}},{{'{2}'}}); MRS_struct = GannetFit(MRS_struct); exit;".format(
            gannettpath, str(acc_act), str(acc_ref))

    acc_cmd = 'matlab -nodisplay -nosplash -nodesktop -r "{0}"'.format(acc_mcode)
    output =()
    with WorkingContext(str(results_dir)):
        try:
            p = Path('.')
            old_dirs = [x for x in p.iterdir() if x.is_dir() and ('MRSfit' in str(x) or 'MRSload' in str(x))]
            if len(old_dirs) != 0:
                for d in sorted(old_dirs, reverse=True):
                    d.rename(appendposix(d, '_old'))
            print ('starting gaba fits for {subj} in {session}'.format(**subj_info))
            output += run_subprocess([acc_cmd])

        except:
            print('an exception has occured during fit of {subj} in {session}'.format(**subj_info))
            print("({})".format(", ".join(output)))
            with open(str(results_dir/'mrs_gaba_error{:%Y%m%d%H%M}.json'.format(datetime.datetime.now())), mode='a') as logr:
                json.dump(output, logr, indent=2)
        else:
            for x in results_dir.glob("MRS*"):
                if '_old' not in str(x):
                    for f in x.glob("*.pdf"):
                        if 'fit' in str(f.parts[-2]):
                            f.rename(appendposix(f, '_fit'))
                            if '_ACC' in str(f.stem):
                                print (appendposix(f, '_fit'), appendposix(f, '_fit').is_file())
                                subj_info['acc-gaba'], subj_info['acc-gabaovercr'] = getgabavalue(appendposix(f, '_fit'))
                                subj_info['gaba-fit-datetime'] = '{:%Y%m%d%H%M}'.format(datetime.datetime.now())
                                output += ('ACC gaba results for {subj} in {session} is {acc-gaba}'.format(**subj_info),)
                                output += ('ACC gaba over Creatinine results for {subj} in {session} is {acc-gabaovercr}'.format(**subj_info),)
                        if 'output' in str(f.parts[-2]):
                            f.rename(appendposix(f, '_output'))
            print("({})".format(", ".join(output)))
            print('GABA fits completed normally for {subj} in {session}'.format(**subj_info))
            print ('ACC gaba = {acc-gaba}, and gaba over creatinine = {acc-gabaovercr}'.format(**subj_info))
            print('')
            with open(str(results_dir/'mrs_gaba_log{:%Y%m%d%H%M}.json'.format(datetime.datetime.now())), mode='a') as logr:
                json.dump(output, logr, indent=2)
            for p in results_dir.rglob("*.pdf"):
                if '_ACC' in str(p.stem):
                    prov.log(str(p), 'gannet gaba fit for acc', str(acc_act), provenance={'log': output, 'subj_info': subj_info})
        finally:
            df2h5(pd.DataFrame.from_dict({'gaba_fit_info': subj_info}), opts.info_fname, '/{subj}/{session}/mrs/gaba_fit_info'.format(**subj_info))
