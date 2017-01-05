#!/u#!/usr/bin/env bash
#set search sub-strings to identify files
sub70=IFOF-45
sub158=IFOF-158
subcc=mori_CC
sub35=PostIntCap-35
sub123=PostIntCap-123
sub43=SLF-43
sub131=SLF-131
#get bbc subject directories
cd ${DATADIR}/bbc
list=`ls -d sub-bbc253*`
rm -f ${DATADIR}/bbc/allvtk_channel.txt
#loop over subject dirs
for afolder in ${list}
do
echo working on subject ${afolder}
#get vtk files to process
cd ${DATADIR}/bbc/${afolder}/*/*/vtk_tensor_comp_run7

list2=`ls *sub-bbc253_ses-1_dti_15dir_b1000_1_eddy_corrected_repol_std2_wls_fsl_tensor_medfilt_mori_LeftPostIntCap-35.vtk`
#loop over vtk files
for afile in ${list2}
do

rm -f base.vtk aal_motor.vtk channel.vtk
echo $afile $sub35
FILESIZE=$(stat -c%s "$afile")
echo $FILESIZE > filesize.txt
if [[ "$afile" == *"$sub35"* ]]; then
echo working on ${afile}
cp *base*.vtk base.vtk
cp *aal*.vtk aal_motor.vtk
cp *JHU*Left_CSP-3.vtk channel.vtk
cp ${afile} f.vtk
${PYLABS}/pylabs/diffusion/readfiber_withchannel_test
echo ${afile}
echo -n "${afile} " >> ${DATADIR}/allvtk_channel.txt
cat dti_results.txt >> ${DATADIR}/allvtk_channel.txt
fi


done
done
