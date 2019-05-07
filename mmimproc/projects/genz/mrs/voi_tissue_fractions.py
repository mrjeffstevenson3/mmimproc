# needs to be made into callable function using extract_brain and spm for segs as death match
# first set global root data directory and defaults
import mmimproc
mmimproc.datadir.target = 'jaba'
mmimproc.popts.nii_ftype = 'NIFTI'
mmimproc.popts.nii_fext = '.nii'
mmimproc.popts.fslmultifilequit = 'FALSE'
mmimproc.popts.overwrite = True
thresh = mmimproc.popts.spm_seg_thr
import os, json
from pathlib import *
import pandas as pd
import matlab.engine
from nipype.interfaces import fsl
from mmimproc.io.mixed import df2h5
from mmimproc.mrs.tissue_fractions import make_voi_mask, calc_tissue_fractions
from mmimproc.structural.brain_extraction import extract_brain
from mmimproc.utils import *
from mmimproc.projects.genz.file_names import project, SubjIdPicks, get_matching_voi_names, get_gaba_names, Opts
prov = ProvenanceWrapper()

os.environ['FSLOUTPUTTYPE'] = mmimproc.popts.nii_ftype
os.environ["FSLMULTIFILEQUIT"] = mmimproc.popts.fslmultifilequit

fs = mmimproc.fs
opts = Opts()
mmimproc.popts.overwrite = True
do_mask = True
do_spm = True
if do_spm:
    spm_dir, tpm_path = getspmpath()
    eng = matlab.engine.start_matlab()
    eng.addpath(eng.genpath(str(mmimproc_dir)))
    eng.addpath(eng.genpath(str(spm_dir)))

do_fast = True
fast = fsl.FAST(
                output_type=mmimproc.popts.nii_ftype,
                number_classes=3,
                segments=True,
                img_type=1,
                hyper=0.1,
                bias_iters=4,
                bias_lowpass=20,
                output_biascorrected=True,
                output_biasfield=True,
                probability_maps=True,
            )
fast.inputs.environ['FSLMULTIFILEQUIT'] = mmimproc.popts.fslmultifilequit
ext = mmimproc.popts.nii_fext
# results of segmentation
only_spm = False
# instantiate subject id list container
subjids_picks = SubjIdPicks()
# list of dicts with subject ids, session, scan info to operate on
picks = [
         #{'subj': 'sub-genz996', 'session': 'ses-1', 'run': '1',},
         #{'subj': 'sub-genz996', 'session': 'ses-2', 'run': '1',},
         #{'subj': 'sub-genz997', 'session': 'ses-1', 'run': '1',},
         {'subj': 'sub-genz901', 'session': 'ses-1', 'run': '1',}
         ]

setattr(subjids_picks, 'subjids', picks)
setattr(subjids_picks, 'source_path', fs / project / '{subj}' / '{session}' / 'source_sparsdat')

acc_actfnames, acc_reffnames = get_gaba_names(subjids_picks)

acc_matchfnames = get_matching_voi_names(subjids_picks)

test_l = map(len, (acc_actfnames, acc_reffnames, acc_matchfnames))
if not all(test_l[0] == l for l in test_l):
    raise ValueError('lists lengths do not all match. cannot zip '+str(test_l))

# for testing
# acc_matchfname, acc_actfname, acc_reffname = acc_matchfnames[0], acc_actfnames[0], acc_reffnames[0]

