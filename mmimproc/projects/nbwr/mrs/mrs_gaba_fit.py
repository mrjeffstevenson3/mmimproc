# nbwr mega press edited gaba spectroscopy processing script

# first set global root data directory
import mmimproc
mmimproc.datadir.target = 'jaba'
import pandas as pd
from pathlib import *
import datetime, json
from mmimproc.utils import *
from mmimproc.projects.nbwr.file_names import project, SubjIdPicks, get_gaba_names
from mmimproc.io.mixed import getgabavalue, df2h5
prov = ProvenanceWrapper()

fs = mmimproc.fs_local
gannettpath = getgannettpath()
all_info_fname = fs/project/'all_{project}_info.h5'.format(**{'project': project})
pdf_only = True
# instantiate subject id list container
subjids_picks = SubjIdPicks()
# list of subject ids to operate on
id_thresh = 500
rawsubjects = list((fs/project).glob('sub-'+project+'*'))
subjects = []
for s in rawsubjects:
    if len(str(s.parts[-1])) == 11 and int(str(s.parts[-1]).replace('sub-'+project, '')) < id_thresh:
        subjects.append(s.parts[-1].replace('sub-'+project, ''))
subjects = sorted(subjects)

picks = subjects    #['442', '443'] # only does one subj until bug fix
setattr(subjids_picks, 'subjids', picks)
setattr(subjids_picks, 'source_path', fs / project / 'sub-nbwr%(sid)s' / 'ses-1' / 'source_sparsdat')
# setattr(subjids_picks, 'source_path', fs / project / 'sub-tadpole%(sid)s' / 'ses-%(ses)s' / 'source_sparsdat')

rt_actfnames, rt_reffnames, lt_actfnames, lt_reffnames = get_gaba_names(subjids_picks)

# for testing
i = 0
rt_act, rt_ref, lt_act, lt_ref = rt_actfnames[i], rt_reffnames[i], lt_actfnames[i], lt_reffnames[i]

for rt_act, rt_ref, lt_act, lt_ref in zip(rt_actfnames, rt_reffnames, lt_actfnames, lt_reffnames):
    results_dir = rt_act.parents[1].joinpath('mrs')
    subj_info = {'subj': results_dir.parts[-3],
                 'session': results_dir.parts[-2],
                 'modality': results_dir.parts[-1]}
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
        if not pdf_only:
            try:
                p = Path('.')
                old_dirs = [x for x in p.iterdir() if x.is_dir() and ('MRSfit' in str(x) or 'MRSload' in str(x))]
                if len(old_dirs) != 0:
                    for d in sorted(old_dirs, reverse=True):
                        d.rename(appendposix(d, '_old'))
                print('starting gaba fits for '+ results_dir.parts[-3])
                output += run_subprocess(rt_cmd)
                output += run_subprocess(lt_cmd)
            except:
                print('an exception has occured during fit of '+ results_dir.parts[-3])
                print("({})".format(", ".join(output)))
                with open(str(results_dir/'mrs_gaba_error{:%Y%m%d%H%M}.json'.format(datetime.datetime.now())), mode='a') as logr:
                    json.dump(output, logr, indent=2)
        for x in results_dir.glob("MRS*"):
            if '_old' not in str(x):
                for f in x.glob("*.pdf"):
                    if 'fit' in f.parts[-2]:
                        if '_RT' in f.name:
                            subj_info['right-gaba'], subj_info['right-gabaovercr'], subj_info['right-fit-err'], subj_info['right-perc-fit-err'] = getgabavalue(f)
                            subj_info['gaba-fit-datetime'] = '{:%Y%m%d%H%M}'.format(datetime.datetime.now())
                            output += ('Right gaba results for {subj} in {session} is {right-gaba}'.format(**subj_info),)
                            output += ('Right gaba over Creatinine results for {subj} in {session} is {right-gabaovercr}'.format(**subj_info),)
                        elif '_LT' in f.name:
                            subj_info['left-gaba'], subj_info['left-gabaovercr'], subj_info['left-fit-err'], subj_info['left-perc-fit-err'] = getgabavalue(f)
                            subj_info['gaba-fit-datetime'] = '{:%Y%m%d%H%M}'.format(datetime.datetime.now())
                            output += ('Left gaba results for {subj} in {session} is {left-gaba}'.format(**subj_info),)
                            output += ('Left gaba over Creatinine results for {subj} in {session} is {left-gabaovercr}'.format(**subj_info),)
                        if 'fit' not in f.name:
                            f.rename(appendposix(f, '_fit'))
                    if 'output' in f.parts[-2] and 'output' not in f.name:
                        f.rename(appendposix(f, '_output'))
        print("({})".format(", ".join(output)))
        print('GABA fits completed normally for {subj} {session}'.format(**subj_info))
        print('Left gaba results = {left-gaba} and right side gaba = {right-gaba}'.format(**subj_info))
        with open(str(results_dir/'mrs_gaba_log{:%Y%m%d%H%M}.json'.format(datetime.datetime.now())), mode='a') as logr:
            json.dump(output, logr, indent=2)
        for p in results_dir.rglob("*.pdf"):
            if '_RT' in str(p.stem):
                prov.log(str(p), 'gannet gaba fit for right side', str(rt_act), script=__file__, provenance={'log': output})
            if '_LT' in str(p.stem):
                prov.log(str(p), 'gannet gaba fit for left side', str(lt_act), script=__file__, provenance={'log': output})
        df2h5(pd.DataFrame.from_dict({'gaba_fit_info': subj_info}), all_info_fname, '/{subj}/{session}/mrs/gaba_fit_info'.format(**subj_info))
