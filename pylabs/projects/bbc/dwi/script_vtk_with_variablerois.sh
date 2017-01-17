#!/usr/bin/env bash
#set search sub-strings to identify files
run=7
sub70=IFOF-45
sub158=IFOF-133
subcc=mori_CC
sub35=PostIntCap-35
sub123=PostIntCap-123
sub43=SLF-43
sub131=SLF-131
#get bbc subject directories
cd ${DATADIR}/bbc
#list=`ls -d sub-bbc*`
list=sub-bbc253
rm -f ${DATADIR}/bbc/allvtk_channel_run${run}.txt
#loop over subject dirs
for afolder in ${list}
do
echo working on ${afolder}
#get vtk files to process
cd ${DATADIR}/bbc/${afolder}/*/*/vtk_tensor_comp_run${run}

#list2=`ls *tensor*.vtk`
list2=`ls sub-bbc253_ses-1_dti_15dir_b1000_1_eddy_corrected_repol_std2_wls_fsl_tensor_mori_LeftPostIntCap-35.vtk`
S0_fname=`basename ../${afolder}*_S0_brain.nii`
fslchfiletype ANALYZE ../${S0_fname} S0.hdr
cp S0.hdr newvolume.hdr
fslhd -x ../${S0_fname} > S0_hdr.txt

#loop over vtk files
for afile in ${list2}
do
echo working on ${afile}
FILESIZE=$(stat -c%s "$afile")
echo $FILESIZE > filesize.txt
rm -f base.vtk aal_motor.vtk channel.vtk
if [[ "$afile" == *"$sub70"* ]]; then
cp *Left_frontal*.vtk base.vtk
cp *Left_occip*.vtk aal_motor.vtk
cp *JHU*Left_IFOF-11.vtk channel.vtk
fi
if [[ "$afile" == *"$sub158"* ]]; then
cp *Right_frontal*.vtk base.vtk
cp *Right_occip*.vtk aal_motor.vtk
cp *JHU*Right_IFOF-12.vtk channel.vtk
fi
if [[ "$afile" == *"$subcc"* ]]; then
cp *aal_motor*.vtk base.vtk
cp *aal_motor*.vtk aal_motor.vtk

fi
if [[ "$afile" == *"$sub35"* ]]; then
cp *base*.vtk base.vtk
cp *aal_motor*.vtk aal_motor.vtk
cp *JHU*Left_CSP-3.vtk channel.vtk
fi
if [[ "$afile" == *"$sub123"* ]]; then
cp *base*.vtk base.vtk
cp *aal_motor*.vtk aal_motor.vtk
cp *JHU*Right_CSP-4.vtk channel.vtk
fi
if [[ "$afile" == *"$sub43"* ]]; then
cp *Left_STG-MTG-18-20*.vtk base.vtk
cp *Left_pre-postCentGyr-6-7*.vtk aal_motor.vtk
cp *JHU*Left_SLF-15.vtk channel.vtk
fi
if [[ "$afile" == *"$sub131"* ]]; then
cp *Right_STG-MTG-106-108*.vtk base.vtk
cp *Right_pre-postCentGyr-94-95*.vtk aal_motor.vtk
cp *JHU*Right_SLF-16.vtk channel.vtk
fi
cp ${afile} f.vtk
if [[ "$afile" == *"$subcc"* ]]; then
${PYLABS}/pylabs/diffusion/readfiber_corpus_callosum_with_ceiling
else
${PYLABS}/pylabs/diffusion/readfiber_withchannel_test
${PYLABS}/pylabs/diffusion/makevolumetric_fromvtk
cp fnew.vtk ${afile/.vtk/_channel.vtk}
fslchfiletype NIFTI_GZ newvolume.hdr ${afile/.vtk/.nii.gz}
fslcreatehd S0_hdr.txt ${afile/.vtk/.nii.gz}
fi
echo ${afile}
echo -n "${afile} " >> ${DATADIR}/bbc/allvtk_channel_run${run}.txt
cat dti_results.txt >> ${DATADIR}/bbc/allvtk_channel_run${run}.txt
done
done
