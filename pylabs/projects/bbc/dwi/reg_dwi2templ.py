from pathlib import *
from pylabs.alignment.ants_reg import subj2templ_applywarp
from pylabs.projects.bbc.pairing import vbmpairing, dwipairing
from pylabs.utils.paths import getnetworkdataroot
#set up provenance
from pylabs.utils.provenance import ProvenanceWrapper
provenance = ProvenanceWrapper()
#setup paths and file names to process
fs = Path(getnetworkdataroot())

#loop over modality then fit method FA then dipy_wls

mods = ['FA', 'MD']

fitmethsd = {'OLS': ['ols_dipy_mf', 'ols_fsl_tensor_mf'],
            'WLS': ['wls_dipy_mf', 'wls_fsl_tensor_mf'],
            }
#             'RESTORE': ['%(m)s_dipy', '%(m)s_cam'],

allfitmeths = ['wls_dipy', 'wls_fsl', 'wls_cam', 'wls_dipy_mf', 'wls_fsl_mf', 'wls_cam_mf',
                'ols_dipy', 'ols_fsl', 'ols_cam', 'ols_dipy_mf', 'ols_fsl_mf', 'ols_cam_mf',
                'restore_cam', 'restore_dipy', 'restore_cam_mf', 'restore_dipy_mf']

fext = {'ols_dipy_mf': '.nii', 'ols_fsl_tensor_mf': '.nii.gz','wls_dipy_mf': '.nii', 'wls_fsl_tensor_mf': '.nii.gz'}


project = 'bbc'
ref = fs / project / 'reg' / 'ants_vbm_pairedLH_in_template_space' / 'bbc_pairedLH_template_resampled2dwi.nii'
dwi_templ = 'sub-bbc{sid}_ses-{snum}_{meth}_{runnum}'
dwi_fnames = [dwi_templ.format(sid=str(s), snum=str(ses), meth=m, runnum=str(r)) for s, ses, m, r in dwipairing]
vbm_templ = 'bbc_pairedLH_sub-bbc{sid}_ses-{snum}_{meth}_{runnum}_brain_susan_nl_comroll'
vbm_fnames = [vbm_templ.format(sid=str(s), snum=str(ses), meth=m, runnum=str(r)) for s, ses, m, r in vbmpairing]
outf_fmat = '{dwif}_eddy_corrected_repol_std2_{f}_reg2vbmtempl.nii'

for dwif, vbmf in zip(dwi_fnames, vbm_fnames):
    for k, fm in fitmethsd.iteritems():
        for f in fm:
            for m in mods:
                mov = (fs / project / dwif.split('_')[0] / dwif.split('_')[1] / 'dwi' / 'cuda_repol_std2_v2' / k / '_'.join([dwif, 'eddy_corrected_repol_std2', f, m+fext[f]]))
                outf = (fs / project / 'reg' / 'dwi_warps_in_template_space' / m / f / outf_fmat.format(dwif=dwif, f=f))
                warp1 = (fs / project / 'reg' / 'ants_vbm_pairedLH_in_template_space' / str(vbmf+'Warp.nii.gz'))
                aff1 = (fs / project / 'reg' / 'ants_vbm_pairedLH_in_template_space' / str(vbmf+'Affine.txt'))
                warp2 = (fs / project / 'reg' / 'reg_subFA2suborigvbmpaired_run2' / str(dwif+'_eddy_corrected_repol_std2_wls_fsl_tensor_mf_FA_ero_reg2sorigvbm_1Warp.nii.gz'))
                aff2 = (fs / project / 'reg' / 'reg_subFA2suborigvbmpaired_run2' / str(dwif+'_eddy_corrected_repol_std2_wls_fsl_tensor_mf_FA_ero_reg2sorigvbm_0GenericAffine.mat'))
                warpfiles = [str(warp1), str(warp2)]
                affine_xform = [str(aff1), str(aff2)]
                execwdir = fs / project / 'reg' / 'dwi_warps_in_template_space' / m / f
                if not execwdir.is_dir():
                    execwdir.mkdir(parents=True)
                subj2templ_applywarp(str(mov), str(ref), str(outf), warpfiles, str(execwdir), affine_xform=affine_xform)
                params = {}
                params['warpfiles'] = warpfiles
                params['affine_xform'] = affine_xform
                params['execwdir'] = execwdir
                params['ref'] = ref
                provenance.log(str(mov), 'apply ants T1 template warps and affines to bring FA into template space', str(outf),
                               script=__file__, provenance=params)