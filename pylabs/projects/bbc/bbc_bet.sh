#!/usr/bin/env bash
cd /mnt/users/js/bbc/sub-bbc105/ses-1/anat
subject='sub-bbc105_ses-1_wempr_1'
PYLABS='/home/mrjeffs/Software/pylabs'
flirt -in ${PYLABS}/data/atlases/MNI152_T1_1mm_bet_zcut.nii.gz -ref ${subject}.nii -out ${subject}_zcut.nii -omat ${subject}.mat
flirt -in ${PYLABS}/data/atlases/MNI152_T1_1mm-com-mask8k.nii.gz -ref ${subject}.nii -out ${subject}_mask8k.nii -applyxfm -init ${subject}.mat
declare -a zcut=( $(fslstats ${subject}_zcut.nii -l 5000 -C) )
declare -a com=( $(fslstats ${subject}_mask8k.nii -l 5000 -C) )
fslmaths ${subject}.nii -roi 0 -1 0 -1 ${zcut[2]} -1 0 1 ${subject}_zcut2
bet ${subject}_zcut2 ${subject}_brain -c ${com[*]}

