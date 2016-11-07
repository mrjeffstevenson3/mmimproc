import os, inspect
from pathlib import *
import datetime
from os.path import split
import numpy as np
import nibabel as nib
import niprov, pylabs
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
MNI_atlases = {'mori': pylabs_atlasdir / 'JHU_MNI_SS_WMPM_Type_I_matched.nii.gz',
                'aal_motor': pylabs_atlasdir / 'aal_1mm_motorcortex.nii',
                'mori_LeftPostIntCap-35': pylabs_atlasdir / 'mori_LeftPostIntCap-35.nii',
                'mori_RightPostIntCap-123': pylabs_atlasdir / 'mori_RightPostIntCap-123.nii',
                'mori_base_mask52only': pylabs_atlasdir / 'mori_base_mask52only.nii'
                }
Slicer_cmd = { 'mori': None,
        'aal_motor': 'ModelMaker -l 1 -n ',
        'mori_LeftPostIntCap-35': 'TractographyLabelMapSeeding -m 2000 -l 2 -x -v 0.1 -a ',
        'mori_RightPostIntCap-123': 'TractographyLabelMapSeeding -m 2000 -l 2 -x -v 0.1 -a ',
        'mori_base_mask52only': 'ModelMaker -l 1 -n '
        }
tensors = {'RESTORE':['_eddy_corrected_repol_std2_restore_cam2fsl_tensor_medfilt.nhdr', '_eddy_corrected_repol_std2_restore_cam2fsl_tensor.nhdr'],
            'OLS': ['_eddy_corrected_repol_std2_ols_fsl_tensor_medfilt.nhdr', '_eddy_corrected_repol_std2_ols_fsl_tensor.nhdr'],
            'WLS': ['_eddy_corrected_repol_std2_wls_fsl_tensor_medfilt.nhdr', '_eddy_corrected_repol_std2_wls_fsl_tensor.nhdr']
            }
project = 'bbc'
fa2t1_outdir = 'reg_subFA2suborigvbmpaired'
fadir = 'FA_fsl_wls_tensor_mf_ero_paired'
dwi_templ = 'sub-bbc{sid}_ses-{snum}_{meth}_{runnum}'
dwi_fnames = [dwi_templ.format(sid=str(s), snum=str(ses), meth=m, runnum=str(r)) for s, ses, m, r in dwipairing]
vbm_templ = 'bbc_pairedLH_sub-bbc{sid}_ses-{snum}_{meth}_{runnum}_brain_susan_nl_comroll'
vbm_fnames = [vbm_templ.format(sid=str(s), snum=str(ses), meth=m, runnum=str(r)) for s, ses, m, r in vbmpairing]
templdir = fs / project / 'reg' / 'ants_vbm_pairedLH_in_template_space'
MNI2templ_invwarp = templdir / 'bbc_pairedLH_template_reg2MNI_1InverseWarp.nii.gz'
MNI2templ_aff = templdir / 'bbc_pairedLH_template_reg2MNI_0GenericAffine.mat'
dwi2vbmsubjdir = fs / project / 'reg' / 'reg_subFA2suborigvbmpaired'
dwi_reg_append = '_eddy_corrected_repol_std2_wls_fsl_tensor_mf_FA_ero_reg2sorigvbm_'

# dwif = dwi_fnames[1]
# vbmf = vbm_fnames[1]
for dwif, vbmf in zip(dwi_fnames[1:], vbm_fnames[1:]):
    for k, a in MNI_atlases.iteritems():
        execwdir = fs / project /  dwif.split('_')[0] / dwif.split('_')[1] / 'dwi'
        mov = a
        ref = execwdir / str(dwif+'_S0_brain.nii')
        outf = execwdir / str(dwif+'_'+k)
        iwarp_templ2vbmsubj = templdir / str(vbmf+'InverseWarp.nii.gz')
        iwarp_vbmsub2dwi = fs / project / 'reg' / 'reg_subFA2suborigvbmpaired' / str(dwif+ dwi_reg_append +'1InverseWarp.nii.gz')
        aff_templ2vbmsubj = templdir / str(vbmf+'Affine.txt')
        aff_vbmsub2dwi = fs / project / 'reg' / 'reg_subFA2suborigvbmpaired' / str(dwif + dwi_reg_append + '0GenericAffine.mat')
        warpfiles = [str(MNI2templ_invwarp), str(iwarp_templ2vbmsubj), str(iwarp_vbmsub2dwi)]
        affine_xform = [str(MNI2templ_aff), str(aff_templ2vbmsubj), str(aff_vbmsub2dwi)]
        subj2templ_applywarp(str(mov), str(ref), str(outf)+'.nii', warpfiles, str(execwdir), affine_xform=affine_xform, inv=True)
        vtkdir = execwdir / 'vtk_tensor_comp'
        if not vtkdir.is_dir():
            vtkdir.mkdir()
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
                    tenpath = execwdir / 'cuda_repol_std2' / m
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
