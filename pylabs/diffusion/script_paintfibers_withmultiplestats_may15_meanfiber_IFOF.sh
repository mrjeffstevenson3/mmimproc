#!/usr/bin/env bash
cd /mnt/users/js/bbc/Slicer_scenes/Slicer_mean_tensor_slf_roi_7am_5-15-2017/toddtest
fslhd -x stats > S0_hdr.txt

grep sto_ijk S0_hdr.txt > z.txt
xoffset=`cat z.txt | awk '{ print $7 }'`
yoffset=`cat z.txt | awk '{ print $11 }'`
zoffset=`cat z.txt | awk '{ print $15 }'`
echo $xoffset $yoffset $zoffset > offsets.txt
cp /mnt/users/js/bbc/stats/stats_for_june12th/* /mnt/users/js/bbc/Slicer_scenes/Slicer_mean_tensor_slf_roi_7am_5-15-2017/toddtest
fslmerge -t stats foster_FA_CTOPPrnCS_tpos_cluster_index_cthr10.nii.gz mean_scsqT1_reg2bbctemplate_resampled2dwi.nii.gz
rm stats1*
cp stats.nii.gz stats1.nii.gz
fslchfiletype ANALYZE stats1

FILESIZE=$(stat -c%s "f.vtk")
echo $FILESIZE > filesize.txt
echo "1" > usechannel.txt
echo "1" > procmethod.txt
cp /mnt/users/js/bbc/Slicer_scenes/Slicer_mean_and_UKF_SLF_IFOF_all_stats_FB_5-17-2017/ltifof3.vtk f.vtk
cp /mnt/users/js/bbc/holdaal/base.vtk .
cp /mnt/users/js/bbc/holdaal/aal_motor.vtk .
cp ${DATADIR}/bbc/${afolder}/*/*/cuda_repol_std2_S0mf3_v5/UKF/*JHU*Left_SLF-15_model.vtk channel.vtk
${PYLABS}/pylabs/diffusion/writefiber_withpaint_with_meantensor_ifof_may18_2017

cp fnew.vtk ${afile/.vtk/_stats_ad.vtk}

