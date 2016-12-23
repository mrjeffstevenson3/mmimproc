#!/u#!/usr/bin/env bash
#set search sub-strings to identify files
sub70=IFOF-70
sub158=IFOF-158
subcc=mori_CC
sub35=PostIntCap-35
sub123=PostIntCap-123
sub43=SLF-43
sub131=SLF-131
#get bbc subject directories
cd ${DATADIR}/bbc
list=`ls -d sub-bbc*`
rm -f ${DATADIR}/bbc/allvtk_channel.txt
#loop over subject dirs
for afolder in ${list}
do
echo working on ${afolder}
#get vtk files to process
cd ${DATADIR}/bbc/${afolder}/*/*/vtk_tensor_comp_run3
list2=`ls *tensor*.vtk`
#loop over vtk files
for afile in ${list2}
do
echo working on ${afile}
rm -f base.vtk aal_motor.vtk
if [[ "$afile" == *"$sub70"* ]]; then
cp *Left_frontal*.vtk base.vtk
cp *Left_occip*.vtk aal_motor.vtk
cp *channel*.vtk channel.vtk
fi
cp ${afile} f.vtk
${PYLABS}/pylabs/diffusion/readfiber_corpus_callosum_with_ceiling
echo ${afile}
echo -n "${afile} " >> ${DATADIR}/bbc/allvtk_channel.txt
cat dti_results.txt >> ${DATADIR}/bbc/allvtk_channel.txt
done
done
sr/bin/env bash