for acc_matchfname, acc_actfname, acc_reffname in zip(acc_matchfnames, acc_actfnames, acc_reffnames):
    results = ()
    subject = acc_matchfname.name.split('_')[0]
    session = acc_matchfname.name.split('_')[1]
    mrs_dir = fs / project / subject / session / 'mrs'
    if not mrs_dir.is_dir():
        raise ValueError('cant find mrs directory '+str(mrs_dir))
    # get gaba data from most recent gannett fits json
    if len(list(mrs_dir.glob('mrs_gaba_log*.json'))) > 0:
        gaba_fits_logf = sorted(list(mrs_dir.glob('mrs_gaba_log*.json')), key=lambda date: int(date.stem.split('_')[-1].replace('log','')))[-1]
    # first do right side
    with WorkingContext(str(mrs_dir)):
        try:
            if mmimproc.popts.overwrite: # and not only_spm:   ## or not Path(replacesuffix(rt_match_pfname, '_brain'+ext)).is_file():
                print('running brain extraction on '+str(acc_matchfname)+ext)
                acc_match_brain, acc_match_mask, acc_match_cropped = extract_brain(str(acc_matchfname)+ext)
            else:
                acc_match_brain, acc_match_mask, acc_match_cropped = replacesuffix(acc_matchfname, '_brain'+ext), replacesuffix(acc_matchfname, '_brain_mask'+ext), replacesuffix(acc_matchfname, '_cropped'+ext)
            if mmimproc.popts.overwrite: #  and not only_spm:  ## or not Path(replacesuffix(rt_match_pfname, '_brain_susanf'+ext)).is_file():
                print('running susan filter on ' + str(acc_match_brain))
                results += run_subprocess(['susan ' + str(acc_match_brain) + ' -1 1 3 1 0 ' + str(appendposix(acc_match_brain, '_susanf'))])
                acc_match_brain = appendposix(acc_match_brain, '_susanf')
            else:
                acc_match_brain = replacesuffix(acc_match_brain, '_susanf'+ext)
            if mmimproc.popts.overwrite and do_mask: # and not only_spm:   ## or not Path(replacesuffix(rt_match_pfname, '_mrs_roi_mask'+ext)).is_file():
                print('running make mask voi on ' +str(replacesuffix(acc_actfname, '.SPAR')))
                acc_mask_img = make_voi_mask(replacesuffix(acc_actfname, '.SPAR'), acc_match_brain, replacesuffix(acc_match_brain, '_mrs_roi_mask'+ext))


            # run SPM segmentation on right matching
            if mmimproc.popts.overwrite and do_spm: #  and only_spm:   ## or not (Path(prependposix(rt_match_brain, 'c1')).is_file() & Path(prependposix(rt_match_brain, 'c2')).is_file() & Path(prependposix(rt_match_brain, 'c3')).is_file()):
                print('running SPM Segmentation on ' + str(acc_match_brain))
                eng.spm_seg(str(acc_match_brain), str(tpm_path), nargout=0)
            # run FSL segmentation on right matching
            if mmimproc.popts.overwrite and do_fast: # and not only_spm:   ## or not (Path(replacesuffix(rt_match_brain, '_fslfast_seg_1'+ext)).is_file() & Path(replacesuffix(rt_match_brain, '_fslfast_seg_2'+ext)).is_file() & Path(replacesuffix(rt_match_brain, '_fslfast_seg_0'+ext)).is_file()):
                print('running FSL Segmentation on ' + str(acc_match_brain))
                fast.inputs.in_files = str(acc_match_brain)
                fast.inputs.out_basename = str(replacesuffix(acc_match_brain, '_fslfast'))
                fast.run()

            # calculate acc FSL tissue fractions
            acc_fsl_fractions = calc_tissue_fractions(replacesuffix(acc_match_brain, '_mrs_roi_mask'+ext),
                                                     str(replacesuffix(acc_match_brain, '_fslfast_seg_1'+ext)),
                                                     str(replacesuffix(acc_match_brain, '_fslfast_seg_2'+ext)),
                                                     str(replacesuffix(acc_match_brain, '_fslfast_seg_0'+ext)),
                                                     'acc', method='FSL')
            eng.quit()
            # calculate acc SPM tissue fractions
            acc_spm_fractions = calc_tissue_fractions(replacesuffix(acc_match_brain, '_mrs_roi_mask'+ext),
                                                     str(prependposix(acc_match_brain, 'c1')),
                                                     str(prependposix(acc_match_brain, 'c2')),
                                                     str(prependposix(acc_match_brain, 'c3')),
                                                     'acc', method='SPM', thresh=thresh)



            # use merge df
            fractions = pd.DataFrame({'acc_SPM': acc_spm_fractions, 'acc_FSL': acc_fsl_fractions, })
            df2h5(fractions, str(fs / project / 'all_genz_info.h5'),
                  '/' + subject + '/' + session + '/mrs/CSF_correction_factors')
            fractions.to_csv(str(mrs_dir / str(subject + '_sv_voi_tissue_proportions.csv')), sep=',', index_label='segmentation_info', columns=['acc_SPM', 'acc_FSL'])

            # temp solution to get data out. not sure about this...
            # indx = [subject, 'acc-percCSF', ]
            # data = {'subject': subject, 'acc-percCSF': fractions.loc['frac_CSF', 'acc_SPM'],}
            # csf_data = pd.Series(data, index=indx, name=data['subject'])
            # csf_data.to_csv(str(mrs_dir / str(subject + '_csf_fractions.csv')))
            # fractions.to_hdf(str(subjs_h5_info_fname), subject/session/'mrs'/'CSF_correction_factors', append=True, format = 'table')
            prov.log(str(mrs_dir / str(subject + '_sv_voi_tissue_proportions.csv')),
                     'csv text file containing percent CSF, GM, WM', str(acc_match_brain),
                     provenance={'thresh': thresh, 'method': 'SPM', 'tissue': 'GM'}, script=__file__)
            print('results for tissue fractions for subject '+str(subject))
            print(fractions)
            if mmimproc.popts.overwrite:
                prov.log(str(prependposix(acc_match_brain, 'c1')), 'grey matter SPM segmentation of matching acc mrs voi', str(acc_match_brain), provenance={'thresh': thresh, 'side': 'right', 'method': 'SPM', 'tissue': 'GM'}, script=__file__)
                prov.log(str(prependposix(acc_match_brain, 'c2')), 'white matter SPM segmentation of matching acc mrs voi', str(acc_match_brain), provenance={'thresh': thresh, 'side': 'right', 'method': 'SPM', 'tissue': 'WM'}, script=__file__)
                prov.log(str(prependposix(acc_match_brain, 'c3')), 'CSF SPM segmentation of matching acc mrs voi', str(acc_match_brain), provenance={'thresh': thresh, 'side': 'right', 'method': 'SPM', 'tissue': 'CSF'}, script=__file__)

        except:
            raise

if do_spm:
    eng.quit()
