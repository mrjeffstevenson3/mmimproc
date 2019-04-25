#!/usr/bin/env bash
cd /media/DiskArray/shared_data/js/bbc/myvbm/ants_wempr_template/orig_wempr
list="sub-bbc101_ses-1_mpr_3 "`imglob sub*_wempr_?.nii`
ffactor=0.35
PYLABS='/home/toddr/Software/mmimproc'
imagelist="";
for subject in ${list}
do
echo working on $subject
flirt -in ${PYLABS}/data/atlases/MNI152_T1_1mm_bet_zcut.nii.gz -ref ${subject}.nii -out ${subject}_zcut.nii -omat ${subject}.mat
flirt -in ${PYLABS}/data/atlases/MNI152_T1_1mm_bet_zcut_mask.nii.gz -ref ${subject}.nii -out ${subject}_mask.nii -applyxfm -init ${subject}.mat -interp nearestneighbour
flirt -in ${PYLABS}/data/atlases/MNI152_T1_1mm-com-mask8k.nii.gz -ref ${subject}.nii -out ${subject}_mask8k.nii -applyxfm -init ${subject}.mat
declare -a com=( $(fslstats ${subject}_mask8k.nii -l 5000 -C) )
fslmaths ${subject}.nii -mas ${subject}_mask.nii ${subject}_zcut2
bet ${subject}_zcut2 ${subject}_brain -c ${com[*]} -m -f $ffactor
susan ${subject}_brain -1 1 3 1 0 ${subject}_brain_susan1
fslmaths ${subject}_brain_susan1 -mas ${subject}_brain_mask ${subject}_brain_susan
mean=`fslstats ${subject}_brain_susan -M`
fslmaths ${subject}_brain_susan -div $mean -mul 5000 ${subject}_brain_susan_nl
imagelist="$imagelist $subject ${subject}_brain_susan_nl";
done
slicesdir -o $imagelist
echo "if slicedir/index.htm passes qc then ready to build ants template"