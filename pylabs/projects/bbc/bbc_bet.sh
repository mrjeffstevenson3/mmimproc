#!/usr/bin/env bash
cd /mnt/users/js/bbc/myvbm/usable_wempr
list="sub-bbc101_ses-1_mpr_3 "`imglob sub*wempr_1.nii`
PYLABS='/home/mrjeffs/Software/pylabs'
imagelist="";
for subject in ${list}
do
echo working on $subject
flirt -in ${PYLABS}/data/atlases/MNI152_T1_1mm_bet_zcut.nii.gz -ref ${subject}.nii -out ${subject}_zcut.nii -omat ${subject}.mat
flirt -in ${PYLABS}/data/atlases/MNI152_T1_1mm-com-mask8k.nii.gz -ref ${subject}.nii -out ${subject}_mask8k.nii -applyxfm -init ${subject}.mat
declare -a zcut=( $(fslstats ${subject}_zcut.nii -l 5000 -C) )
declare -a com=( $(fslstats ${subject}_mask8k.nii -l 5000 -C) )
fslmaths ${subject}.nii -roi 0 -1 0 -1 ${zcut[2]} -1 0 1 ${subject}_zcut2
bet ${subject}_zcut2 ${subject}_brain -c ${com[*]} -m
susan ${subject}_brain -1 1 3 1 0 ${subject}_brain_susan1
fslmaths ${subject}_brain_susan1 -mas ${subject}_brain_mask ${subject}_brain_susan
imagelist="$imagelist $subject ${subject}_brain";
done
slicesdir -o $imagelist
