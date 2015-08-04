
def select_significant(resultdir, imgdir, modality)
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


    resultsfile = pathjoin(resultdir,'/sig_results_list.txt')
    with open(resultsfile) as aresultfile:
        lines = aresultfile.read().splitlines()


    for line in lines:
        fields = line.split('_')
        if modality == 'diffusion':
            matfiles = [ pathjoin(matfiledir, fields[2]+'_'+fields[3]+'.mat') ]
            images = [imgdir+imgtemplate.format(fields[5]) ]
        elif modality == 'vbm':
            matfiles = [ pathjoin(matfiledir, fields[6]+'_'+fields[7]+'.mat') ]
            imgtemplate = '{0}_mod_merge_{1}.nii.gz'
            images = [imgdir+imgtemplate.format(fields[2], fields[5])]
    return (images, matfiles)

## Other code that is different between modalities, not sure why

## VBM

# designfile = tbssdir+'scs_design4col.con'
# matfiledir = pathjoin(tbssdir,'matfiles/matfiles_gender_and_dti_delta_cov')

## DIFF

# randpar_n500_WM_mod_merg_s4_c4b21s15d_SOPT41totalcorrectmax3_tfce_corrp_tstat2.nii.gz
# randpar_n500_GM_mod_merg_s4_c4b21s15d_SOPT41totalcorrectmax3_tfce_corrp_tstat1.nii.gz
# with open(resultdir+'/sig_results_fslviewcmd.txt', 'w') as sig_results_fslviewcmd:
#      sig_results_fslviewcmd.write('fslview ')
#      for fp in sig_results_fullpath:
#          f = fp.split('/')[-1]
#          sig_results_fslviewcmd.write(f+' -b '+str(1 - pthresh)+',1 ')
#      sig_results_fslviewcmd.write('\n')

