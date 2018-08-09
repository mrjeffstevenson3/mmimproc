# todo: recode to exctract tracts from UKF whole brain.
import pylabs

import os, inspect
from pathlib import *
import datetime

from pylabs.correlation.atlas import make_mask_fm_atlas_parts, make_mask_fm_tracts
from pylabs.alignment.ants_reg import subj2templ_applywarp, subj2T1
from pylabs.projects.genz.file_names import get_dwi_names, Optsd, project, SubjIdPicks, get_vfa_names, merge_ftempl_dicts
from pylabs.utils import *
from pylabs.conversion.nifti2nrrd import nii2nrrd
from pylabs.diffusion.vol_into_vtk import inject_vol_data_into_vtk
#set up provenance
provenance = ProvenanceWrapper()
#setup paths and file names to process
fs = Path(getnetworkdataroot())
slicer_path = getslicercmd(ver='stable', stable_linux_ver='Slicer-4.8.1-linux-amd64')

mori_atlasd = {
    'mori_LeftPostIntCap-35': {'vtk_fname': '{subj}_{session}_ukf_mori_LeftPostIntCap-35.vtk', 'roi_list': [35], 'Sl_cmd': 'FiberBundleLabelSelect '},
    'mori_RightPostIntCap-123': {'vtk_fname': '{subj}_{session}_ukf_mori_RightPostIntCap-123.vtk', 'roi_list': [123], 'Sl_cmd': 'FiberBundleLabelSelect '},
    'mori_CC': {'vtk_fname': '{subj}_{session}_ukf_mori_bilatCC-52to54-140to142.vtk', 'roi_list': [52, 53, 54, 140, 141, 142], 'Sl_cmd': 'FiberBundleLabelSelect '},
    'mori_Left_IFOF-45-47': {'vtk_fname': '{subj}_{session}_ukf_mori_Left_IFOF-45-47.vtk', 'roi_list': [45, 47, 36], 'Sl_cmd': 'FiberBundleLabelSelect '},
    'mori_Right_IFOF-133-135': {'vtk_fname': '{subj}_{session}_ukf_mori_Right_IFOF-133-135.vtk', 'roi_list': [133, 135, 124], 'Sl_cmd': 'FiberBundleLabelSelect '},
    'mori_Left_SLF-43': {'vtk_fname': '{subj}_{session}_ukf_mori_Left_SLF-43.vtk', 'roi_list': [43], 'Sl_cmd': 'FiberBundleLabelSelect '},
    'mori_Right_SLF-131': {'vtk_fname': '{subj}_{session}_ukf_mori_Right_SLF-131.vtk', 'roi_list': [131], 'Sl_cmd': 'FiberBundleLabelSelect '},
    }

