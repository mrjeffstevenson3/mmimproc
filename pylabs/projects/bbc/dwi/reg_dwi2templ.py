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

mods = ['FA', 'MD', 'AD', 'RD']
# winners of fit death match
fitmethsd = {'OLS': ['ols_dipy_mf', 'ols_fsl_tensor_mf'],
            'WLS': ['wls_dipy_mf', 'wls_fsl_tensor_mf']}

fext = {'ols_dipy_mf': '.nii', 'ols_fsl_tensor_mf': '.nii.gz','wls_dipy_mf': '.nii', 'wls_fsl_tensor_mf': '.nii.gz'}

project = 'bbc'
ecdir = 'cuda_repol_std2_S0mf3_v5'
filterS0_string = ''
filterS0 = True
if filterS0:
    filterS0_string = '_withmf3S0'
ref = fs / project / 'reg' / 'ants_vbm_pairedLH_in_template_space' / 'bbc_pairedLH_template_resampled2dwi.nii'
#dwi_templ = 'sub-bbc{sid}_ses-{snum}_{meth}_{runnum}'
dwi_templ = 'sub-bbc{sid}_ses-{snum}_{meth}_{runnum}'+filterS0_string+'_ec_thr1'
dwi_fnames = [dwi_templ.format(sid=str(s), snum=str(ses), meth=m, runnum=str(r)) for s, ses, m, r in dwipairing]
vbm_templ = 'bbc_pairedLH_sub-bbc{sid}_ses-{snum}_{meth}_{runnum}_brain_susan_nl_comroll'
vbm_fnames = [vbm_templ.format(sid=str(s), snum=str(ses), meth=m, runnum=str(r)) for s, ses, m, r in vbmpairing]
outf_fmat = '{dwif}_{f}_{m}_reg2vbmtempl.nii'

for dwif, vbmf in zip(dwi_fnames, vbm_fnames):
    for k, fm in fitmethsd.iteritems():
        for f in fm:
            for m in mods:
                mov = (fs / project / dwif.split('_')[0] / dwif.split('_')[1] / 'dwi' / ecdir / k / '_'.join([dwif, f, m+fext[f]]))
                outf = (fs / project / 'reg' / 'dwi_warps_in_template_space' / m / f / outf_fmat.format(dwif=dwif, f=f, m=m))
                warp1 = (fs / project / 'reg' / 'ants_vbm_pairedLH_in_template_space' / str(vbmf+'Warp.nii.gz'))
                aff1 = (fs / project / 'reg' / 'ants_vbm_pairedLH_in_template_space' / str(vbmf+'Affine.txt'))
                warp2 = (fs / project / 'reg' / 'reg_subFA2suborigvbmpaired_run2' / str(dwif.replace(filterS0_string+'_ec_thr1', '')+'_eddy_corrected_repol_std2_wls_fsl_tensor_mf_FA_ero_reg2sorigvbm_1Warp.nii.gz'))
                aff2 = (fs / project / 'reg' / 'reg_subFA2suborigvbmpaired_run2' / str(dwif.replace(filterS0_string+'_ec_thr1', '')+'_eddy_corrected_repol_std2_wls_fsl_tensor_mf_FA_ero_reg2sorigvbm_0GenericAffine.mat'))
                warpfiles = [str(warp1), str(warp2)]
                affine_xform = [str(aff1), str(aff2)]
                execwdir = fs / project / 'reg' / 'dwi_warps_in_template_space' / m / f
                if not execwdir.is_dir():
                    execwdir.mkdir(parents=True)
                if all([mov.is_file(), warp1.is_file(), aff1.is_file(), warp2.is_file(), aff2.is_file()]):
                    try:
                        subj2templ_applywarp(str(mov), str(ref), str(outf), warpfiles, str(execwdir), affine_xform=affine_xform, args=['--use-NN'])
                    except ValueError:
                        print "Caught ApplyWarp error for subj " + dwif + " fit method "+f+ " and "+ m
                        print "skipping to next method or subject"
                        pass
                else:
                    print 'missing one or more input files for {dwif} with {m} for {f}.'.format(dwif=dwif, m=m, f=f)
for m in mods:
    for k, fm in fitmethsd.iteritems():
        for f in fm:
            regdir = fs / project / 'reg' / 'dwi_warps_in_template_space' / m / f
            print str(regdir)
            results = ()
            with WorkingContext(str(regdir)):
                cmd = ''
                cmd += 'fslmerge -t ' + '_'.join(['all', m, f+'.nii.gz']) + ' '
                mergelist = ' '.join([a + b for a, b in zip(dwi_fnames, [f+'_'+m+'_reg2vbmtempl.nii'] * len(dwi_fnames))])
                cmd += mergelist
                results += run_subprocess(cmd)
                #provenance.log(str(regdir / '_'.join(['all', m, f+'.nii.gz'])), 'generate merged all file from '+m+' '+f, mergelist)
                print cmd





