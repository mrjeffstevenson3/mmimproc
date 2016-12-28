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
list=`ls -d sub-bbc105*`
rm -f ${DATADIR}/bbc/allvtk_channel.txt
#loop over subject dirs
for afolder in ${list}
do
echo working on subject ${afolder}
#get vtk files to process
cd ${DATADIR}/bbc/${afolder}/*/*/vtk_tensor_comp_run5
list2=`ls *tensor*.vtk`
#loop over vtk files
for afile in ${list2}
do

rm -f base.vtk aal_motor.vtk channel.vtk
echo $afile $sub70
if [[ "$afile" == *"$sub70"* ]]; then
echo working on ${afile}
cp *Left_frontal*.vtk base.vtk
cp *Left_occip*.vtk aal_motor.vtk
cp *JHU*Left_IFOF-11.vtk channel.vtk
cp ${afile} f.vtk
${PYLABS}/pylabs/diffusion/readfiber_withchannel
echo ${afile}
echo -n "${afile} " >> ${DATADIR}/bbc/allvtk_channel.txt
cat dti_results.txt >> ${DATADIR}/bbc/allvtk_channel.txt
fi


done
done
