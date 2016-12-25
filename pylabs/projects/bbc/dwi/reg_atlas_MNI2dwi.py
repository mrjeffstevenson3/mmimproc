import os, inspect
from pathlib import *
import datetime
import pylabs
from pylabs.correlation.atlas import make_mask_fm_atlas_parts, make_mask_fm_tracts
from pylabs.alignment.ants_reg import subj2templ_applywarp
from pylabs.projects.bbc.pairing import vbmpairing, dwipairing
from pylabs.utils.paths import getnetworkdataroot
from pylabs.utils import run_subprocess, WorkingContext
#set up provenance
from pylabs.utils.provenance import ProvenanceWrapper
provenance = ProvenanceWrapper()
#setup paths and file names to process
fs = Path(getnetworkdataroot())
pylabs_atlasdir = Path(*Path(inspect.getabsfile(pylabs)).parts[:-2]) / 'data' / 'atlases'
slicer_path = Path(*Path(inspect.getabsfile(pylabs)).parts[:-3]) / 'Slicer-4.5.0-2016-05-02-linux-amd64' / 'Slicer --launch '
#setup masks and templates:
anat_atlas = pylabs_atlasdir / 'JHU_MNI_SS_WMPM_Type_I_matched.nii.gz'
tract_atlas = pylabs_atlasdir / 'JHU-ICBM-tracts-prob-1mm.nii.gz'
thr = {'thr': 10}    #global threshold for tract atlas to narrow fiber bundle channel

