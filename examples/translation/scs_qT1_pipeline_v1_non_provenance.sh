#!/bin/bash -e

basedir=${PWD}

while read subfull
do
cd hbm_group_data/qT1/${subfull}
echo working on ${subfull}
rm -f *.nii* *.hdr *.img *.mat* *.txt
parrec2nii --overwrite  --scaling='fp' *T1_MAP_02B*.PAR
parrec2nii --overwrite  --scaling='fp' *T1_MAP_10B*.PAR
parrec2nii --overwrite  --scaling='fp' *T1_MAP_20B*.PAR
parrec2nii --overwrite  --scaling='dv' *B1MAP_SAG*.PAR
B1MAP=`imglob *B1MAP_SAG*.nii`
T1REF=`imglob *T1_MAP_02B*.nii`
echo "B1 map file name is ${B1MAP} and T1 referense file name is ${T1REF}"
echo -e "1 0 0 0\\n0 1 0 0 \\n0 0 1 0\\n0 0 0 1\\n" > identity.mat
fslhd -x ${T1REF} > t1ref_temphdr.txt
fslmerge -t t1flip_all_orig1 `imglob *T1_MAP*.nii*`
fslmaths t1flip_all_orig1 -mul 1 t1flip_all_orig -odt float
bet $T1REF ${T1REF}_brain -m
fslroi $B1MAP b1map_mag 0 1
fslroi $B1MAP b1map_phase 2 1
mcflirt -in t1flip_all_orig -out t1all_reg -mats -plots -refvol 0 -rmsrel -rmsabs
flirt -in b1map_mag -ref $T1REF -init identity.mat -o b1map_mag_upsample -omat b1mag2t1ref.mat
flirt -in b1map_phase -ref $T1REF -applyxfm -init b1mag2t1ref.mat -out b1map_phase_reg2t1map
fslmaths b1map_phase_reg2t1map -s 5 -mas ${T1REF}_brain_mask b1map_phase_reg2t1map_s5_masked -odt float
fslchfiletype ANALYZE t1all_reg t1flip_all.hdr
fslchfiletype ANALYZE b1map_phase_reg2t1map_s5_masked out_image.hdr
/home/toddr/Software/t1flip_with3_with3differentoutputs
fslchfiletype NIFTI t1image_b1corr ${subfull}_qT1.nii
fslchfiletype NIFTI t1flip_all_b1corr ${subfull}_all_t1flips_b1corr.nii
fslchfiletype NIFTI t1image_uncorr ${subfull}_qT1_nob1corr.nii
fslchfiletype NIFTI t1image_intensitycorr ${subfull}_qT1_intensitycorr.nii
fslcreatehd t1ref_temphdr.txt ${subfull}_qT1.nii
fslcreatehd t1ref_temphdr.txt ${subfull}_all_t1flips_b1corr.nii
fslcreatehd t1ref_temphdr.txt ${subfull}_qT1_nob1corr.nii
fslcreatehd t1ref_temphdr.txt ${subfull}_qT1_intensitycorr.nii
fslmaths  ${subfull}_qT1 -thr 1 -uthr 8000 -ero  ${subfull}_qT1_thr8000_ero
cd $basedir
done</media/DiskArray/shared_data/js/self_control/hbm_group_data/test1.txt
#/media/DiskArray/shared_data/js/self_control/hbm_group_data/scs_hbm_valid_subj_list.txt
