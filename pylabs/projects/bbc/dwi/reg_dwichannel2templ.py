from pathlib import *
from pylabs.alignment.ants_reg import subj2templ_applywarp
from pylabs.projects.bbc.pairing import vbmpairing, dwipairing
from pylabs.utils import run_subprocess, WorkingContext
from pylabs.utils.paths import getnetworkdataroot
#set up provenance
from pylabs.utils.provenance import ProvenanceWrapper
provenance = ProvenanceWrapper()
#setup paths and file names to process
fs = Path(getnetworkdataroot())

# winners of fit death match
fitmethsd = {'OLS': ['ols_dipy_tensor_medfilt', 'ols_fsl_tensor_medfilt'],
            'WLS': ['wls_dipy_tensor_medfilt', 'wls_fsl_tensor_medfilt']}
#fitmethsd = {'WLS': ['wls_fsl_tensor_medfilt']}

channel_atlases = {'mori_LeftPostIntCap-35': {'atlas_fname': 'mori_LeftPostIntCap-35_channel.nii.gz', 'roi_list': [35]},
                'mori_RightPostIntCap-123': {'atlas_fname': 'mori_RightPostIntCap-123_channel.nii.gz', 'roi_list': [123]},
                'mori_CC': {'atlas_fname': 'mori_CC_channel.nii.gz', 'roi_list': [52, 53, 54, 140, 141, 142]},
                'mori_Left_IFOF-45-47': {'atlas_fname': 'mori_Left_IFOF-45-47_channel.nii.gz', 'roi_list': [45,47,36]},
                'mori_Right_IFOF-133-135': {'atlas_fname': 'mori_Right_IFOF-133-135_channel.nii.gz', 'roi_list': [133, 135, 124]},
                'mori_Left_SLF-43':  {'atlas_fname': 'mori_Left_SLF-43_channel.nii.gz', 'roi_list': [43]},
                'mori_Right_SLF-131': {'atlas_fname': 'mori_Right_SLF-131_channel.nii.gz', 'roi_list': [131]},
                   }


fext = {'ols_dipy_mf': '.nii', 'ols_fsl_tensor_mf': '.nii.gz','wls_dipy_mf': '.nii', 'wls_fsl_tensor_mf': '.nii.gz'}

project = 'bbc'
ref = fs / project / 'reg' / 'ants_vbm_pairedLH_in_template_space' / 'bbc_pairedLH_template_resampled2dwi.nii'
dwi_templ = 'sub-bbc{sid}_ses-{snum}_{meth}_{runnum}'
dwi_fnames = [dwi_templ.format(sid=str(s), snum=str(ses), meth=m, runnum=str(r)) for s, ses, m, r in dwipairing]
vbm_templ = 'bbc_pairedLH_sub-bbc{sid}_ses-{snum}_{meth}_{runnum}_brain_susan_nl_comroll'
vbm_fnames = [vbm_templ.format(sid=str(s), snum=str(ses), meth=m, runnum=str(r)) for s, ses, m, r in vbmpairing]
outf_fmat = '{dwif}_eddy_corrected_repol_std2_{f}_{a}_channel_reg2vbmtempl_FA_AD_RD_MD.nii'

for dwif, vbmf in zip(dwi_fnames, vbm_fnames):
    for k, fm in fitmethsd.iteritems():
        for f in fm:
            for a, c in channel_atlases.iteritems():
                mov = (fs / project / dwif.split('_')[0] / dwif.split('_')[1] / 'dwi' / 'vtk_tensor_comp_run7' / '_'.join([dwif, 'eddy_corrected_repol_std2', f, c['atlas_fname']]))
                outf = (fs / project / 'reg' / 'dwi_warps_in_template_space' / str(f+'_comb_FA_AD_RD_MD_4vol') / outf_fmat.format(dwif=dwif, f=f, a=a))
                warp1 = (fs / project / 'reg' / 'ants_vbm_pairedLH_in_template_space' / str(vbmf+'Warp.nii.gz'))
                aff1 = (fs / project / 'reg' / 'ants_vbm_pairedLH_in_template_space' / str(vbmf+'Affine.txt'))
                warp2 = (fs / project / 'reg' / 'reg_subFA2suborigvbmpaired_run2' / str(dwif+'_eddy_corrected_repol_std2_wls_fsl_tensor_mf_FA_ero_reg2sorigvbm_1Warp.nii.gz'))
                aff2 = (fs / project / 'reg' / 'reg_subFA2suborigvbmpaired_run2' / str(dwif+'_eddy_corrected_repol_std2_wls_fsl_tensor_mf_FA_ero_reg2sorigvbm_0GenericAffine.mat'))
                warpfiles = [str(warp1), str(warp2)]
                affine_xform = [str(aff1), str(aff2)]
                execwdir = fs / project / 'reg' / 'dwi_warps_in_template_space' / str(f+'_comb_FA_AD_RD_MD_4vol')
                if not execwdir.is_dir():
                    execwdir.mkdir(parents=True)
                try:
                    subj2templ_applywarp(str(mov), str(ref), str(outf), warpfiles, str(execwdir), affine_xform=affine_xform, dims=4, args=['--use-BSpline'])
                except:
                    print "exception caught for " + dwif + ". Missing " + k + " for " + f
