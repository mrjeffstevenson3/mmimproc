#!/bin/bash

basedir=${PWD}

while read subfull
do
echo working on ${subfull}
cd hbm_group_data/qT1/${subfull}
#parrec2nii --scaling='dv' --overwrite *.PAR &
#sub=`echo ${subfull} | awk ' { print substr($0, 1, 6) } ' ` ;
#parfile=`echo ${subfull} | cut -d '/' -f3 | cut -d '.' -f1`
#sub=`echo ${subfull} | cut -d '/' -f1 ` ;
#for dtimeas in qT1_precorr
#do
#cp ${subfull}.PAR /media/DiskArray/shared_data/js/self_control/hbm_group_data/qT1/${sub}/
#cp ${subfull}.REC /media/DiskArray/shared_data/js/self_control/hbm_group_data/qT1/${sub}/
##done
fslhd -x *T1_MAP_02B*.nii > t1map_temphdr.txt
cd $basedir
done</media/DiskArray/shared_data/js/self_control/hbm_group_data/scs_hbm_valid_subj_list.txt