#!/usr/bin/env bash
cd ${DATADIR}/bbc
list=`ls -d sub-bbc*`
rm ${DATADIR}/bbc/allvtk_run3.txt
for afolder in ${list}
do
echo working on ${afolder}
cd ${DATADIR}/bbc
cd ${afolder}/*/*/vtk_tensor_comp_run3

list2=`ls *tensor*.vtk`
for afile in ${list2}
do
echo working on ${afile}
rm aal_motor.vtk
rm base.vtk
cp *aal_motor.vtk base.vtk
cp *aal_motor.vtk aal_motor.vtk

sub70=IFOF-70
sub158=IFOF-158
subcc=mori_CC
sub35=PostIntCap-35
sub123=PostIntCap-123
sub43=SLF-43
sub131=SLF-131

rm base.vtk
rm aal_motor.vtk
if [[ "$afile" == *"$sub70"* ]]; then
cp *Left_frontal*.vtk base.vtk
cp *Left_occip*.vtk aal_motor.vtk
fi
if [[ "$afile" == *"$sub158"* ]]; then
cp *Right_frontal*.vtk base.vtk
cp *Rigth_occip*.vtk aal_motor.vtk
fi
if [[ "$afile" == *"$subcc"* ]]; then
cp *aal_motor*.vtk base.vtk
cp *aal_motor*.vtk aal_motor.vtk
fi
if [[ "$afile" == *"$sub35"* ]]; then
cp *base*.vtk base.vtk
cp *aal_motor*.vtk aal_motor.vtk
fi
if [[ "$afile" == *"$sub123"* ]]; then
cp *base*.vtk base.vtk
cp *aal_motor*.vtk aal_motor.vtk
fi
if [[ "$afile" == *"$sub43"* ]]; then
cp *Left_STG-MTG-18-20*.vtk base.vtk
cp *Left_pre-postCentGyr-6-7*.vtk aal_motor.vtk
fi
if [[ "$afile" == *"$sub131"* ]]; then
cp *Right_STG-MTG-106-108*.vtk base.vtk
cp *Right_pre-postCentGyr-94-95*.vtk aal_motor.vtk
fi
cp ${afile} f.vtk
${PYLABS}/pylabs/diffusion/readfiber_corpus_callosum_with_ceiling
echo ${afile}
echo ${afile} >> ${DATADIR}/bbc/allvtk_run3.txt
cat dti_results.txt >> ${DATADIR}/bbc/allvtk_run3.txt
done
done