MNI_atlases = {'mori': {'atlas_fname': pylabs_atlasdir / 'JHU_MNI_SS_WMPM_Type_I_matched.nii.gz', 'roi_list': None, 'Sl_cmd': None},
                'aal_motor': {'atlas_fname': pylabs_atlasdir / 'aal_1mm_motorcortex.nii', 'roi_list': [1, 2, 3, 4, 7, 8, 19, 20, 23, 24, 57, 58, 59, 60, 61, 62, 63, 64, 69, 70], 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'mori_LeftPostIntCap-35': {'atlas_fname': pylabs_atlasdir / 'mori_LeftPostIntCap-35.nii', 'roi_list': [35], 'Sl_cmd': 'TractographyLabelMapSeeding -m 2000 -l 2 -x -v 0.1 -a '},
                'mori_RightPostIntCap-123': {'atlas_fname': pylabs_atlasdir / 'mori_RightPostIntCap-123.nii', 'roi_list': [123], 'Sl_cmd': 'TractographyLabelMapSeeding -m 2000 -l 2 -x -v 0.1 -a '},
                'mori_base_mask52only': {'atlas_fname': pylabs_atlasdir / 'mori_base_mask52only.nii', 'roi_list': None, 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'mori_CC': {'atlas_fname': pylabs_atlasdir / 'mori_bilatCC-52to54-140to142.nii', 'roi_list': [52, 53, 54, 140, 141, 142], 'Sl_cmd': 'TractographyLabelMapSeeding -m 2000 -l 2 -x -v 0.1 -a '},
                'mori_Left_IFOF-45-47': {'atlas_fname': pylabs_atlasdir / 'mori_Left_IFOF-45-47.nii', 'roi_list': [45,47], 'Sl_cmd': 'TractographyLabelMapSeeding -m 2000 -l 2 -x -v 0.1 -a '},
                'mori_Right_IFOF-133-135': {'atlas_fname': pylabs_atlasdir / 'mori_Right_IFOF-133-135.nii', 'roi_list': [133, 135],  'Sl_cmd': 'TractographyLabelMapSeeding -m 2000 -l 2 -x -v 0.1 -a '},
                'mori_Left_frontal-3-5': {'atlas_fname': pylabs_atlasdir / 'mori_Left_frontal-3-5.nii', 'roi_list': [3,4,5], 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'mori_Left_occip-10-16-20': {'atlas_fname': pylabs_atlasdir / 'mori_Left_occip-10-16-20.nii', 'roi_list': [10,16,20], 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'mori_Right_frontal-91-93': {'atlas_fname': pylabs_atlasdir / 'mori_Right_frontal-91-93.nii', 'roi_list': [91,92,93], 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'mori_Right_occip-98-99-102-104': {'atlas_fname': pylabs_atlasdir / 'mori_Right_occip-98-99-102-104.nii', 'roi_list': [104,99,98,102], 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'mori_Left_SLF-43':  {'atlas_fname': pylabs_atlasdir / 'mori_Left_SLF-43.nii', 'roi_list': [43], 'Sl_cmd': 'TractographyLabelMapSeeding -m 2000 -l 2 -x -v 0.1 -a '},
                'mori_Right_SLF-131': {'atlas_fname': pylabs_atlasdir / 'mori_Right_SLF-131.nii', 'roi_list': [131], 'Sl_cmd': 'TractographyLabelMapSeeding -m 2000 -l 2 -x -v 0.1 -a '},
                'mori_Left_pre-postCentGyr-6-7': {'atlas_fname': pylabs_atlasdir / 'mori_Left_pre-postCentGyr-6-7.nii', 'roi_list': [6, 7], 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'mori_Right_pre-postCentGyr-94-95': {'atlas_fname': pylabs_atlasdir / 'mori_Right_pre-postCentGyr-94-95.nii', 'roi_list': [94,95], 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'mori_Left_STG-MTG-18-20':  {'atlas_fname': pylabs_atlasdir / 'mori_Left_STG-MTG-18-20.nii', 'roi_list': [20,18], 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'mori_Right_STG-MTG-106-108': {'atlas_fname': pylabs_atlasdir / 'mori_Right_STG-MTG-106-108.nii', 'roi_list': [106,108], 'Sl_cmd': 'ModelMaker -l 1 -n '},

                'JHU_tracts_Left_ATR-1': {'atlas_fname': pylabs_atlasdir / 'JHU_tracts_thr%(thr)s_Left_ATR-1.nii', 'roi_list': 1, 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'JHU_tracts_Right_ATR-2': {'atlas_fname': pylabs_atlasdir / 'JHU_tracts_thr%(thr)s_Right_ATR-2.nii', 'roi_list': 2, 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'JHU_tracts_Left_CSP-3': {'atlas_fname': pylabs_atlasdir / 'JHU_tracts_thr%(thr)s_Left_CSP-3.nii', 'roi_list': 3, 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'JHU_tracts_Right_CSP-4': {'atlas_fname': pylabs_atlasdir / 'JHU_tracts_thr%(thr)s_Right_CSP-4.nii', 'roi_list': 4, 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'JHU_tracts_Left_Cing-5': {'atlas_fname': pylabs_atlasdir / 'JHU_tracts_thr%(thr)s_Left_Cing-5.nii', 'roi_list': 5, 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'JHU_tracts_Right_Cing-6': {'atlas_fname': pylabs_atlasdir / 'JHU_tracts_thr%(thr)s_Right_Cing-6.nii', 'roi_list': 6, 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'JHU_tracts_Forceps_Major-9': {'atlas_fname': pylabs_atlasdir / 'JHU_tracts_thr%(thr)s_Forceps_Major-9.nii', 'roi_list': 9, 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'JHU_tracts_Forceps_Minor-10': {'atlas_fname': pylabs_atlasdir / 'JHU_tracts_thr%(thr)s_Forceps_Minor-10.nii', 'roi_list': 10, 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'JHU_tracts_Left_IFOF-11': {'atlas_fname': pylabs_atlasdir / 'JHU_tracts_thr%(thr)s_Left_IFOF-11.nii', 'roi_list': 11, 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'JHU_tracts_Right_IFOF-12':  {'atlas_fname': pylabs_atlasdir / 'JHU_tracts_thr%(thr)s_Right_IFOF-12.nii', 'roi_list': 12, 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'JHU_tracts_Left_ILF-13': {'atlas_fname': pylabs_atlasdir / 'JHU_tracts_thr%(thr)s_Left_ILF-13.nii', 'roi_list': 13, 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'JHU_tracts_Right_ILF-14': {'atlas_fname': pylabs_atlasdir / 'JHU_tracts_thr%(thr)s_Right_ILF-14.nii', 'roi_list': 14, 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'JHU_tracts_Left_SLF-15': {'atlas_fname': pylabs_atlasdir / 'JHU_tracts_thr%(thr)s_Left_SLF-15.nii', 'roi_list': 15, 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'JHU_tracts_Right_SLF-16': {'atlas_fname': pylabs_atlasdir / 'JHU_tracts_thr%(thr)s_Right_SLF-16.nii', 'roi_list': 16, 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'JHU_tracts_Left_Unc-17': {'atlas_fname': pylabs_atlasdir / 'JHU_tracts_thr%(thr)s_Left_Unc-17.nii', 'roi_list': 17, 'Sl_cmd': 'ModelMaker -l 1 -n '},
                'JHU_tracts_Right_Unc-18': {'atlas_fname': pylabs_atlasdir / 'JHU_tracts_thr%(thr)s_Right_Unc-18.nii', 'roi_list': 18, 'Sl_cmd': 'ModelMaker -l 1 -n '},
                }

tensors = {'RESTORE':['_eddy_corrected_repol_std2_restore_cam_tensor_medfilt.nhdr', '_eddy_corrected_repol_std2_restore_cam_tensor.nhdr', '_eddy_corrected_repol_std2_restore_dipy_tensor.nhdr', '_eddy_corrected_repol_std2_restore_dipy_tensor_medfilt.nhdr'],
            'OLS': ['_eddy_corrected_repol_std2_ols_fsl_tensor_medfilt.nhdr', '_eddy_corrected_repol_std2_ols_fsl_tensor.nhdr', '_eddy_corrected_repol_std2_ols_dipy_tensor.nhdr', '_eddy_corrected_repol_std2_ols_dipy_tensor_medfilt.nhdr', '_eddy_corrected_repol_std2_ols_cam_tensor.nhdr', '_eddy_corrected_repol_std2_ols_cam_tensor_medfilt.nhdr'],
            'WLS': ['_eddy_corrected_repol_std2_wls_fsl_tensor_medfilt.nhdr', '_eddy_corrected_repol_std2_wls_fsl_tensor.nhdr', '_eddy_corrected_repol_std2_wls_dipy_tensor.nhdr', '_eddy_corrected_repol_std2_wls_dipy_tensor_medfilt.nhdr', '_eddy_corrected_repol_std2_wls_cam_tensor.nhdr', '_eddy_corrected_repol_std2_wls_cam_tensor_medfilt.nhdr']
            }
#set project specific files
project = 'bbc'
fa2t1_outdir = 'reg_subFA2suborigvbmpaired_run2'
fadir = 'FA_fsl_wls_tensor_mf_ero_paired'
dwi_templ = 'sub-bbc{sid}_ses-{snum}_{meth}_{runnum}'
dwi_fnames = [dwi_templ.format(sid=str(s), snum=str(ses), meth=m, runnum=str(r)) for s, ses, m, r in dwipairing]
vbm_templ = 'bbc_pairedLH_sub-bbc{sid}_ses-{snum}_{meth}_{runnum}_brain_susan_nl_comroll'
vbm_fnames = [vbm_templ.format(sid=str(s), snum=str(ses), meth=m, runnum=str(r)) for s, ses, m, r in vbmpairing]
templdir = fs / project / 'reg' / 'ants_vbm_pairedLH_in_template_space'
MNI2templ_invwarp = templdir / 'bbc_pairedLH_template_reg2MNI_1InverseWarp.nii.gz'
MNI2templ_aff = templdir / 'bbc_pairedLH_template_reg2MNI_0GenericAffine.mat'
dwi2vbmsubjdir = fs / project / 'reg' / 'reg_subFA2suborigvbmpaired_run2'
dwi_reg_append = '_eddy_corrected_repol_std2_wls_fsl_tensor_mf_FA_ero_reg2sorigvbm_'

#apply the warps
for dwif, vbmf in zip(dwi_fnames, vbm_fnames):
    for k, a in MNI_atlases.iteritems():
        # extract rois from atlases and make masks
        if 'mori' in k and not a['roi_list'] == None:
            make_mask_fm_atlas_parts(atlas=str(anat_atlas), roi_list=a['roi_list'], mask_fname=str(a['atlas_fname']))
        elif 'JHU_' in k:
            make_mask_fm_tracts(atlas=str(tract_atlas), volidx=a['roi_list'], thresh=thr, mask_fname=(str(a['atlas_fname']) % thr))
        elif 'aal_motor' in k:
            make_mask_fm_atlas_parts(atlas=str(pylabs_atlasdir / 'aal_1mm_reg2MNI_masked.nii.gz'), roi_list=a['roi_list'], mask_fname=str(a['atlas_fname']))
        execwdir = fs / project / dwif.split('_')[0] / dwif.split('_')[1] / 'dwi'
        ref = execwdir / str(dwif+'_S0_brain.nii')
        if 'mori' in k or 'aal_motor' in k:
            mov = a['atlas_fname']
            outf = execwdir / str(dwif+'_'+k+'.nii')
        if 'JHU_' in k:
            mov = (str(a['atlas_fname']) % thr)
            outf = execwdir / str(dwif+'_'+(a['atlas_fname'].name % thr))
        iwarp_templ2vbmsubj = templdir / str(vbmf+'InverseWarp.nii.gz')
        iwarp_vbmsub2dwi = dwi2vbmsubjdir / str(dwif+ dwi_reg_append +'1InverseWarp.nii.gz')
        aff_templ2vbmsubj = templdir / str(vbmf+'Affine.txt')
        aff_vbmsub2dwi = dwi2vbmsubjdir / str(dwif + dwi_reg_append + '0GenericAffine.mat')
        warpfiles = [str(MNI2templ_invwarp), str(iwarp_templ2vbmsubj), str(iwarp_vbmsub2dwi)]
        affine_xform = [str(MNI2templ_aff), str(aff_templ2vbmsubj), str(aff_vbmsub2dwi)]
        subj2templ_applywarp(str(mov), str(ref), str(outf), warpfiles, str(execwdir), affine_xform=affine_xform, inv=True)
        vtkdir = execwdir / 'vtk_tensor_comp_run5'
        if not vtkdir.is_dir():
            vtkdir.mkdir()
        #recoded till here
        try:
            if not a['Sl_cmd'] == None:
                if a['Sl_cmd'] == 'ModelMaker -l 1 -n ':
                    cmd = ''
                    cmd += str(slicer_path) + a['Sl_cmd']
                    if 'mori' in k or 'aal_motor' in k:
                        cmd += str(vtkdir / str(dwif + '_' + k))
                    if 'JHU_' in k:
                        cmd += str(vtkdir / str(dwif + '_' + (str(a['atlas_fname'].name) % thr).split('.')[0]))
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
                        provenance.log(str(vtkdir / str(dwif + '_' + str(str(a['atlas_fname'].name) % thr).split('.')[0]) + '.vtk'), 'generate model vtk', str(outf), script=__file__, provenance=params)
                else:
                    for m, ts in tensors.iteritems():
                        tenpath = execwdir / 'cuda_repol_std2_v2' / m
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
        except:
            print "exception caught for "+dwif+". Missing "+k+" for "+' '.join(list(a))+" or "+m