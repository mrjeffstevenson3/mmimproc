#!/usr/bin/env bash
cd ${DATADIR}/bbc
list=`ls -d sub-bbc*`
rm ${DATADIR}/bbc/allvtk_cc.txt
for afolder in ${list}
do
echo working on ${afolder}
cd ${DATADIR}/bbc
cd ${afolder}/*/*/vtk_tensor_comp_run2
rm aal_motor.vtk
rm base.vtk
cp *aal_motor.vtk base.vtk
cp *aal_motor.vtk aal_motor.vtk


list2=`ls *tensor*CC.vtk`
for afile in ${list2}
do
echo working on ${afile}
cp ${afile} f.vtk
${PYLABS}/pylabs/diffusion/readfiber_corpus_callosum_with_ceiling
echo ${afile}
echo -n "${afile} " >> ${DATADIR}/bbc/allvtk_cc.txt
cat dti_results.txt >> ${DATADIR}/bbc/allvtk_cc.txt
done
done
