# this script moves bbc dwi data from subject space directly to template space after executing this bash cmd is bbc/reg/ants_dwiS0_in_template_space:
## for f in `ls orig_S0_in_subject_space/*.nii`; do antsRegistrationSyN.sh -d 3 -m $f -f bbc_pairedLH_template_invT2c_resampled2dwi.nii.gz -o `basename ${f/.nii/}`_reg2dwiT2template_ -n 30 -t s -p f -j 1 -s 10 -r 1; done

from pathlib import *
from mmimproc.alignment.ants_reg import subj2templ_applywarp
from mmimproc.projects.bbc.pairing import vbmpairing, dwipairing, dwituppairing
from mmimproc.utils import run_subprocess, WorkingContext
from mmimproc.utils.paths import getnetworkdataroot
#set up provenance
from mmimproc.utils.provenance import ProvenanceWrapper
provenance = ProvenanceWrapper()
#setup paths and file names to process
fs = Path(getnetworkdataroot())

mods = ['FA', 'MD', 'AD', 'RD']
# winners of fit death match
# fitmethsd = {'OLS': ['ols_dipy_mf', 'ols_fsl_tensor_mf'], 'WLS': ['wls_dipy_mf', 'wls_fsl_tensor_mf']}
# only fsl has all 18 subjs for ols and wls. using only median filtered tensors.
fitmethsd = {'OLS': ['ols_fsl_tensor_mf'], 'WLS': ['wls_fsl_tensor_mf']}

fext = {'ols_dipy_mf': '.nii', 'ols_fsl_tensor_mf': '.nii.gz','wls_dipy_mf': '.nii', 'wls_fsl_tensor_mf': '.nii.gz'}

project = 'bbc'
ecdir = 'cuda_repol_std2_S0mf3_v5'
filterS0_string = '_withmf3S0'
regdir = fs / project / 'reg' / 'ants_dwiS0_in_template_space'
ref = regdir / 'bbc_pairedLH_template_invT2c_resampled2dwi.nii.gz'
# dwi_templ = 'sub-bbc{sid}_ses-{snum}_{meth}_{runnum}'
dwi_bn_templ = 'sub-bbc{sid}_ses-{snum}_{meth}_{runnum}'
dwif_templ = '{dwif}'+filterS0_string+'_ec_thr1_{fm}_{m}'
dwi_fnames = [dwi_bn_templ.format(sid=str(s), snum=str(ses), meth=m, runnum=str(r)) for s, ses, m, r in dwipairing]
warp1_templ = '{dwif}'+filterS0_string+'_S0_brain_j1_s10_r1_reg2dwiT2template_1Warp.nii.gz'
aff1_templ = '{dwif}'+filterS0_string+'_S0_brain_j1_s10_r1_reg2dwiT2template_0GenericAffine.mat'
outf_fmat = '{dwif}_{f}_{m}_reg2vbmtempl.nii'

for dwif in dwi_fnames:
    for k, fm in fitmethsd.iteritems():
        for f in fm:
            for m in mods:
                mov = fs / project / dwif.split('_')[0] / dwif.split('_')[1] / 'dwi' / ecdir / k / dwif_templ.format(dwif=dwif, fm=f, m=m+fext[f])
                outf = regdir / m / f / outf_fmat.format(dwif=dwif, f=f, m=m)
                warp1 = regdir / warp1_templ.format(dwif=dwif)
                aff1 = regdir / aff1_templ.format(dwif=dwif)
                warpfiles = [str(warp1)]
                affine_xform = [str(aff1)]
                execwdir = regdir / m / f
                if not execwdir.is_dir():
                    execwdir.mkdir(parents=True)
                if all([mov.is_file(), warp1.is_file(), aff1.is_file()]):
                    try:
                        subj2templ_applywarp(str(mov), str(ref), str(outf), warpfiles, str(execwdir), affine_xform=affine_xform, args=['--use-NN'])
                    except ValueError:
                        print("Caught ApplyWarp error for subj " + dwif + " fit method "+f+ " and "+ m)
                        print("skipping to next method or subject")
                        pass
                else:
                    print('missing one or more input files for {dwif} with {m} for {f}.'.format(dwif=dwif, m=m, f=f))
# merge all modalities and fit methods - no subtraction yet.
results = ()
for m in mods:
    for k, fm in fitmethsd.iteritems():
        for f in fm:
            wrkdir = regdir / m / f
            with WorkingContext(str(wrkdir)):
                cmd = ''
                cmd += 'fslmerge -t ' + '_'.join(['all_pairedLH', f, m+'.nii.gz']) + ' '
                mergelist = ' '.join([str(regdir / m / f / outf_fmat.format(dwif=d, f=f, m=m)) for d, f, m in zip(dwi_fnames, [f]*len(dwi_fnames), [m]*len(dwi_fnames))])
                cmd += mergelist
                try:
                    results += run_subprocess(cmd)
                except ValueError:
                    print("Caught fslmerge error for  fit method " + f + " and " + m)
                    print("skipping to next method")
                    pass
                #provenance.log(str(regdir / '_'.join(['all', m, f+'.nii.gz'])), 'generate merged all file from '+m+' '+f, mergelist)

dwifslsubcmdtempl = ('fslmaths sub-bbc{csid}_ses-{csnum}_{cmeth}_{crunnum}_{f}_{m}_reg2vbmtempl.nii -sub '
    'sub-bbc{fsid}_ses-{fsnum}_{fmeth}_{frunnum}_{f}_{m}_reg2vbmtempl.nii '
    'bbc_{dwifs}_subtraction_{f}_{m}_reg2vbmtempl.nii')
# make paired subtractions
sublist = []
for dwituppair in dwituppairing:
    fost, cont, subtxt = dwituppair
    sublist.append(subtxt)
    for m in mods:
        for k, fm in fitmethsd.iteritems():
            for f in fm:
                wrkdir = regdir / m / f
                kwargs = {'fsid':fost[0], 'fsnum':fost[1], 'fmeth':fost[2], 'frunnum':fost[3],
                          'csid': cont[0], 'csnum': cont[1], 'cmeth': cont[2], 'crunnum': cont[3],
                          'dwifs': subtxt, 'f': f, 'm': m, 'filterS0_string': filterS0_string}
            with WorkingContext(str(wrkdir)):
                try:
                    results += run_subprocess(dwifslsubcmdtempl.format(**kwargs))
                except ValueError:
                    print("Caught subtraction error for "+subtxt+" fit method " + f + " and " + m)
                    print("skipping to next pair")
                    pass
# merge subtractions into 1 all subs file
for m in mods:
    for k, fm in fitmethsd.iteritems():
        for f in fm:
            wrkdir = regdir / m / f
            with WorkingContext(str(wrkdir)):
                cmd = ''
                cmd += 'fslmerge -t ' + '_'.join(['all_subtracted_pairsLH', f, m+'.nii.gz']) + ' '
                mergelist = ' '.join(['bbc_{dwifs}_subtraction_{f}_{m}_reg2vbmtempl.nii.gz'.format(dwifs=d, f=f, m=m) for d, f, m in zip(sublist, [f]*len(sublist), [m]*len(sublist))])
                cmd += mergelist
                try:
                    results += run_subprocess(cmd)
                except ValueError:
                    print("Caught merge error for fit method " + f + " and " + m)
                    print("skipping to next pair")
                    pass
                #provenance.log(str(regdir / '_'.join(['all_subtracted_pairsLH', f, m+'.nii.gz'])), 'generate merged subtraction all file from '+m+' '+f, str(regdir / mergelist))
