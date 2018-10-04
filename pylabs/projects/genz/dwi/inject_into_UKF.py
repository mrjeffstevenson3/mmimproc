# inject R1 and MPF into UKF
from pathlib import *
from pylabs.utils import *
from pylabs.conversion.analyze import reorient_img_with_pr_affine
from pylabs.io.mixed import get_pr_affine_fromh5
from pylabs.diffusion.vol_into_vtk import inject_vol_data_into_vtk
from pylabs.structural.brain_extraction import extract_brain
from pylabs.alignment.resample import reslice_niivol
from pylabs.projects.genz.file_names import SubjIdPicks, Optsd, get_vfa_names, merge_ftempl_dicts
antsRegistrationSyN_cmd = get_antsregsyn_cmd(default_cmd_str=True)
antsN4bias_cmd = get_antsregsyn_cmd(N4bias=True, default_cmd_str=True)
project = 'genz'
subjids_picks = SubjIdPicks()
opts = Optsd()
picks = [
        {'run': '1', 'session': 'ses-1', 'subj': 'sub-genz205'},
        ]
setattr(subjids_picks, 'subjids', picks)
setattr(subjids_picks, 'getR1_MPF_nii_fnames', True)
setattr(subjids_picks, 'get_analyse_R1_MPF_names', True)

r1_fname_templ = '{subj}_{session}_vasily_r1_ras'
mpf_fname_templ = '{subj}_{session}_vasily_mpf_ras'
orig_r1_fname_templ = 'R1_{subj}_WIP_VFA_FA4-25_QUIET-adolescents_SENSE_{wild}.img'  # get file name to match PAR file
orig_mpf_fname_templ = 'MPF{subj}_WIP_VFA_FA4-25_QUIET-adolescents_SENSE_{wild}.img'

setattr(subjids_picks, 'r1_fname_templ', r1_fname_templ)
setattr(subjids_picks, 'mpf_fname_templ', mpf_fname_templ)
setattr(subjids_picks, 'orig_r1_fname_templ', orig_r1_fname_templ)
setattr(subjids_picks, 'orig_mpf_fname_templ', orig_mpf_fname_templ)

qt1_picks = get_vfa_names(subjids_picks)

results = ('',)
errors = ('',)

