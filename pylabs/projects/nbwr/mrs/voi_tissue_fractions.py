# needs to be made into callable function using extract_brain and spm for segs as death match
# first set global root data directory and defaults
import pylabs
pylabs.datadir.target = 'jaba'
pylabs.opts.nii_ftype = 'NIFTI'
pylabs.opts.nii_fext = '.nii'
pylabs.opts.fslmultifilequit = 'FALSE'
pylabs.opts.overwrite = True
thresh = pylabs.opts.spm_seg_thr
import os, json
from pathlib import *
import pandas as pd
import matlab.engine
from nipype.interfaces import fsl
from pylabs.mrs.tissue_fractions import make_voi_mask, calc_tissue_fractions
from pylabs.structural.brain_extraction import extract_brain
from pylabs.utils import ProvenanceWrapper, run_subprocess, WorkingContext, getnetworkdataroot, appendposix, replacesuffix, \
    prependposix, getspmpath, pylabs_dir
from pylabs.projects.nbwr.file_names import project, SubjIdPicks, subjs_h5_info_fname, get_matching_voi_names, get_gaba_names
prov = ProvenanceWrapper()

os.environ['FSLOUTPUTTYPE'] = pylabs.opts.nii_ftype
os.environ["FSLMULTIFILEQUIT"] = pylabs.opts.fslmultifilequit

fs = Path(getnetworkdataroot())
spm_dir, tpm_path = getspmpath()

eng = matlab.engine.start_matlab()
eng.addpath(eng.genpath(str(pylabs_dir)))
eng.addpath(eng.genpath(str(spm_dir)))

