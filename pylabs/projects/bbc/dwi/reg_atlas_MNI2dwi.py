import os, inspect
from pathlib import *
import datetime
import pylabs
from pylabs.correlation.atlas import make_mask_fm_atlas_parts
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
atlas = pylabs_atlasdir / 'JHU_MNI_SS_WMPM_Type_I_matched.nii.gz'
roi_lists = [[70], [158], [3,4,5], [91,92,93], [10,16,20], [104,99,98,102], [43], [131], [6,7], [94,95], [20,18], [106,108]]
mask_fnames = ['mori_Left_IFOF-70', 'mori_Right_IFOF-158', 'mori_Left_frontal-3-5', 'mori_Right_frontal-91-93',
               'mori_Left_occip-10-16-20', 'mori_Right_occip-98-99-102-104', 'mori_Left_SLF-43', 'mori_Right_SLF-131',
               'mori_Left_pre-postCentGyr-6-7', 'mori_Right_pre-postCentGyr-94-95', 'mori_Left_STG-MTG-18-20',
                'mori_Right_STG-MTG-106-108', ]
[make_mask_fm_atlas_parts(atlas=str(atlas), roi_list=r, mask_fname=str(pylabs_atlasdir / m) for r, m in zip(roi_lists, mask_fnames)]


MNI_atlases = {'mori': pylabs_atlasdir / 'JHU_MNI_SS_WMPM_Type_I_matched.nii.gz',
                'aal_motor': pylabs_atlasdir / 'aal_1mm_motorcortex.nii',
                'mori_LeftPostIntCap-35': pylabs_atlasdir / 'mori_LeftPostIntCap-35.nii',
                'mori_RightPostIntCap-123': pylabs_atlasdir / 'mori_RightPostIntCap-123.nii',
                'mori_base_mask52only': pylabs_atlasdir / 'mori_base_mask52only.nii',
                'mori_CC': pylabs_atlasdir / 'mori_bilatCC-52to54-140to142.nii',
                'mori_Left_IFOF-70': pylabs_atlasdir / 'mori_Left_IFOF-70.nii',
                'mori_Right_IFOF-158': pylabs_atlasdir / 'mori_Right_IFOF-158.nii',
                'mori_Left_frontal-3-5': pylabs_atlasdir / 'mori_Left_frontal-3-5.nii',
                'mori_Left_occip-10-16-20': pylabs_atlasdir / 'mori_Left_occip-10-16-20.nii',
                'mori_Right_frontal-91-93': pylabs_atlasdir / 'mori_Right_frontal-91-93.nii',
                'mori_Right_occip-98-99-102-104': pylabs_atlasdir / 'mori_Right_occip-98-99-102-104.nii',
                'mori_Left_SLF-43':  pylabs_atlasdir / 'mori_Left_SLF-43.nii',
                'mori_Right_SLF-131': pylabs_atlasdir / 'mori_Right_SLF-131.nii',
                'mori_Left_pre-postCentGyr-6-7': pylabs_atlasdir / 'mori_Left_pre-postCentGyr-6-7.nii',
                'mori_Right_pre-postCentGyr-94-95': pylabs_atlasdir / 'mori_Right_pre-postCentGyr-94-95.nii',
                'mori_Left_STG-MTG-18-20':  pylabs_atlasdir / 'mori_Left_STG-MTG-18-20.nii',
                'mori_Right_STG-MTG-106-108': pylabs_atlasdir / 'mori_Right_STG-MTG-106-108.nii',

                'JHU_tracts_thr10_Right_IFOF-12':  pylabs_atlasdir / 'JHU_tracts_thr10_Right_IFOF-12.nii',
                }
Slicer_cmd = { 'mori': None,
        'aal_motor': 'ModelMaker -l 1 -n ',
        'mori_LeftPostIntCap-35': 'TractographyLabelMapSeeding -m 2000 -l 2 -x -v 0.1 -a ',
        'mori_RightPostIntCap-123': 'TractographyLabelMapSeeding -m 2000 -l 2 -x -v 0.1 -a ',
        'mori_base_mask52only': 'ModelMaker -l 1 -n ',
        'mori_Left_frontal-3-5': 'ModelMaker -l 1 -n ',
        'mori_Left_occip-10-16-20': 'ModelMaker -l 1 -n ',
        'mori_Right_frontal-91-93': 'ModelMaker -l 1 -n ',
        'mori_Right_occip-98-99-102-104': 'ModelMaker -l 1 -n ',
        'mori_Left_pre-postCentGyr-6-7': 'ModelMaker -l 1 -n ',
        'mori_Right_pre-postCentGyr-94-95': 'ModelMaker -l 1 -n ',
        'mori_Left_STG-MTG-18-20': 'ModelMaker -l 1 -n ',
        'mori_Right_STG-MTG-106-108': 'ModelMaker -l 1 -n ',
        'mori_CC': 'TractographyLabelMapSeeding -m 2000 -l 2 -x -v 0.1 -a ',
        'mori_Left_IFOF-70': 'TractographyLabelMapSeeding -m 2000 -l 2 -x -v 0.1 -a ',
        'mori_Right_IFOF-158': 'TractographyLabelMapSeeding -m 2000 -l 2 -x -v 0.1 -a ',
        'mori_Left_SLF-43': 'TractographyLabelMapSeeding -m 2000 -l 2 -x -v 0.1 -a ',
        'mori_Right_SLF-131': 'TractographyLabelMapSeeding -m 2000 -l 2 -x -v 0.1 -a ',

        'JHU_tracts_thr10_Right_IFOF-12': 'ModelMaker -l 1 -n ',
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
        execwdir = fs / project /  dwif.split('_')[0] / dwif.split('_')[1] / 'dwi'
        mov = a
        ref = execwdir / str(dwif+'_S0_brain.nii')
        outf = execwdir / str(dwif+'_'+k)
        iwarp_templ2vbmsubj = templdir / str(vbmf+'InverseWarp.nii.gz')
        iwarp_vbmsub2dwi = dwi2vbmsubjdir / str(dwif+ dwi_reg_append +'1InverseWarp.nii.gz')
        aff_templ2vbmsubj = templdir / str(vbmf+'Affine.txt')
        aff_vbmsub2dwi = dwi2vbmsubjdir / str(dwif + dwi_reg_append + '0GenericAffine.mat')
        warpfiles = [str(MNI2templ_invwarp), str(iwarp_templ2vbmsubj), str(iwarp_vbmsub2dwi)]
        affine_xform = [str(MNI2templ_aff), str(aff_templ2vbmsubj), str(aff_vbmsub2dwi)]
        subj2templ_applywarp(str(mov), str(ref), str(outf)+'.nii', warpfiles, str(execwdir), affine_xform=affine_xform, inv=True)
        vtkdir = execwdir / 'vtk_tensor_comp_run3'
        if not vtkdir.is_dir():
            vtkdir.mkdir()
        try:
            if not Slicer_cmd[k] == None:
                if Slicer_cmd[k] == 'ModelMaker -l 1 -n ':
                    cmd = ''
                    cmd += str(slicer_path) + Slicer_cmd[k]
                    cmd += str(vtkdir / str(dwif + '_' + k)) + ' '+ str(outf)+'.nii'
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
                    provenance.log(str(vtkdir / str(dwif+'_'+k+'.vtk')), 'generate model vtk', str(outf)+'.nii', script=__file__, provenance=params)
                else:
                    for m, ts in tensors.iteritems():
                        if m in ['RESTORE', 'OLS', 'WLS']:
                            tenpath = execwdir / 'cuda_repol_std2_v2' / m
                            for t in ts:
                                cmd = ''
                                cmd += str(slicer_path) + Slicer_cmd[k]
                                cmd += str(outf)+'.nii '+str(tenpath / str(dwif+t))+' '+str(vtkdir / str(dwif+t.split('.')[0]+'_'+k))+'.vtk'
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
                                provenance.log(str(vtkdir / str(dwif+t.split('.')[0]+'_'+k))+'.vtk', 'generate fiberbundle vtk from tensors', [str(outf)+'.nii', str(tenpath / str(dwif+t))] , script=__file__, provenance=params)
        except:
            print "Missing "+Slicer_cmd[k]+"for"+m