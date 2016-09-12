#!/usr/bin/env bash
#this script takes the paired template after spm segmentation batch proc of template output
#Pairs are set in designpaired18.mat and defined in /media/DiskArray/shared_data/js/bbc/myvbm/ants_vbm_template_pairedLH/spmseg/mergelist.txt
fname='brain_susan_nl_comrolldeformed.nii.gz'
cd /media/DiskArray/shared_data/js/bbc/myvbm/ants_vbm_template_pairedLH
fslmaths bbc_pairedLH_template.nii.gz -thr 0.4 -bin -fillh bbc_pairedLH_template_mask.nii.gz
mergelist=`cat ./spmseg/mergelist.txt`
GMmergelist="";
WMmergelist="";
# heal headers
for f in $mergelist; do
    echo working on $f
    fslchfiletype NIFTI_GZ ./spmseg/${f};
    fslcreatehd ./spmseg/${f}_hdr.txt ./spmseg/${f}.nii.gz;   # heal orig header
    fslcreatehd ./spmseg/${f}_hdr.txt ./spmseg/c1${f}.nii;    # apply orig header to newly generated GM segments
    fslcreatehd ./spmseg/${f}_hdr.txt ./spmseg/c2${f}.nii;    # apply orig header to newly generated WM segments
    GMmergelist="${GMmergelist} ./spmseg/c1${f}.nii"
    WMmergelist="${WMmergelist} ./spmseg/c2${f}.nii"
    fslorient -getqform ./spmseg/${f}.nii.gz
    fslorient -getqform ./spmseg/c1${f}.nii
    fslorient -getqform ./spmseg/c2${f}.nii
done;
# make masks
fslmerge -t ./spmseg/all_GM $GMmergelist;  # make GM all files to check for shimmy
fslmerge -t ./spmseg/all_WM $WMmergelist; # make WM all files to check for shimmy
fslmaths ./spmseg/all_GM -Tmean -bin  ./stats/all_GM_mask
fslmaths ./spmseg/all_WM -Tmean -bin  ./stats/all_WM_mask
GMmodmergelist=''
WMmodmergelist=''
for f in $mergelist; do
    bn=${f/deformed*/};
    ANTSJacobian 3 ./jac/${bn}Warp.nii.gz ./jac/${bn} 0 bbc_pairedLH_template_mask.nii.gz 1
    fslmaths ./spmseg/c1${f} -div 255 -mul ./jac/${bn}jacobian.nii.gz ./jac/GM_${bn}_mod;
    fslmaths ./spmseg/c2${f} -div 255 -mul ./jac/${bn}jacobian.nii.gz ./jac/WM_${bn}_mod;
    GMmodmergelist="${GMmodmergelist} ./jac/GM_${bn}_mod";
    WMmodmergelist="${WMmodmergelist} ./jac/WM_${bn}_mod";
done;

fslmerge -t ./stats/all_GM_mod $GMmodmergelist
fslmerge -t ./stats/all_WM_mod $WMmodmergelist
cd stats
#smooth, filter and randomise paired bbc vbm post jacobian
for i in all_GM_mod all_WM_mod; do for j in 2 3 4; do fslmaths $i -s $j ${i}_s${j}; randomise_parallel -i ${i}_s${j} -m ${i:0:6}_mask -o ${i}_s${j}_pairedLH_n10000 -d designpaired18.mat -t designpaired18.con -T -n 10000 -V; done; done



