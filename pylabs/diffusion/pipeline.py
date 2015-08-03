import os, glob
from os.path import join as pathjoin
import niprov
from pylabs.correlation.behavior import csv2fslmat
from pylabs.correlation.regfilt import multiregfilt
from pylabs.correlation.randpar import multirandpar
from pylabs.utils.paths import getlocaldataroot
from niprov.options import NiprovOptions
opts = NiprovOptions()
opts.dryrun = True
opts.verbose = True

exptag='gender_and_dti_delta_cov'

subjects= [ 317, 322, 324, 328, 332, 334, 335, 341, 347, 353, 364, 370, 371, 
    376, 379, 381, 384, 385, 396 ]
imgtemplate = 'all_{0}_skeletonised.nii.gz'
measures = ['F1', 'F2', 'FA', 'L1', 'MD', 'MO', 'RA', 'AD', 'L2', 'L3']
skellist = [imgtemplate.format(m) for m in measures]
fs = getlocaldataroot()
tbssdir = fs+'js/self_control/hbm_group_data/tbss_19subj/workdir_thr1p5_v3/stats/'
matfiledir = pathjoin(tbssdir,'matfiles','matfiles_'+exptag)
resultdir = pathjoin(tbssdir,'randpar',exptag)
qsubdir = resultdir+'qsubdir_defunctcommands'
behavdir = fs+'js/self_control/behavioral_data/behav_from_andy_march27_2015/'
csvfile = behavdir+'EF_and_Brain_july08_2015_Meq0_delta.csv'
maskfile = tbssdir+'mean_FA_skeletonised_mask.nii.gz'
images = [tbssdir+i for i in skellist]
masks = {img: maskfile for img in images} # Mask is the same for all images
niprov.add(csvfile)
[niprov.add(img) for img in images]


## Randomize n500 test run
# designfile = tbssdir+'scs_design4col.con'
# assert os.path.isfile(designfile)
# matfiles = csv2fslmat(csvfile, cols=range(5, 39), covarcols=[2, 41],
#     selectSubjects=subjects, groupcol=True, outdir=matfiledir, opts=opts)
# multirandpar(images, matfiles, designfile, masks=masks, niterations=500,
#     tbss=True, workdir=qsubdir, outdir=resultdir, opts=opts)

# find significant results from n500 run to pass along to n5000
pthresh = 0.05
corrpfiles = glob.glob(resultdir+'/*_corrp_tstat*.nii.gz')
sig_results_fullpath = []
with open(resultdir+'/sig_results_list_fullpath.txt', 'w') as outfile_fullpath:
    for astat in corrpfiles:
        statcmd = 'fslstats '+astat+' -R'
        statout1 = subprocess.Popen(statcmd, shell=True, stdout=subprocess.PIPE)
        statout2 = statout1.stdout.read()
        statout3 = statout2.split()
        pval = 1 - float(statout3[1])
        if pval <= pthresh:
            print('+++++ found p='+' '+str(pval)+' in file '+os.path.basename(astat).split('.')[0])
            outfile_fullpath.write(astat+'\n')
            sig_results_fullpath.append(astat)

with open(resultdir+'/sig_results_list.txt', 'w') as sig_results:
     for fp in sig_results_fullpath:
         f = fp.split('/')[-1]
         sig_results.write(f+'\n')


resultsfile = pathjoin(resultdir,'/sig_results_list_hard_behav_meas.txt')
with open(resultsfile) as aresultfile:
    lines = aresultfile.read().splitlines()


designfile = tbssdir+'scs_design4col.con'
matfiledir = pathjoin(tbssdir,'matfiles/matfiles_gender_and_dti_delta_cov')
exptag='gender_and_dti_delta_cov_4col_n5000_select'
resultdir = pathjoin(tbssdir,'randomise_runs',exptag)
for line in lines:
    fields = line.split('_')
    matfiles = [ pathjoin(matfiledir, fields[2]+'_'+fields[3]+'.mat') ]
    images = [tbssdir+imgtemplate.format(fields[5]) ]

multirandpar(images, matfiles, designfile, masks=masks, niterations=5000,
    tbss=True, workdir=qsubdir, outdir=resultdir, opts=opts)
