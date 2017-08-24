# needs to be made into callable function using extract_brain and spm for segs as death match
# first set global root data directory
import pylabs
pylabs.datadir.target = 'jaba'
from pathlib import *
import nibabel as nib
import numpy as np
import nipype.interfaces.spm as spm
from nipype.interfaces import fsl
from pylabs.io.spar import load as readspar
from pylabs.io.images import savenii
from pylabs.structural.brain_extraction import extract_brain
from pylabs.utils import ProvenanceWrapper, run_subprocess, WorkingContext, getnetworkdataroot, appendposix, replacesuffix
from pylabs.projects.nbwr.file_names import project, SubjIdPicks, get_matching_voi_names, get_gaba_names
prov = ProvenanceWrapper()

fs = Path(getnetworkdataroot())
seg = spm.Segment()
fast = fsl.FAST()

# instantiate subject id list container
subjids_picks = SubjIdPicks()
# list of subject ids to operate on
picks = ['404'] # only does one subj until bug fix
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
    # first do right side
    with WorkingContext(str(mrs_dir)):
        try:
            rt_match_pfname = mrs_dir / appendposix(rt_matchfname, '.nii')
            rt_match_brain, rt_match_mask = extract_brain(str(rt_match_pfname))
            results += run_subprocess(['susan ' + str(rt_match_brain) + ' -1 1 3 1 0 ' + str(replacesuffix(rt_match_brain, '_susanf.nii.gz'))])
            rt_spar = readspar(str(replacesuffix(rt_actfname, '.SPAR')))

            rt_match_img = nib.load(str(replacesuffix(rt_match_brain, '_susanf.nii.gz')))
            rt_match_img_data = rt_match_img.get_data()
            rt_affine = rt_match_img.affine
            rt_mask_img = np.zeros(rt_match_img_data.shape, dtype='int32')
            rt_lr_diff = round((rt_spar['lr_size'] / 2.) / rt_match_img.header.get_zooms()[0])
            rt_ap_diff = round((rt_spar['ap_size'] / 2.) / rt_match_img.header.get_zooms()[1])
            rt_cc_diff = round((rt_spar['cc_size'] / 2.) / rt_match_img.header.get_zooms()[2])
            rt_startx = int((rt_match_img_data.shape[0] / 2.0) - lr_diff)
            rt_endx = int((rt_match_img_data.shape[0] / 2.0) + lr_diff)
            rt_starty = int((rt_match_img_data.shape[1] / 2.0) - ap_diff)
            rt_endy = int((rt_match_img_data.shape[1] / 2.0) + ap_diff)
            rt_startz = int((rt_match_img_data.shape[2] / 2.0) - cc_diff)
            rt_endz = int((rt_match_img_data.shape[2] / 2.0) + cc_diff)
            rt_mask_img[rt_startx:rt_endx, rt_starty:rt_endy, rt_startz:rt_endz] = 1
            savenii(rt_mask_img, rt_affine, str(mrs_dir / appendposix(rt_matchfname, '_mrs_roi_mask.nii.gz')), header=rt_match_img.header)
            prov.log(str(mrs_dir / appendposix(rt_matchfname, '_mrs_roi_mask.nii.gz')), 'rt sv mrs voi mask file created for csf fraction', str(replacesuffix(rt_actfname, '.SPAR')), script=__file__)
            # run spm segmentation
            #seg.inputs.data = str(replacesuffix(rt_match_brain, '_susanf.nii.gz'))
            #seg.run()
            fast.inputs.in_files = str(replacesuffix(rt_match_brain, '_susanf.nii.gz'))
            fast.inputs.out_basename = str(replacesuffix(rt_match_brain, '_susanf_fslfast'))
            fast.inputs.number_classes = 3
            fast.inputs.segments = True
            fast.inputs.img_type = 1
            fast.inputs.hyper = 0.1
            fast.inputs.bias_iters = 4
            fast.inputs.bias_lowpass = 20
            fast.inputs.output_biascorrected = True
            fast.inputs.output_biasfield = True
            fast.inputs.probability_maps = True
            fast.run()

            rt_GM_seg_data = nib.load(str(mrs_dir / str(replacesuffix(rt_match_brain, '_susanf_fslfast_seg_1.nii.gz')))).get_data()
            rt_GM_voi = rt_GM_seg_data * rt_mask_img
            rt_GM_num_vox = np.count_nonzero(rt_GM_voi)
            rt_WM_seg_data = nib.load(str(mrs_dir / str(replacesuffix(rt_match_brain, '_susanf_fslfast_seg_2.nii.gz')))).get_data()
            rt_WM_voi = rt_WM_seg_data * rt_mask_img
            rt_WM_num_vox = np.count_nonzero(rt_WM_voi)
            rt_CSF_seg_data = nib.load(str(mrs_dir / str(replacesuffix(rt_match_brain, '_susanf_fslfast_seg_0.nii.gz')))).get_data()
            rt_CSF_voi = rt_CSF_seg_data * rt_mask_img
            rt_CSF_num_vox = np.count_nonzero(rt_CSF_voi)
            rt_mask_num_vox = float(np.count_nonzero(rt_mask_img))
            
            lt_match_pfname = mrs_dir / appendposix(lt_matchfname, '.nii')
            lt_match_brain, lt_match_mask = extract_brain(str(lt_match_pfname))
            results += run_subprocess(['susan ' + str(lt_match_brain) + ' -1 1 3 1 0 ' + str(replacesuffix(lt_match_brain, '_susanf.nii.gz'))])
            lt_spar = readspar(str(replacesuffix(lt_actfname, '.SPAR')))

            lt_match_img = nib.load(str(replacesuffix(lt_match_brain, '_susanf.nii.gz')))
            lt_match_img_data = lt_match_img.get_data()
            lt_affine = lt_match_img.affine
            lt_mask_img = np.zeros(lt_match_img_data.shape, dtype='int32')
            lt_lr_diff = round((lt_spar['lr_size'] / 2.) / lt_match_img.header.get_zooms()[0])
            lt_ap_diff = round((lt_spar['ap_size'] / 2.) / lt_match_img.header.get_zooms()[1])
            lt_cc_diff = round((lt_spar['cc_size'] / 2.) / lt_match_img.header.get_zooms()[2])
            lt_startx = int((lt_match_img_data.shape[0] / 2.0) - lr_diff)
            lt_endx = int((lt_match_img_data.shape[0] / 2.0) + lr_diff)
            lt_starty = int((lt_match_img_data.shape[1] / 2.0) - ap_diff)
            lt_endy = int((lt_match_img_data.shape[1] / 2.0) + ap_diff)
            lt_startz = int((lt_match_img_data.shape[2] / 2.0) - cc_diff)
            lt_endz = int((lt_match_img_data.shape[2] / 2.0) + cc_diff)
            lt_mask_img[lt_startx:lt_endx, lt_starty:lt_endy, lt_startz:lt_endz] = 1
            savenii(lt_mask_img, lt_affine, str(mrs_dir / appendposix(lt_matchfname, '_mrs_roi_mask.nii.gz')), header=lt_match_img.header)
            prov.log(str(mrs_dir / appendposix(lt_matchfname, '_mrs_roi_mask.nii.gz')), 'rt sv mrs voi mask file created for csf fraction', str(replacesuffix(lt_actfname, '.SPAR')), script=__file__)
            # run spm segmentation
            #seg.inputs.data = str(replacesuffix(lt_match_brain, '_susanf.nii.gz'))
            #seg.run()
            fast.inputs.in_files = str(replacesuffix(lt_match_brain, '_susanf.nii.gz'))
            fast.inputs.out_basename = str(replacesuffix(lt_match_brain, '_susanf_fslfast'))
            fast.inputs.number_classes = 3
            fast.inputs.segments = True
            fast.inputs.img_type = 1
            fast.inputs.hyper = 0.1
            fast.inputs.bias_iters = 4
            fast.inputs.bias_lowpass = 20
            fast.inputs.output_biascorrected = True
            fast.inputs.output_biasfield = True
            fast.inputs.probability_maps = True
            fast.run()

            lt_GM_seg_data = nib.load(str(mrs_dir / str(replacesuffix(lt_match_brain, '_susanf_fslfast_seg_1.nii.gz')))).get_data()
            lt_GM_voi = lt_GM_seg_data * lt_mask_img
            lt_GM_num_vox = np.count_nonzero(lt_GM_voi)
            lt_WM_seg_data = nib.load(str(mrs_dir / str(replacesuffix(lt_match_brain, '_susanf_fslfast_seg_2.nii.gz')))).get_data()
            lt_WM_voi = lt_WM_seg_data * lt_mask_img
            lt_WM_num_vox = np.count_nonzero(lt_WM_voi)
            lt_CSF_seg_data = nib.load(str(mrs_dir / str(replacesuffix(lt_match_brain, '_susanf_fslfast_seg_0.nii.gz')))).get_data()
            lt_CSF_voi = lt_CSF_seg_data * lt_mask_img
            lt_CSF_num_vox = np.count_nonzero(lt_CSF_voi)
            lt_mask_num_vox = float(np.count_nonzero(lt_mask_img))

            with open(str(mrs_dir / str(subject + '_sv_voi_tissue_proportions.txt')), "w") as f:
                f.write('rt_CSF: {0}\nrt_GM: {1}\nrt_WM: {2}\n'.format('{:.3%}'.format(rt_CSF_num_vox / rt_mask_num_vox),
                                                              '{:.3%}'.format(rt_GM_num_vox / rt_mask_num_vox),
                                                              '{:.3%}'.format(rt_WM_num_vox / rt_mask_num_vox)))
                f.write('lt_CSF: {0}\nlt_GM: {1}\nlt_WM: {2}\n'.format('{:.3%}'.format(lt_CSF_num_vox / lt_mask_num_vox),
                                                              '{:.3%}'.format(lt_GM_num_vox / lt_mask_num_vox),
                                                              '{:.3%}'.format(lt_WM_num_vox / lt_mask_num_vox)))
                
        except:
            raise

# 
# prov.log(join(fs, project, subject, session, 'mrs', subject + side + '_match_sv_seg_0.nii'), 'CSF segmentation', brain_outfname, script=__file__)
# prov.log(join(fs, project, subject, session, 'mrs', subject + side + '_match_sv_seg_1.nii'), 'GM segmentation', brain_outfname, script=__file__)
# prov.log(join(fs, project, subject, session, 'mrs', subject + side + '_match_sv_seg_2.nii'), 'WM segmentation', brain_outfname, script=__file__)
# prov.log(join(fs, project, subject, session, 'mrs', subject + side + '_sv_voi_tissue_proportions.txt'), 'results file containing %tissue values', brain_outfname, script=__file__)
