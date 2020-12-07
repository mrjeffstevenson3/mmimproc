# genz mega press edited gaba spectroscopy processing script

# first set global root data directory
import mmimproc
mmimproc.datadir.target = 'jaba'
from pathlib import *
import datetime, json
import pandas as pd
from mmimproc.utils import *
from mmimproc.projects.genz.file_names import project, SubjIdPicks, get_gaba_names, get_freesurf_names, Optsd
from mmimproc.structural.brain_extraction import extract_brain
from mmimproc.io.mixed import getgabavalue, df2h5
prov = ProvenanceWrapper()

fs = mmimproc.fs_local
gannettpath = getgannettpath()
spmpath, tpm_path = getspmpath()

# instantiate subject id list container
subjids_picks = SubjIdPicks()
# list of subject ids to operate on

picks = [{'subj': 'sub-genz501', 'session': 'ses-1', 'run': '1',},

         ]

setattr(subjids_picks, 'subjids', picks)
setattr(subjids_picks, 'source_path', fs / project / '{subj}' / '{session}' / 'source_sparsdat')

opts = Optsd()

acc_actfnames, acc_reffnames = get_gaba_names(subjids_picks)
b1map_fs_fnames, freesurf_fnames = get_freesurf_names(subjids_picks)

# i = 0   # for testing
# acc_act, acc_ref = acc_actfnames[i], acc_reffnames[i]
# b1map, fs_rms = b1map_fs_fnames[i], freesurf_fnames[i]

for acc_act, acc_ref, b1map, fs_rms in zip(acc_actfnames, acc_reffnames, b1map_fs_fnames, freesurf_fnames):

    results_dir = acc_act.parents[1].joinpath('mrs')
    subj_info = {'subj': results_dir.parts[-3],
                 'session': results_dir.parts[-2],
                 'modality': results_dir.parts[-1],
                 'region': 'ACC',
                 'gannettpath': gannettpath,
                 'spmpath': spmpath,
                 'acc_act': acc_act,
                 'acc_ref': acc_ref,
                 'b1map': fs/project/results_dir.parts[-3]/results_dir.parts[-2]/'fmap'/(b1map+'.nii'),
                 'fs_rms': fs/project/results_dir.parts[-3]/results_dir.parts[-2]/'anat'/(fs_rms+'.nii'),

                 }

    if not results_dir.is_dir():
        results_dir.mkdir(parents=True)

    if not acc_act.is_file() or not acc_ref.is_file():
        raise ValueError('one or more .SDAT files is missing. please check.')

    fs_rms_brain, fs_rms_brain_mask, fs_rms_cropped = extract_brain(subj_info['fs_rms'], nii=True)

    subj_info['fs_rms_brain'] = fs_rms_brain
    subj_info['fs_rms_brain_mask'] = fs_rms_brain_mask

    acc_mcode = "addpath('{gannettpath}', '{genpath(spmpath})'); MRS_struct = GannetLoad({{'{acc_act}'}},{{'{acc_ref}'}});" \
                " MRS_struct = GannetFit(MRS_struct); MRS_struct = GannetCoRegister(MRS_struct, {{'{fs_rms_brain}'}});" \
                " MRS_struct = GannetSegment(MRS_struct) ; exit;".format(**subj_info)

    acc_cmd = 'matlab -nodisplay -nosplash -nodesktop -r "{0}"'.format(acc_mcode)
    output =()
    with WorkingContext(str(results_dir)):
        try:
            p = Path('.')
            old_dirs = [x for x in p.iterdir() if x.is_dir() and ('MRSfit' in str(x) or 'MRSload' in str(x))]
            if len(old_dirs) != 0:
                for d in sorted(old_dirs, reverse=True):
                    d.rename(appendposix(d, '_old'))
            print('starting gaba fits for {subj} in {session}'.format(**subj_info))
            output += run_subprocess([acc_cmd])

        except:
            print('an exception has occured during fit of {subj} in {session} for region {region}'.format(**subj_info))
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
                                print(appendposix(f, '_fit'), appendposix(f, '_fit').is_file())
                                subj_info['acc-gaba'], subj_info['acc-gabaovercr'], subj_info['acc-fit-err'], subj_info['acc-perc-fit-err'] = getgabavalue(appendposix(f, '_fit'))
                                subj_info['gaba-fit-datetime'] = '{:%Y%m%d%H%M}'.format(datetime.datetime.now())
                                output += ('ACC gaba results for {subj} in {session} is {acc-gaba}'.format(**subj_info),)
                                output += ('ACC gaba over Creatinine results for {subj} in {session} is {acc-gabaovercr}'.format(**subj_info),)
                        if 'output' in str(f.parts[-2]):
                            f.rename(appendposix(f, '_output'))
            print("({})".format(", ".join(output)))
            print('GABA fits completed normally for {subj} in {session}'.format(**subj_info))
            print('ACC gaba = {acc-gaba}, and gaba over creatinine = {acc-gabaovercr}'.format(**subj_info))
            print('ACC fit error = {acc-fit-err}'.format(**subj_info))
            print('')
            with open(str(results_dir/'mrs_gaba_log{:%Y%m%d%H%M}.json'.format(datetime.datetime.now())), mode='a') as logr:
                json.dump(output, logr, indent=2)
            for p in results_dir.rglob("*.pdf"):
                if '_ACC' in str(p.stem):
                    prov.log(str(p), 'gannet gaba fit for acc', str(acc_act), provenance={'log': output, 'subj_info': subj_info})
        finally:
            df2h5(pd.DataFrame.from_dict({'gaba_fit_info': subj_info}), opts.info_fname, '/{subj}/{session}/mrs/gaba_fit_info'.format(**subj_info))
