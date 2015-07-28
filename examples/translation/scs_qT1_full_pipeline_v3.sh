#!/bin/bash
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
#old stuff
#bet my_structural my_betted_structural
#flirt -ref ${FSLDIR}/data/standard/MNI152_T1_2mm_brain -in my_betted_structural -omat my_affine_transf.mat
#fnirt --in=my_structural --aff=my_affine_transf.mat --cout=my_nonlinear_transf --config=T1_2_MNI152_2mm
#applywarp --ref=${FSLDIR}/data/standard/MNI152_T1_2mm --in=my_structural --warp=my_nonlinear_transf --out=my_warped_structural
# --premat=./qT1_precorr/${subfull}_FA_reg2invT1.mat
#--aff=./qT1_precorr/${subfull}_FA_reg2invT1.mat

