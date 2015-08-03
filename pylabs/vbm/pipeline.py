## Raw file conversion:  nibabel
## RMS / Concat: MRIConcat
## Skullstripping: fslvbm_2_proc_-n
## Segmentation
## Normalizing
## From here there is two paths; filter out covariate or include it in model.
import os, glob
from os.path import join as pathjoin
import niprov
from pylabs.correlation.behavior import csv2fslmat
from pylabs.correlation.regfilt import multiregfilt
from pylabs.correlation.randpar import multirandpar
from pylabs.utils.paths import getlocaldataroot
from niprov.options import NiprovOptions
opts = NiprovOptions()
opts.dryrun = False
opts.verbose = True

exptag='gender_and_vbm_delta_cov_4col_vbm'

subjects = [
317, 328, 332, 334, 335, 347, 353, 364, 371, 376, 379, 381, 384, 385, 396]

fs = getlocaldataroot()
vbmdir = fs+'js/self_control/hbm_group_data/vbm_15subj/workdir_v1/stats/'
matfiledir = pathjoin(vbmdir,'matfiles','matfiles_'+exptag)
resultdir = pathjoin(vbmdir,'randomise_runs','randpar_n500_'+exptag)
qsubdir = pathjoin(vbmdir,'qsubs_defunctcommands')
behavdir = fs+'js/self_control/behavioral_data/behav_from_andy_march27_2015/'
csvfile = behavdir+'EF_and_Brain_july08_2015_Meq0_delta.csv'
niprov.add(csvfile)
imgtemplate = '{0}_mod_merge_{1}.nii.gz'
images = glob.glob(vbmdir+'?M_mod_merg_s4.nii.gz')
[niprov.add(img) for img in images]

## Covariate Filtering
#
# matfiles = csv2fslmat(csvfile, cols=[2], covarcols=[43] selectSubjects=subjects,
#     groupcol=False, demean=False, outdir=matfiledir, opts=opts)
# images = multiregfilt(images, matfiles[0], opts=opts)

## Randomize n500 test run
designfile = vbmdir+'scs_design4col.con'
assert os.path.isfile(designfile)
subcols = range(5,8)+range(18,32)
# matfiles = csv2fslmat(csvfile, cols=subcols, covarcols=[2, 43], selectSubjects=subjects,
#     groupcol=True, outdir=matfiledir, opts=opts)
# multirandpar(images, matfiles, designfile, niterations=500, workdir=qsubdir,
#     outdir=resultdir, opts=opts)
#
# pthresh = 0.05
# corrpfiles = glob.glob(resultdir+'/*_corrp_tstat*.nii.gz')
# sig_results_fullpath = []
# with open(resultdir+'/sig_results_list_fullpath.txt', 'w') as outfile_fullpath:
#     for astat in corrpfiles:
#         statcmd = 'fslstats '+astat+' -R'
#         statout1 = subprocess.Popen(statcmd, shell=True, stdout=subprocess.PIPE)
#         statout2 = statout1.stdout.read()
#         statout3 = statout2.split()
#         pval = 1 - float(statout3[1])
#         if pval <= pthresh:
#             print('+++++ found p='+' '+str(pval)+' in file '+os.path.basename(astat).split('.')[0])
#             outfile_fullpath.write(astat+'\n')
#             sig_results_fullpath.append(astat)
#
# with open(resultdir+'/sig_results_list.txt', 'w') as sig_results:
#      for fp in sig_results_fullpath:
#          f = fp.split('/')[-1]
#          sig_results.write(f+'\n')
#
# with open(resultdir+'/sig_results_fslviewcmd.txt', 'w') as sig_results_fslviewcmd:
#      sig_results_fslviewcmd.write('fslview ')
#      for fp in sig_results_fullpath:
#          f = fp.split('/')[-1]
#          sig_results_fslviewcmd.write(f+' -b '+str(1 - pthresh)+',1 ')
#      sig_results_fslviewcmd.write('\n')

resultsfile = resultdir+'/sig_results_list.txt'
with open(resultsfile) as aresultfile:
    lines = aresultfile.read().splitlines()

# randpar_n500_WM_mod_merg_s4_c4b21s15d_SOPT41totalcorrectmax3_tfce_corrp_tstat2.nii.gz
# randpar_n500_GM_mod_merg_s4_c4b21s15d_SOPT41totalcorrectmax3_tfce_corrp_tstat1.nii.gz

exptag='randpar_n5000_gender_and_vbm_delta_cov_fm_sig_n500_4col_vbm'
resultdir = pathjoin(vbmdir,'randomise_runs',exptag)
for line in lines:
    fields = line.split('_')
    matfiles = [ pathjoin(matfiledir, fields[6]+'_'+fields[7]+'.mat') ]
    imgtemplate = '{0}_mod_merge_{1}.nii.gz'
    images = [vbmdir+imgtemplate.format(fields[2], fields[5])]

multirandpar(images, matfiles, designfile, niterations=5000,
    tbss=False, workdir=qsubdir, outdir=resultdir, opts=opts)