MNI_atlases = {'mori': {'atlas_fname': 'JHU_MNI_SS_WMPM_Type_I_matched.nii.gz', 'roi_list': None, 'Sl_cmd': None},
                'aal_motor': {'atlas_fname': 'aal_1mm_motorcortex.nii', 'roi_list': [1, 2, 3, 4, 7, 8, 19, 20, 23, 24, 57, 58, 59, 60, 61, 62, 63, 64, 69, 70], 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'mori_LeftPostIntCap-35': {'atlas_fname': 'mori_LeftPostIntCap-35.nii', 'roi_list': [35], 'Sl_cmd': 'TractographyLabelMapSeeding -m 2000 -l 2 -x -v 0.1 -a '},
                'mori_RightPostIntCap-123': {'atlas_fname': 'mori_RightPostIntCap-123.nii', 'roi_list': [123], 'Sl_cmd': 'TractographyLabelMapSeeding -m 2000 -l 2 -x -v 0.1 -a '},
                'mori_base_mask52only': {'atlas_fname': 'mori_base_mask52only.nii', 'roi_list': None, 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'mori_CC': {'atlas_fname': 'mori_bilatCC-52to54-140to142.nii', 'roi_list': [52, 53, 54, 140, 141, 142], 'Sl_cmd': 'TractographyLabelMapSeeding -m 2000 -l 2 -x -v 0.1 -a '},
                'mori_Left_IFOF-45-47': {'atlas_fname': 'mori_Left_IFOF-45-47.nii', 'roi_list': [45,47,36], 'Sl_cmd': 'TractographyLabelMapSeeding -m 2000 -l 2 -x -v 0.1 -a '},
                'mori_Right_IFOF-133-135': {'atlas_fname': 'mori_Right_IFOF-133-135.nii', 'roi_list': [133, 135, 124],  'Sl_cmd': 'TractographyLabelMapSeeding -m 2000 -l 2 -x -v 0.1 -a '},
                'mori_Left_frontal-3-5': {'atlas_fname': 'mori_Left_frontal-3-5.nii', 'roi_list': [3,4,5], 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'mori_Left_occip-10-14-16': {'atlas_fname': 'mori_Left_occip-10-16-20.nii', 'roi_list': [10,14,15,16], 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'mori_Right_frontal-91-93': {'atlas_fname': 'mori_Right_frontal-91-93.nii', 'roi_list': [91,92,93], 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'mori_Right_occip-98-102-103-104': {'atlas_fname': 'mori_Right_occip-98-99-102-104.nii', 'roi_list': [104,103,98,102], 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'mori_Left_SLF-43':  {'atlas_fname': 'mori_Left_SLF-43.nii', 'roi_list': [43], 'Sl_cmd': 'TractographyLabelMapSeeding -m 2000 -l 2 -x -v 0.1 -a '},
                'mori_Right_SLF-131': {'atlas_fname': 'mori_Right_SLF-131.nii', 'roi_list': [131], 'Sl_cmd': 'TractographyLabelMapSeeding -m 2000 -l 2 -x -v 0.1 -a '},
                'mori_Left_pre-postCentGyr-6-7': {'atlas_fname': 'mori_Left_pre-postCentGyr-6-7.nii', 'roi_list': [6, 7], 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'mori_Right_pre-postCentGyr-94-95': {'atlas_fname': 'mori_Right_pre-postCentGyr-94-95.nii', 'roi_list': [94,95], 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'mori_Left_STG-MTG-18-20':  {'atlas_fname': 'mori_Left_STG-MTG-18-20.nii', 'roi_list': [20,18], 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'mori_Right_STG-MTG-106-108': {'atlas_fname': 'mori_Right_STG-MTG-106-108.nii', 'roi_list': [106,108], 'Sl_cmd': 'ModelMaker -l 1 -n '},

                'JHU_tracts_Left_ATR-1': {'atlas_fname': 'JHU_tracts_thr%(JHU_thr)s_Left_ATR-1.nii', 'roi_list': 1, 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'JHU_tracts_Right_ATR-2': {'atlas_fname': 'JHU_tracts_thr%(JHU_thr)s_Right_ATR-2.nii', 'roi_list': 2, 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'JHU_tracts_Left_CSP-3': {'atlas_fname': 'JHU_tracts_thr%(JHU_thr)s_Left_CSP-3.nii', 'roi_list': 3, 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'JHU_tracts_Right_CSP-4': {'atlas_fname': 'JHU_tracts_thr%(JHU_thr)s_Right_CSP-4.nii', 'roi_list': 4, 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'JHU_tracts_Left_Cing-5': {'atlas_fname': 'JHU_tracts_thr%(JHU_thr)s_Left_Cing-5.nii', 'roi_list': 5, 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'JHU_tracts_Right_Cing-6': {'atlas_fname': 'JHU_tracts_thr%(JHU_thr)s_Right_Cing-6.nii', 'roi_list': 6, 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'JHU_tracts_Forceps_Major-9': {'atlas_fname': 'JHU_tracts_thr%(JHU_thr)s_Forceps_Major-9.nii', 'roi_list': 9, 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'JHU_tracts_Forceps_Minor-10': {'atlas_fname': 'JHU_tracts_thr%(JHU_thr)s_Forceps_Minor-10.nii', 'roi_list': 10, 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'JHU_tracts_Left_IFOF-11': {'atlas_fname': 'JHU_tracts_thr%(JHU_thr)s_Left_IFOF-11.nii', 'roi_list': 11, 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'JHU_tracts_Right_IFOF-12':  {'atlas_fname': 'JHU_tracts_thr%(JHU_thr)s_Right_IFOF-12.nii', 'roi_list': 12, 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'JHU_tracts_Left_ILF-13': {'atlas_fname': 'JHU_tracts_thr%(JHU_thr)s_Left_ILF-13.nii', 'roi_list': 13, 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'JHU_tracts_Right_ILF-14': {'atlas_fname': 'JHU_tracts_thr%(JHU_thr)s_Right_ILF-14.nii', 'roi_list': 14, 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'JHU_tracts_Left_SLF-15': {'atlas_fname': 'JHU_tracts_thr%(JHU_thr)s_Left_SLF-15.nii', 'roi_list': 15, 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'JHU_tracts_Right_SLF-16': {'atlas_fname': 'JHU_tracts_thr%(JHU_thr)s_Right_SLF-16.nii', 'roi_list': 16, 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'JHU_tracts_Left_Unc-17': {'atlas_fname': 'JHU_tracts_thr%(JHU_thr)s_Left_Unc-17.nii', 'roi_list': 17, 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'JHU_tracts_Right_Unc-18': {'atlas_fname': 'JHU_tracts_thr%(JHU_thr)s_Right_Unc-18.nii', 'roi_list': 18, 'Sl_cmd': 'ModelMaker -l 1 -n '},

                # 'stats_vbm_WM_s2'  : {'atlas_fname': 'all_WM_mod_s2_n10000_exchbl_tfce_corrp_tstat2.nii.gz', 'roi_list': 1, 'Sl_cmd': 'UKFTractography --dwiFile %(fdwinrrd)s --seedsFile %(seed_fnamenrrd)s --labels 1 --maskFile %(mask_fnamenrrd)s --tracts %(dwif)s_UKF_whbr.vtk '
                #                      '--seedsPerVoxel 1 --seedFALimit 0.18 --minFA 0.15 --minGA 0.2 --numThreads -1 --numTensor 2 --stepLength 0.3 --Qm 0 --recordLength 0.9 --maxHalfFiberLength 250 --recordNMSE --freeWater '
                #                      '--recordFA --recordTrace --recordFreeWater --recordTensors --Ql 0 --Qw 0 --Qkappa 0.01 --Qvic 0.004 --Rs 0 --sigmaSignal 0 --maxBranchingAngle 0 --minBranchingAngle 0'},
                }

# tensors = {'RESTORE':['_eddy_corrected_repol_std2_restore_cam_tensor_medfilt.nhdr', '_eddy_corrected_repol_std2_restore_cam_tensor.nhdr', '_eddy_corrected_repol_std2_restore_dipy_tensor.nhdr', '_eddy_corrected_repol_std2_restore_dipy_tensor_medfilt.nhdr'],
#             'OLS': ['_eddy_corrected_repol_std2_ols_fsl_tensor_medfilt.nhdr', '_eddy_corrected_repol_std2_ols_fsl_tensor.nhdr', '_eddy_corrected_repol_std2_ols_dipy_tensor.nhdr', '_eddy_corrected_repol_std2_ols_dipy_tensor_medfilt.nhdr', '_eddy_corrected_repol_std2_ols_cam_tensor.nhdr', '_eddy_corrected_repol_std2_ols_cam_tensor_medfilt.nhdr'],
#             'WLS': ['_eddy_corrected_repol_std2_wls_fsl_tensor_medfilt.nhdr', '_eddy_corrected_repol_std2_wls_fsl_tensor.nhdr', '_eddy_corrected_repol_std2_wls_dipy_tensor.nhdr', '_eddy_corrected_repol_std2_wls_dipy_tensor_medfilt.nhdr', '_eddy_corrected_repol_std2_wls_cam_tensor.nhdr', '_eddy_corrected_repol_std2_wls_cam_tensor_medfilt.nhdr']
#             }

#set project specific files
subjids_picks = SubjIdPicks()
opts = Optsd()
# must set fas mannually when patch used. not reported in PAR file correctly.
picks = [
        {'patch': True, 'project': project, 'subj': 'sub-genz510', 'session': 'ses-1', 'run': '1', 'fas': [4.0, 25.0],},
        {'patch': True, 'project': project, 'subj': 'sub-genz508', 'session': 'ses-1', 'run': '1', 'fas': [4.0, 25.0],},
        {'patch': True, 'project': project, 'subj': 'sub-genz501', 'session': 'ses-1', 'run': '1', 'fas': [4.0, 25.0],},
        {'patch': True, 'project': project, 'subj': 'sub-genz308', 'session': 'ses-1', 'run': '1', 'fas': [4.0, 25.0],},
        {'patch': True, 'project': project, 'subj': 'sub-genz311', 'session': 'ses-1', 'run': '1', 'fas': [4.0, 25.0],},
         ]
setattr(subjids_picks, 'subjids', picks)

dwi_picks, qt1_picks  =  get_dwi_names(subjids_picks), get_vfa_names(subjids_picks)
if dwi_picks == qt1_picks:
    picks = qt1_picks
else:
    raise ValueError('dwi and qt1 picks dict not aligned. stopping.')

opts.inject_qt1 = True

opts.test = True
if opts.test:
    i = 0
    picks = [picks[i]]

# ec_meth = 'cuda_repol_std2_S0mf3_v5'
# fa2t1_outdir = 'reg_subFA2suborigvbmpaired_run2'
# fadir = 'FA_fsl_wls_tensor_mf_ero_paired'
# dwi_templ = 'sub-bbc{sid}_ses-{snum}_{meth}_{runnum}'
#
# vbm_templ = 'bbc_pairedLH_sub-bbc{sid}_ses-{snum}_{meth}_{runnum}_brain_susan_nl_comroll'
#
# templdir = fs / project / 'reg' / 'ants_vbm_pairedLH_in_template_space'
# vbm_statsdir = templdir / 'stats' / 'exchblks'
# MNI2templ_invwarp = templdir / 'bbc_pairedLH_template_reg2MNI_1InverseWarp.nii.gz'
# MNI2templ_aff = templdir / 'bbc_pairedLH_template_reg2MNI_0GenericAffine.mat'
# dwi2vbmsubjdir = fs / project / 'reg' / 'reg_subFA2suborigvbmpaired_run2'
# dwi_reg_append = '_eddy_corrected_repol_std2_wls_fsl_tensor_mf_FA_ero_reg2sorigvbm_'



#apply the warps
for pick in picks:
    output = tuple()
    print('Woking on subject {subj} session {session}'.format(**pick))
    # first warp MNI atlases to dwi space
    reg_dir = Path(fs/project/'{subj}/{session}/reg/MNI2dwi'.format(**pick))
    dwi_dir = Path(fs/project/'{subj}/{session}/dwi/{dwi_fits_dir}'.format(**merge_ftempl_dicts(dict1=pick, dict2=vars(opts))))
    vtk_dir = Path(fs/project/'{subj}/{session}/dwi/{vtk_dir}'.format(**merge_ftempl_dicts(dict1=pick, dict2=vars(opts))))
    if not vtk_dir.is_dir():
        vtk_dir.mkdir(parents=True)
        # ukf_fname = Path(fs/project/'{subj}/{session}/dwi/{dwi_fits_dir}/vtk/'.format(**merge_ftempl_dicts(dict1=pick, dict2=vars(opts))))
    if not reg_dir.is_dir():
        reg_dir.mkdir(parents=True)
    mori_in_vtk_dir = vtk_dir / appendposix(moriMNIatlas.name, '_reg2dwi')
    ref = dwi_dir / '{subj}_{session}_dwi_unwarped_ec_fslfit_tensor_mf_S0.nii.gz'.format(**pick)
    if not (replacesuffix(mori_in_vtk_dir, '.nrrd')).is_file():
        with WorkingContext(reg_dir):
            moving = MNI1mm_T2_brain_dwi
            out_fname = reg_dir/replacesuffix(MNI1mm_T2_brain_dwi.name, '_reg2dwi_')
            subj2T1(moving, ref, out_fname, inargs=opts.ants_args)
            warpfiles = [str(reg_dir/replacesuffix(MNI1mm_T2_brain_dwi.name, '_reg2dwi_1Warp.nii.gz'))]
            affine_xfm = [str(reg_dir/replacesuffix(MNI1mm_T2_brain_dwi.name, '_reg2dwi_0GenericAffine.mat'))]
            output += subj2templ_applywarp(moriMNIatlas, ref, dwi_dir/appendposix(moriMNIatlas.name, '_reg2dwi'), warpfiles, dwi_dir, affine_xform=affine_xfm)
            mori_in_vtk_dir.symlink_to(dwi_dir/appendposix(moriMNIatlas.name, '_reg2dwi'))
            nii2nrrd(mori_in_vtk_dir, replacesuffix(mori_in_vtk_dir, '.nrrd'), ismask=True)

    with WorkingContext(vtk_dir):
        if opts.inject_qt1:
            qt1_fname = fs/project/'{subj}/{session}/qt1/{subj}_{session}_vfa_qt1_b1corrmf_vlinregr-fit_clamped.nii'.format(**pick)
            vol_in = '{subj}_{session}_vfa_qt1_b1corrmf_vlinregr-fit_clamped_reg2dwi_Warped.nii.gz'
            if not qt1_fname.is_file():
                raise ValueError('cannot find qt1 file '+str(qt1_fname))
            if not Path(vol_in).is_file():
                print('moving qt1 to dwi space.')
                qt1_fnamevtk = vtk_dir/'{subj}_{session}_vfa_qt1_b1corrmf_vlinregr-fit_clamped.nii'.format(**pick)
                qt1_fnamevtk.symlinc_to(qt1_fname)
                subj2T1(qt1_fnamevtk, ref, replacesuffix(qt1_fname.name, '_reg2dwi_'), inargs=opts.ants_args)
            vtk_in = '{subj}_{session}_dwi-topup_64dir-3sh-800-2000_1_topdn_unwarped_ec_mf_clamp1_UKF_whbr.vtk'
            vtk_out = appendposix(vtk_in, '_qt1-inj')
            inject_vol_data_into_vtk(Path('.'), vol_in, vtk_in, vtk_out)
        for k, a in mori_atlasd.iteritems():
            cmd = str(slicer_path)+a['Sl_cmd']+'-p '+','.join([str(x) for x in a['roi_list']])+' '+str(replacesuffix(mori_in_vtk_dir, '.nrrd'))
            cmd += ' '+'{subj}_{session}_dwi-topup_64dir-3sh-800-2000_1_topdn_unwarped_ec_mf_clamp1_UKF_whbr.vtk'.format(**pick)
            cmd += ' '+'{subj}_{session}_dwi-topup_64dir-3sh-800-2000_1_topdn_unwarped_ec_mf_clamp1_UKF_whbr_'.format(**pick)+k+'.vtk'





            # extract rois from atlases and make masks
            if 'mori_' in k:
                make_mask_fm_atlas_parts(atlas=str(mori_in_vtk_dir), roi_list=a['roi_list'], mask_fname=str(a['atlas_fname']), makenrrd=True)


            make_mask_fm_atlas_parts(atlas=str(moriMNIatlas), roi_list=a['roi_list'], mask_fname=str(pylabs_atlasdir / a['atlas_fname']))
        elif 'JHU_' in k:
            make_mask_fm_tracts(atlas=str(JHUtracts_prob_atlas), volidx=a['roi_list'], thresh=JHU_thr, mask_fname=str(pylabs_atlasdir / (a['atlas_fname'] % JHU_thr)))
        elif 'aal_motor' in k:
            make_mask_fm_atlas_parts(atlas=str(pylabs_atlasdir / 'aal_1mm_reg2MNI_masked.nii.gz'), roi_list=a['roi_list'], mask_fname=str(pylabs_atlasdir / a['atlas_fname']))
        elif 'stats' in k:
            make_mask_fm_tracts(atlas=str(vbm_statsdir / a['atlas_fname']), volidx=a['roi_list'], thresh=stat_thr, mask_fname=str(pylabs_atlasdir / (a['atlas_fname'].split('.')[0]+'_thr%(fn_thr)s_bin.nii.gz' % stat_thr)))
        execwdir = fs / project / dwif.split('_')[0] / dwif.split('_')[1] / 'dwi'

        if 'mori' in k or 'aal_motor' in k:
            mov = pylabs_atlasdir / a['atlas_fname']
            outf = execwdir / str(dwif+'_'+k+'.nii')
        if 'JHU_' in k:
            mov = pylabs_atlasdir / (a['atlas_fname'] % JHU_thr)
            outf = execwdir / str(dwif+'_'+ (a['atlas_fname'] % JHU_thr))
        if 'stats' in k:
            mov = vbm_statsdir / (a['atlas_fname'].split('.')[0]+'_thr%(fn_thr)s_bin.nii.gz' % stat_thr)
            outf = execwdir / str(dwif+'_'+ (a['atlas_fname'].split('.')[0]+'_thr%(fn_thr)s_bin.nii.gz' % stat_thr))
        iwarp_templ2vbmsubj = templdir / str(vbmf+'InverseWarp.nii.gz')
        iwarp_vbmsub2dwi = dwi2vbmsubjdir / str(dwif+ dwi_reg_append +'1InverseWarp.nii.gz')
        aff_templ2vbmsubj = templdir / str(vbmf+'Affine.txt')
        aff_vbmsub2dwi = dwi2vbmsubjdir / str(dwif + dwi_reg_append + '0GenericAffine.mat')
        warpfiles = [str(MNI2templ_invwarp), str(iwarp_templ2vbmsubj), str(iwarp_vbmsub2dwi)]
        affine_xform = [str(MNI2templ_aff), str(aff_templ2vbmsubj), str(aff_vbmsub2dwi)]
        if 'stats' in k:  # this is because stats are already in template space so no MNI warps needed.
            warpfiles = warpfiles[1:]
            affine_xform = affine_xform[1:]
        subj2templ_applywarp(str(mov), str(ref), str(outf), warpfiles, str(execwdir), affine_xform=affine_xform, inv=True)
        nii2nrrd(str(outf), str(outf).replace('.nii','.nhdr'), ismask=True)
        vtkdir = execwdir / 'vtk_tensor_comp_run7'
        if not vtkdir.is_dir():
            vtkdir.mkdir()
        #recoded till here
        try:
            if not a['Sl_cmd'] == None and 'stats_vbm' not in k:
                if a['Sl_cmd'] == 'ModelMaker -l 1 -n ':
                    cmd = ''
                    cmd += str(slicer_path) + a['Sl_cmd']
                    if 'mori' in k or 'aal_motor' in k:
                        cmd += str(vtkdir / str(dwif + '_' + k))
                    if 'JHU_' in k:
                        cmd += str(vtkdir / str(dwif + '_' + (a['atlas_fname'] % JHU_thr).split('.')[0]))
                    cmd += ' '+ str(outf)
                    output = ()
                    dt = datetime.datetime.now()
                    output += (str(dt),)
                    cmdt = (cmd,)
                    output += cmdt
                    with WorkingContext(str(execwdir)):
                        print(cmd)
                        output += run_subprocess(cmd)
                    params = {}
                    params['cmd'] = cmd
                    params['output'] = output
                    if 'mori' in k or 'aal_motor' in k:
                        provenance.log(str(vtkdir / str(dwif+'_'+k+'.vtk')), 'generate model vtk', str(outf), script=__file__, provenance=params)
                    elif 'JHU_' in k:
                        provenance.log(str(vtkdir / str(dwif + '_' + (a['atlas_fname'] % JHU_thr).split('.')[0]) + '.vtk'), 'generate model vtk', str(outf), script=__file__, provenance=params)
                elif 'stats' not in k:
                    for m, ts in tensors.iteritems():
                        tenpath = execwdir / opts.eddy_corr_dir
                        for t in ts:
                            cmd = ''
                            cmd += str(slicer_path) + a['Sl_cmd']
                            cmd += str(outf)+' '+str(tenpath / str(dwif+t))+' '+str(vtkdir / str(dwif+t.split('.')[0]+'_'+k))+'.vtk'
                            output = ()
                            dt = datetime.datetime.now()
                            output += (str(dt),)
                            cmdt = (cmd,)
                            output += cmdt
                            with WorkingContext(str(execwdir)):
                                print(cmd)
                                output += run_subprocess(cmd)
                            params = {}
                            params['cmd'] = cmd
                            params['output'] = output
                            provenance.log(str(vtkdir / str(dwif+t.split('.')[0]+'_'+k))+'.vtk', 'generate fiberbundle vtk from tensors', [str(outf), str(tenpath / str(dwif+t))] , script=__file__, provenance=params)
                elif 'stats' in k:
                    # sets up variables to combine with MNI_atlases dict
                    cmdvars = {'mask_fname': str(mask_fname), 'm': m.lower(), 'dwif': dwif,
                               'fdwinrrd': str(outf).replace('.nii','.nhdr'),
                               'seed_fnamenrrd': str(outf).replace('.nii', '.nhdr')}

                    with WorkingContext(m):
                        output += tuple(run_subprocess(MNI_atlases[a]['Sl_cmd'] % cmdvars))


        except:
            print "exception caught for "+dwif+". Missing "+k+" for "+' '.join(list(a))+" or "+m
