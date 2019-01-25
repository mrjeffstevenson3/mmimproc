allfiledir='/media/DiskArray/shared_data/js/self_control/hbm_group_data/tbss_19subj/workdir_thr1p5_v3/stats'
DATADIR='/media/DiskArray/shared_data/js/self_control/hbm_group_data/tbss_19subj/workdir_thr1p5_v3/stats/no_gender_cov_n5000_fm_sig_n500_thr95'
cp /media/DiskArray/shared_data/js/self_control/hbm_group_data/tbss_19subj/workdir_thr1p5_v3/stats/EF_and_Brain_mar26_2015.csv ${DATADIR}/behav.csv
cp /media/DiskArray/shared_data/js/self_control/hbm_group_data/tbss_19subj/workdir_thr1p5_v3/stats/list_of_subjects_mri19.txt ${DATADIR}
TODDSW='/home/toddr/Software'
rm ${DATADIR}/all*report.txt
cd ${DATADIR}
rm plo*
list=`ls out*corrp*.nii.gz`

for afile in ${list}
do
echo working on ${afile}

#out_L2_c2b36s19d_inhibition_n5000_no_gender_cov_fm_n500_thr95_tfce_corrp_tstat2.nii.gz
dtimeas=`echo ${afile} | awk ' { keep=index($0,".nii.gz")-1 ; print substr($0, 5, 2) } ' ` ;
behavcol=`echo ${afile} | awk ' { keep=index($0,".nii.gz")-1 ; print substr($0, 11, 2) } ' ` ;
tstat=`echo ${afile} | awk ' { keep=index($0,".nii.gz")-1 ; print substr($0, keep, 1) } ' ` ;
echo $behavcol > behavcol.txt
echo $dtimeas > dtimeas.txt
echo $tstat > tstat.txt
echo "1 19 1 19" > groupnums.txt         # this is the start and end of 2 groups
echo "317 322 324 328 332 334 335 341 347 353 364 370 371 376 379 381 384 385 396" > subjectids.txt
echo "line" >> subjectids.txt
echo "0.95" > thresh.txt                  # this is the threshold for significance to test stats as belonging in anatomical region.
rm afile.*
rm afile2.*
rm afile3.*
cp $afile afile.nii.gz
fslchfiletype ANALYZE afile.nii.gz
cp ${allfiledir}/all_${dtimeas}_skeletonised.nii.gz afile2.nii.gz
cp ${allfiledir}/all_MO_skeletonised.nii.gz afile3.nii.gz
fslchfiletype ANALYZE afile2.nii.gz
fslchfiletype ANALYZE afile3.nii.gz
cp /home/toddr/Software/mori* .
cp /home/toddr/Software/JHU* .
cp /home/toddr/Software/Cere* .
cp /home/toddr/Software/cere*.txt .


echo $afile > passname.txt
${TODDSW}/anatomy_mean_dti_behav_scs_july15_2015_cereb2
listlab=`ls moria*.txt`
for afilelab in ${listlab}
do
ssconvert ${afilelab} filtered${afilelab/.txt*/}.xls
done


echo $afile >> ${DATADIR}/all_label_report.txt
cat labeled_reports.txt >> ${DATADIR}/all_label_report.txt
done



