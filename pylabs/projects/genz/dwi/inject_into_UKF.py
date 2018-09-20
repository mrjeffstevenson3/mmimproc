# inject R1 and MPF into UKF
from pathlib import *
from pylabs.utils import *
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
        {'run': '1', 'session': 'ses-1', 'subj': 'sub-genz311'},
        ]
setattr(subjids_picks, 'subjids', picks)
setattr(subjids_picks, 'getR1_MPF_names', True)
r1_fname_templ = '{subj}_{session}_vasily_r1_sep06_2018_ras'
mpf_fname_templ = '{subj}_{session}_vasily_mpf_sep06_2018_ras'
setattr(subjids_picks, 'r1_fname_templ', r1_fname_templ)
setattr(subjids_picks, 'mpf_fname_templ', mpf_fname_templ)
qt1_picks = get_vfa_names(subjids_picks)
results = ('',)
errors = ('',)
for pick in qt1_picks:
    print('Working on {subj} and {session}'.format(**pick))
    if not pick['qt1_dir'].is_dir():
        pick['qt1_dir'].mkdir(parents=True)
        raise ValueError('missing qt1 directory and hense files. please check for {subj} in {session}/qt1')
    with WorkingContext(pick['qt1_dir']):
        pick['vfa_ec-1_fname'] = pick['vfa_fname'].replace('fa-4-25', 'ec-1-fa-4')
        results += run_subprocess([' '.join(['fslroi', pick['vfa_fname'], pick['vfa_ec-1_fname'], '0 1'])])
        pick['vfa_ec-1_N4bias_fname'] = pick['vfa_ec-1_fname'] + '_N4bias' + opts.ext
        results += run_subprocess([antsN4bias_cmd.format(**{'infile': pick['vfa_ec-1_fname'] + opts.ext, 'outfile':pick['vfa_ec-1_N4bias_fname']})])
        vfa_brain_fname, vfa_brain_mask_fname, vfa_brain_cropped_fname = extract_brain(pick['vfa_ec-1_N4bias_fname'], mode='T2', f_factor=0.5, robust=True)
        results += run_subprocess([' '.join(['fslmaths', str(vfa_brain_mask_fname), '-ero -ero', str(appendposix(vfa_brain_mask_fname, '_ero2'))])])
        results += run_subprocess([' '.join(['fslmaths', pick['r1_fname'], '-mas', str(appendposix(vfa_brain_mask_fname, '_ero2')), pick['r1_fname'] + '_brain'])])
        results += run_subprocess([' '.join(['fslmaths', pick['mpf_fname'], '-mas', str(appendposix(vfa_brain_mask_fname, '_ero2')), pick['mpf_fname'] + '_brain'])])
    if not pick['reg2dwi_dir'].is_dir():
        pick['reg2dwi_dir'].mkdir(parents=True)
    if not pick['vtk_dir'].is_dir():
        pick['vtk_dir'].mkdir(parents=True)
    with WorkingContext(pick['reg2dwi_dir']):
        pick['moving'] = pick['qt1_dir'] / '{r1_fname}_brain.nii.gz'.format(**pick)
        reslice_niivol(pick['moving'], pick['dwi_dir'] / '{topup_brain_fname}.nii.gz'.format(**pick),  pick['dwi_dir'] / '{topup_brain_fname}_resampled2qt1.nii.gz'.format(**pick))
        pick['fixed'] = pick['dwi_dir'] / '{topup_brain_fname}_resampled2qt1.nii.gz'.format(**pick)
        pick['outfile'] = pick['reg2dwi_dir'].joinpath(pick['r1_fname'] + '_brain_reg2resampleddwi_')
        results += run_subprocess([antsRegistrationSyN_cmd.format(**pick)])
        with WorkingContext(pick['vtk_dir']):
            results += run_subprocess(['ln -sf ../../reg/{qt12dwi_reg_dir}/{outfile}Warped.nii.gz {r1_fname}_brain_reg2resampleddwi.nii.gz'.format(**merge_ftempl_dicts(pick, vars(opts)))])
        pick['moving'] = pick['qt1_dir'] / '{mpf_fname}_brain.nii.gz'.format(**pick)
        pick['outfile'] = pick['reg2dwi_dir'].joinpath(pick['mpf_fname'] + '_brain_reg2resampleddwi_')
        results += run_subprocess([antsRegistrationSyN_cmd.format(**pick)])
        with WorkingContext(pick['vtk_dir']):
            results += run_subprocess(['ln -sf ../../reg/{qt12dwi_reg_dir}/{outfile}Warped.nii.gz {mpf_fname}_brain_reg2resampleddwi.nii.gz'.format(**merge_ftempl_dicts(pick, vars(opts)))])
    try:
        with WorkingContext(pick['vtk_dir']):
            print('Injecting {UKF_fname} for {subj} and {session} with {r1_fname}'.format(**pick))
            inject_vol_data_into_vtk(Path('.'), '{r1_fname}_brain_reg2resampleddwi.nii.gz'.format(**pick), pick['UKF_fname'], replacesuffix(pick['UKF_fname'], '_resampledB0_injectR1.vtk'))
            print('Injecting {UKF_fname} for {subj} and {session} with {mpf_fname}'.format(**pick))
            inject_vol_data_into_vtk(Path('.'), '{mpf_fname}_brain_reg2resampleddwi.nii.gz'.format(**pick), pick['UKF_fname'], replacesuffix(pick['UKF_fname'], '_resampledB0_injectMPF.vtk'))
            print('Calculating Myelin Water Fraction for {subj} and {session} with {mpf_fname}'.format(**pick))
            results += run_subprocess([str(vol2myelin_density)])
            mwf_fname = replacesuffix(pick['UKF_fname'], '_resampledB0_injectMyelinWaterFrac.vtk')
            Path('fnew.vtk').rename(mwf_fname)
            print('Successful Injection of {UKF_fname} for {subj} and {session} with {r1_fname} and {mpf_fname}'.format(**pick))
    except:
        print('injection failed with errors for {subj} and {session} on vtk file {UKF_fname} and injection file {r1_fname} or {mpf_fname}.'.format(**pick))
        errors += ('injection failed with errors for {subj} and {session} on vtk file {UKF_fname} and injection file {r1_fname} or {mpf_fname}.\n'.format(**pick),)
        print(results)

print(errors)

