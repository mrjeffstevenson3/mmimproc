#!/usr/bin/env bash
cd /media/DiskArray/shared_data/js/bbc/myvbm/ants_vbm_template/orig_vbm
list="sub-bbc116_ses-1_wempr_1 "`imglob sub*_mpr_?.nii`
ffactor=0.45
PYLABS='/home/toddr/Software/pylabs'
imagelist="";
for subject in ${list}
do
echo working on $subject
flirt -in ${PYLABS}/data/atlases/MNI152_T1_1mm_bet_zcut.nii.gz -ref ${subject}.nii -out ${subject}_zcut.nii -omat ${subject}.mat
flirt -in ${PYLABS}/data/atlases/MNI152_T1_1mm_bet_zcut_mask.nii.gz -ref ${subject}.nii -out ${subject}_mask.nii -applyxfm -init ${subject}.mat -interp nearestneighbour
flirt -in ${PYLABS}/data/atlases/MNI152_T1_1mm-com-mask8k.nii.gz -ref ${subject}.nii -out ${subject}_mask8k.nii -applyxfm -init ${subject}.mat
#declare -a zcut=( $(fslstats ${subject}_zcut.nii -l 5000 -C) )
declare -a com=( $(fslstats ${subject}_mask8k.nii -l 5000 -C) )
#fslmaths ${subject}.nii -roi 0 -1 0 -1 ${zcut[2]} -1 0 1 ${subject}_zcut2
fslmaths ${subject}.nii -mas ${subject}_mask.nii ${subject}_zcut2
bet ${subject}_zcut2 ${subject}_brain -c ${com[*]} -m -f $ffactor
susan ${subject}_brain -1 1 3 1 0 ${subject}_brain_susan1
fslmaths ${subject}_brain_susan1 -mas ${subject}_brain_mask ${subject}_brain_susan
mean=`fslstats ${subject}_brain_susan -M`
fslmaths ${subject}_brain_susan -div $mean -mul 5000 ${subject}_brain_susan_nl
imagelist="$imagelist $subject ${subject}_brain_susan_nl";
done
slicesdir -o $imagelist