fast = fsl.FAST(
                output_type=pylabs.opts.nii_ftype,
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
fast.inputs.environ['FSLMULTIFILEQUIT'] = pylabs.opts.fslmultifilequit
ext = pylabs.opts.nii_fext
 # results of segmentation
only_spm = True
# instantiate subject id list container
subjids_picks = SubjIdPicks()
# list of subject ids to operate on
picks = ['447', ]
setattr(subjids_picks, 'subjids', picks)
setattr(subjids_picks, 'source_path', fs / project / 'sub-nbwr%(sid)s' / 'ses-1' / 'source_sparsdat')

rt_actfnames, rt_reffnames, lt_actfnames, lt_reffnames = get_gaba_names(subjids_picks)

rt_matchfnames, lt_matchfnames = get_matching_voi_names(subjids_picks)

test_l = map(len, (rt_actfnames, lt_actfnames, rt_matchfnames, lt_matchfnames))
if not all(test_l[0] == l for l in test_l):
    raise ValueError('lists lengths do not all match. cannot zip '+str(test_l))

for rt_matchfname, lt_matchfname, rt_actfname, lt_actfname in zip(rt_matchfnames, lt_matchfnames, rt_actfnames, lt_actfnames):
    results = ()
    if not rt_matchfname.split('_')[0] == lt_matchfname.split('_')[0]:
        raise ValueError('subject id does not match between right and left side.')
    subject = rt_matchfname.split('_')[0]
    session = rt_matchfname.split('_')[1]
    mrs_dir = fs / project / subject / session / 'mrs'
    if not mrs_dir.is_dir():
        raise ValueError('cant find mrs directory '+str(mrs_dir))
    # get gaba data from gannett fits json
    if len(list(mrs_dir.glob('mrs_gaba_log*.json'))) > 0:
        gaba_fits_logf = sorted(list(mrs_dir.glob('mrs_gaba_log*.json')), key=lambda date: int(date.stem.split('_')[-1].replace('log','')))[-1]
    # first do right side
    with WorkingContext(str(mrs_dir)):
        try:
            # start with right side
            rt_match_pfname = mrs_dir / appendposix(rt_matchfname, ext)
            if pylabs.opts.overwrite: # and not only_spm:   ## or not Path(replacesuffix(rt_match_pfname, '_brain'+ext)).is_file():
                print('running brain extraction on '+str(rt_match_pfname))
                rt_match_brain, rt_match_mask = extract_brain(str(rt_match_pfname))
            else:
                rt_match_brain, rt_match_mask = replacesuffix(rt_match_pfname, '_brain'+ext), replacesuffix(rt_match_pfname, '_brain_mask'+ext)
            if pylabs.opts.overwrite: #  and not only_spm:  ## or not Path(replacesuffix(rt_match_pfname, '_brain_susanf'+ext)).is_file():
                print('running susan filter on ' + str(rt_match_brain))
                results += run_subprocess(['susan ' + str(rt_match_brain) + ' -1 1 3 1 0 ' + str(replacesuffix(rt_match_brain, '_susanf'+ext))])
                rt_match_brain = replacesuffix(rt_match_brain, '_susanf' + ext)
            else:
                rt_match_brain = replacesuffix(rt_match_brain, '_susanf'+ext)
            if pylabs.opts.overwrite: # and not only_spm:   ## or not Path(replacesuffix(rt_match_pfname, '_mrs_roi_mask'+ext)).is_file():
                print('running make mask voi on ' +str(replacesuffix(rt_actfname, '.SPAR'))+' and '+ str(rt_match_brain))
                rt_mask_img = make_voi_mask(replacesuffix(rt_actfname, '.SPAR'), rt_match_brain, replacesuffix(rt_match_pfname, '_mrs_roi_mask'+ext))
            # run SPM segmentation on right matching
            if pylabs.opts.overwrite: #  and only_spm:   ## or not (Path(prependposix(rt_match_brain, 'c1')).is_file() & Path(prependposix(rt_match_brain, 'c2')).is_file() & Path(prependposix(rt_match_brain, 'c3')).is_file()):
                print('running SPM Segmentation on ' + str(rt_match_brain)+' and '+str(rt_match_mask))
                eng.spm_seg(str(rt_match_brain), str(tpm_path), nargout=0)
            # run FSL segmentation on right matching
            if pylabs.opts.overwrite: # and not only_spm:   ## or not (Path(replacesuffix(rt_match_brain, '_fslfast_seg_1'+ext)).is_file() & Path(replacesuffix(rt_match_brain, '_fslfast_seg_2'+ext)).is_file() & Path(replacesuffix(rt_match_brain, '_fslfast_seg_0'+ext)).is_file()):
                print('running FSL Segmentation on ' + str(rt_match_brain))
                fast.inputs.in_files = str(rt_match_brain)
                fast.inputs.out_basename = str(replacesuffix(rt_match_brain, '_fslfast'))
                fast.run()

            # now do left side
            print ('overwrite='+str(pylabs.opts.overwrite))
            lt_match_pfname = mrs_dir / appendposix(lt_matchfname, ext)
            if pylabs.opts.overwrite: # and not only_spm:   ## or not Path(replacesuffix(lt_match_pfname, '_brain'+ext)).is_file():
                print('running brain extraction on ' + str(lt_match_pfname))
                lt_match_brain, lt_match_mask = extract_brain(str(lt_match_pfname))
            else:
                lt_match_brain, lt_match_mask = replacesuffix(lt_match_pfname, '_brain'+ext), replacesuffix(lt_match_pfname, '_brain_mask'+ext)
            if pylabs.opts.overwrite: # and not only_spm:   ##  or not Path(replacesuffix(lt_match_pfname, '_brain_susanf'+ext)).is_file():
                print('running susan filter on ' + str(lt_match_brain))
                results += run_subprocess(['susan ' + str(lt_match_brain) + ' -1 1 3 1 0 ' + str(replacesuffix(lt_match_brain, '_susanf'+ext))])
                lt_match_brain = replacesuffix(lt_match_brain, '_susanf' + ext)
            else:
                lt_match_brain = replacesuffix(lt_match_brain, '_susanf'+ext)

            if pylabs.opts.overwrite: # and not only_spm:   ## or not Path(replacesuffix(lt_match_pfname, '_mrs_roi_mask'+ext)).is_file():
                print('running make mask voi on ' + str(replacesuffix(lt_actfname, '.SPAR')) + ' and ' + str(lt_match_brain))
                lt_mask_img = make_voi_mask(replacesuffix(lt_actfname, '.SPAR'), lt_match_brain, replacesuffix(lt_match_pfname, '_mrs_roi_mask'+ext))

            # run SPM segmentation on left matching
            if pylabs.opts.overwrite: # and only_spm:   ## or not (Path(prependposix(lt_match_brain, 'c1')).is_file() & Path(prependposix(lt_match_brain, 'c2')).is_file() & Path(prependposix(lt_match_brain, 'c3')).is_file()):
                print('running SPM Segmentation on ' + str(lt_match_brain) + ' and ' + str(lt_match_mask))
                eng.spm_seg(str(lt_match_brain), str(tpm_path), nargout=0)
            # run FSL segmentation on left matching
            if pylabs.opts.overwrite: # and not only_spm:   ## or not (Path(replacesuffix(lt_match_brain, '_fslfast_seg_1'+ext)).is_file() & Path(replacesuffix(lt_match_brain, '_fslfast_seg_2'+ext)).is_file() & Path(replacesuffix(lt_match_brain, '_fslfast_seg_0'+ext)).is_file()):
                print('running FSL Segmentation on ' + str(lt_match_brain))
                fast.inputs.in_files = str(lt_match_brain)
                fast.inputs.out_basename = str(replacesuffix(lt_match_brain, '_fslfast'))
                fast.run()

            # calculate right FSL tissue fractions
            rt_fsl_fractions = calc_tissue_fractions(replacesuffix(rt_match_pfname, '_mrs_roi_mask'+ext),
                                                     str(replacesuffix(rt_match_brain, '_fslfast_seg_1'+ext)),
                                                     str(replacesuffix(rt_match_brain, '_fslfast_seg_2'+ext)),
                                                     str(replacesuffix(rt_match_brain, '_fslfast_seg_0'+ext)),
                                                     'right', method='FSL')
            # calculate right SPM tissue fractions
            rt_spm_fractions = calc_tissue_fractions(replacesuffix(rt_match_pfname, '_mrs_roi_mask'+ext),
                                                     str(prependposix(rt_match_brain, 'c1')),
                                                     str(prependposix(rt_match_brain, 'c2')),
                                                     str(prependposix(rt_match_brain, 'c3')),
                                                     'right', method='SPM', thresh=thresh)

            # calculate left FSL tissue fractions
            lt_fsl_fractions = calc_tissue_fractions(replacesuffix(lt_match_pfname, '_mrs_roi_mask'+ext),
                                                     str(replacesuffix(lt_match_brain, '_fslfast_seg_1'+ext)),
                                                     str(replacesuffix(lt_match_brain, '_fslfast_seg_2'+ext)),
                                                     str(replacesuffix(lt_match_brain, '_fslfast_seg_0'+ext)),
                                                     'left', method='FSL')
            # calculate left SPM tissue fractions
            lt_spm_fractions = calc_tissue_fractions(replacesuffix(lt_match_pfname, '_mrs_roi_mask'+ext),
                                                     str(prependposix(lt_match_brain, 'c1')),
                                                     str(prependposix(lt_match_brain, 'c2')),
                                                     str(prependposix(lt_match_brain, 'c3')),
                                                     'left', method='SPM', thresh=thresh)
            # use merge df
            fractions = pd.DataFrame({'left_SPM': lt_spm_fractions, 'right_SPM': rt_spm_fractions, 'left_FSL': lt_fsl_fractions, 'right_FSL': rt_fsl_fractions})
            fractions.to_csv(str(mrs_dir / str(subject + '_sv_voi_tissue_proportions.csv')), sep=',', columns=['left_SPM', 'right_SPM', 'left_FSL', 'right_FSL'])
            # temp solution to get data out
            indx = [subject, 'left-percCSF', 'right-percCSF', ]
            data = {'subject': subject, 'left-percCSF': fractions.loc['frac_CSF', 'left_SPM'],
                    'right-percCSF': fractions.loc['frac_CSF', 'right_SPM']}
            csf_data = pd.Series(data, index=indx, name=data['subject'])
            csf_data.to_csv(str(mrs_dir / str(subject + '_csf_fractions.csv')))
            fractions.to_hdf(str(subjs_h5_info_fname), subject/session/'mrs'/'CSF_correction_factors', append=True, format = 'table')
            prov.log(str(mrs_dir / str(subject + '_sv_voi_tissue_proportions.csv')),
                     'csv text file containing percent CSF, GM, WM', str(lt_match_brain),
                     provenance={'thresh': thresh, 'side': 'left', 'method': 'SPM', 'tissue': 'GM'}, script=__file__)
            print ('results for tissue fractions for subject '+str(subject))
            print(fractions)
            if pylabs.opts.overwrite:
                prov.log(str(prependposix(lt_match_brain, 'c1')), 'grey matter SPM segmentation of matching left mrs voi', str(lt_match_brain), provenance={'thresh': thresh, 'side': 'left', 'method': 'SPM', 'tissue': 'GM'}, script=__file__)
                prov.log(str(prependposix(lt_match_brain, 'c2')), 'white matter SPM segmentation of matching left mrs voi', str(lt_match_brain), provenance={'thresh': thresh, 'side': 'left', 'method': 'SPM', 'tissue': 'WM'}, script=__file__)
                prov.log(str(prependposix(lt_match_brain, 'c3')), 'CSF SPM segmentation of matching left mrs voi', str(lt_match_brain), provenance={'thresh': thresh, 'side': 'left', 'method': 'SPM', 'tissue': 'CSF'}, script=__file__)
                prov.log(str(prependposix(rt_match_brain, 'c1')), 'grey matter SPM segmentation of matching right mrs voi', str(rt_match_brain), provenance={'thresh': thresh, 'side': 'right', 'method': 'SPM', 'tissue': 'GM'}, script=__file__)
                prov.log(str(prependposix(rt_match_brain, 'c2')), 'white matter SPM segmentation of matching right mrs voi', str(rt_match_brain), provenance={'thresh': thresh, 'side': 'right', 'method': 'SPM', 'tissue': 'WM'}, script=__file__)
                prov.log(str(prependposix(rt_match_brain, 'c3')), 'CSF SPM segmentation of matching right mrs voi', str(rt_match_brain), provenance={'thresh': thresh, 'side': 'right', 'method': 'SPM', 'tissue': 'CSF'}, script=__file__)

        except:
            raise

eng.quit()