for pick in qt1_picks:
    print('Working on {subj} and {session}'.format(**pick))
    pick['ext'] = opts.ext
    if not pick['qt1_path'].is_dir():
        pick['qt1_path'].mkdir(parents=True)
        raise ValueError('missing qt1 directory and hence qt1 files. please check for {subj} in {session}/qt1'.format(**pick))
    # convert R1 and MPF to nifti
    pr_affine = get_pr_affine_fromh5(opts.info_fname, pick['subj'], pick['session'], 'qt1', pick['vfa_fname'])
    reorient_img_with_pr_affine(pick['orig_r1_fname'], pr_affine, pr_shape=opts.vfa_pr_shape, out_nii_fname=pick['qt1_path']/(pick['r1_fname']+opts.ext), mpf_dtype=opts.mpf_img_dtype)
    reorient_img_with_pr_affine(pick['orig_mpf_fname'], pr_affine, pr_shape=opts.vfa_pr_shape, out_nii_fname=pick['qt1_path']/(pick['mpf_fname']+opts.ext), mpf_dtype=opts.mpf_img_dtype)
    with WorkingContext(pick['qt1_path']):
        pick['vfa_ec-1_fname'] = pick['vfa_fname'].replace('fa-4-25', 'ec-1-fa-4')
        results += run_subprocess([' '.join(['fslroi', pick['vfa_fname'], pick['vfa_ec-1_fname'], '0 1'])])
        pick['vfa_ec-1_N4bias_fname'] = pick['vfa_ec-1_fname'] + '_N4bias' + opts.ext
        results += run_subprocess([antsN4bias_cmd.format(**{'infile': pick['vfa_ec-1_fname'] + opts.ext, 'outfile':pick['vfa_ec-1_N4bias_fname']})])
        vfa_brain_fname, vfa_brain_mask_fname, vfa_brain_cropped_fname = extract_brain(pick['vfa_ec-1_N4bias_fname'], mode='T2', f_factor=0.5, robust=True)
        results += run_subprocess([' '.join(['fslmaths', str(vfa_brain_mask_fname), '-ero -ero', str(appendposix(vfa_brain_mask_fname, '_ero2'))])])
        pick['r1_brain_fname'], pick['mpf_brain_fname'] = pick['r1_fname']+ '_brain', pick['mpf_fname']+ '_brain'
        results += run_subprocess([' '.join(['fslmaths', pick['r1_fname'], '-mas', str(appendposix(vfa_brain_mask_fname, '_ero2')), str(pick['r1_brain_fname'])])])
        results += run_subprocess([' '.join(['fslmaths', pick['mpf_fname'], '-mas', str(appendposix(vfa_brain_mask_fname, '_ero2')), str(pick['mpf_brain_fname'])])])
        with WorkingContext(pick['vtk_path']):
            results += run_subprocess(['ln -sf ../../qt1/{r1_brain_fname}{ext} {r1_brain_fname}{ext}'.format(**pick)])
            results += run_subprocess(['ln -sf ../../qt1/{mpf_brain_fname}{ext} {mpf_brain_fname}{ext}'.format(**pick)])
    if not pick['reg2dwi_path'].is_dir():
        pick['reg2dwi_path'].mkdir(parents=True)
    if not pick['vtk_path'].is_dir():
        pick['vtk_path'].mkdir(parents=True)
    with WorkingContext(pick['reg2dwi_path']):
        pick['moving'] = pick['qt1_path'] / (pick['r1_brain_fname']+opts.ext)
        reslice_niivol(pick['moving'], pick['dwi_path'] / '{topup_brain_fname}.nii.gz'.format(**pick),  pick['dwi_path'] / '{topup_brain_fname}_resampled2qt1.nii.gz'.format(**pick))
        pick['fixed'] = pick['dwi_path'] / '{topup_brain_fname}_resampled2qt1.nii.gz'.format(**pick)
        pick['outfile'] = pick['reg2dwi_path'].joinpath(pick['r1_brain_fname'] + '_reg2resampleddwi_')
        results += run_subprocess([antsRegistrationSyN_cmd.format(**pick)])
        with WorkingContext(pick['vtk_path']):
            results += run_subprocess(['ln -sf ../../reg/{qt12dwi_reg_dir}/{outfile}Warped.nii.gz {r1_brain_fname}_reg2resampleddwi{ext}'.format(**merge_ftempl_dicts(pick, vars(opts), {'outfile': pick['outfile'].name}))])
        pick['moving'] = pick['qt1_path'] / '{mpf_brain_fname}{ext}'.format(**pick)
        pick['outfile'] = pick['reg2dwi_path'].joinpath(pick['mpf_brain_fname'] + '_reg2resampleddwi_')
        results += run_subprocess([antsRegistrationSyN_cmd.format(**pick)])
        with WorkingContext(pick['vtk_path']):
            results += run_subprocess(['ln -sf ../../reg/{qt12dwi_reg_dir}/{outfile}Warped.nii.gz {mpf_brain_fname}_reg2resampleddwi{ext}'.format(**merge_ftempl_dicts(pick, vars(opts), {'outfile': pick['outfile'].name}))])
    try:
        with WorkingContext(pick['vtk_path']):
            print('Injecting {UKF_fname} for {subj} and {session} with {r1_brain_fname}'.format(**pick))
            inject_vol_data_into_vtk(Path('.'), '{r1_brain_fname}_reg2resampleddwi{ext}'.format(**pick), pick['UKF_fname'], replacesuffix(pick['UKF_fname'], '_resampledB0_injectR1.vtk'))
            print('Injecting {UKF_fname} for {subj} and {session} with {mpf_brain_fname}'.format(**pick))
            inject_vol_data_into_vtk(Path('.'), '{mpf_brain_fname}_reg2resampleddwi{ext}'.format(**pick), pick['UKF_fname'], replacesuffix(pick['UKF_fname'], '_resampledB0_injectMPF.vtk'))
            print('Calculating Myelin Water Fraction for {subj} and {session} with {mpf_brain_fname}'.format(**pick))
            results += run_subprocess([str(vol2myelin_density)])
            mwf_fname = replacesuffix(pick['UKF_fname'], '_resampledB0_injectMyelinWaterFrac.vtk')
            Path('fnew.vtk').rename(mwf_fname)
            print('Successful Injection of {UKF_fname} for {subj} and {session} with {r1_brain_fname} and {mpf_brain_fname}'.format(**pick))
    except:
        print('injection failed with errors for {subj} and {session} on vtk file {UKF_fname} and injection file {r1_brain_fname} or {mpf_brain_fname}.'.format(**pick))
        errors += ('injection failed with errors for {subj} and {session} on vtk file {UKF_fname} and injection file {r1_brain_fname} or {mpf_brain_fname}.\n'.format(**pick),)
        print(' \n'.join(results))

print(' \n'.join(errors))
