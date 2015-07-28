#!/bin/bash -e

basedir=${PWD}
#run only once for each new file
provenance discover /media/DiskArray/shared_data/js/self_control/hbm_group_data/qT1/scs318
while read subfull
do
cd hbm_group_data/qT1/${subfull}
echo working on ${subfull}
rm -f *.nii* *.hdr *.img *.mat* *.txt
parrec2nii --overwrite  --scaling='fp' *T1_MAP_02B*.PAR
provenance log "parrec2nii" *T1_MAP_02B*.PAR *T1_MAP_02B*.nii --code "parrec2nii --overwrite  --scaling='fp' *T1_MAP_02B*.PAR"
parrec2nii --overwrite  --scaling='fp' *T1_MAP_10B*.PAR
provenance log "parrec2nii" *T1_MAP_10B*.PAR *T1_MAP_10B*.nii  --code "parrec2nii --overwrite  --scaling='fp' *T1_MAP_10B*.PAR"
parrec2nii --overwrite  --scaling='fp' *T1_MAP_20B*.PAR
provenance log "parrec2nii" *T1_MAP_20B*.PAR *T1_MAP_20B*.nii  --code "parrec2nii --overwrite  --scaling='fp' *T1_MAP_20B*.PAR"
parrec2nii --overwrite  --scaling='dv' *B1MAP_SAG*.PAR
provenance log "parrec2nii" *B1MAP_SAG*.PAR *B1MAP_SAG*.nii  --code "parrec2nii --overwrite  --scaling='dv' *B1MAP_SAG*.PAR"
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

#run in main tbss dir
basedir=${PWD}
mkdir -p qT1_precorr/qT1_reg_logs
index=0
affmergelist=""
fnirtmergelist=""
holdlist=""
REF_1mm="$basedir/qT1_precorr/MNI152_invT1_1mm_brain.nii.gz"
MASK_1mm="$basedir/qT1_precorr/MNI152_T1_1mm_brain_mask"
REF="$basedir/qT1_precorr/MNI152_invT1_2mm_brain.nii.gz"
MASK="$basedir/qT1_precorr/MNI152_T1_2mm_brain_mask"
rm -f qT1_precorr/.commands_i* qT1_precorr/.commands_fin
while read subfull
do
echo working on subject ${subfull}
echo "echo scs_qT1_reg for ${subfull} started at `date`" >> qT1_precorr/.commands_i${index}
echo "flirt -in ./qT1_precorr/${subfull}_FA -ref $REF_1mm -omat ./qT1_precorr/${subfull}_FA_reg2invT1.mat -out ./qT1_precorr/${subfull}_FA_affreg2MNI -bins 256 -cost corratio -searchrx -90 90 -searchry -90 90 -searchrz -90 90 -dof 9  -interp nearestneighbour" >> qT1_precorr/.commands_i${index}
echo "fnirt --in=./qT1_precorr/${subfull}_FA_affreg2MNI --config=T1_2_MNI152_2mm --ref=$REF_1mm --refmask=$MASK_1mm  --warpres=10,10,10 --cout=./qT1_precorr/${subfull}_FA_warp2invT1" >> qT1_precorr/.commands_i${index}
echo "applywarp --ref=$REF_1mm --in=./qT1_precorr/${subfull}_FA --warp=./qT1_precorr/${subfull}_FA_warp2invT1 --out=./qT1_precorr/${subfull}_FA_reg2MNI" >> qT1_precorr/.commands_i${index}
chmod u+x ${basedir}/qT1_precorr/.commands_i${index}
declare cmdi${index}_id=`${FSLDIR}/bin/fsl_sub -l ./qT1_precorr/qT1_reg_logs -T 30 -N reg_i${index} ./qT1_precorr/.commands_i${index}`
hold1=cmdi${index}_id
echo "submitting fnirt reg condor job for ${subfull} at `date`. Should take 30 min. FNIRT JOB ID: ${!hold1}"
holdlist="$holdlist ${!hold1}"
affmergelist="$affmergelist qT1_precorr/${subfull}_FA_affreg2MNI"
fnirtmergelist="$fnirtmergelist qT1_precorr/${subfull}_FA_reg2M±NI"
index=`echo "$index + 1" | bc`
cd $basedir
done</media/DiskArray/shared_data/js/self_control/hbm_group_data/test1.txt
#scs_hbm_valid_subj_list.txt

echo $affmergelist > qT1_precorr/qT1_aff_reg2MNI_mergelist.txt
echo $fnirtmergelist > qT1_precorr/qT1_fnirt_reg2MNI_mergelist.txt
if [ $index>1 ]; then
	echo "fslmerge -t qT1_precorr/all_qT1_aff_reg2MNI `cat qT1_precorr/qT1_aff_reg2MNI_mergelist.txt`" >> qT1_precorr/.commands_i${index}
	echo "fslmerge -t qT1_precorr/all_qT1_fnirt_reg2MNI `cat qT1_precorr/qT1_fnirt_reg2MNI_mergelist.txt`" >> qT1_precorr/.commands_i${index}
	chmod u+x ${basedir}/qT1_precorr/.commands_i${index}
	declare cmdi${index}_id=`${FSLDIR}/bin/fsl_sub -l ./qT1_precorr/qT1_reg_logs -T 30 -N reg_i${index} -j $holdlist ./qT1_precorr/.commands_i${index}`
	hold1=cmdi${index}_id
	echo "submitting cleanup routine at `date` which waits for all other reg jobs to be done. cleanup job id=${!hold1}"
	echo "job ids waiting for completion: $holdlist"
fi
