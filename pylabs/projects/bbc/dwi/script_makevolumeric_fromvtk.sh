#!/usr/bin/env bash
#set search sub-strings to identify files
run=7

#get bbc subject directories
cd ${DATADIR}/bbc
list=`ls -d sub-bbc253*`
#loop over subject dirs
for afolder in ${list}
do
echo working on ${afolder}
#get vtk files to process
cd ${DATADIR}/bbc/${afolder}/*/*/vtk_tensor_comp_run${run}

list2=`ls sub-bbc253_ses-1_dti_15dir_b1000_1_eddy_corrected_repol_std2_wls_fsl_tensor_mori_LeftPostIntCap-35.vtk`
#loop over vtk files
for afile in ${list2}
do
echo working on ${afile}
rm -f input1.vtk input2.vtk
cp ${afile} input1.vtk
cp ${afile/.vtk/_channel.vtk} input2.vtk

${PYLABS}/pylabs/diffusion/makevolumetric_fromvtk
echo ${afile}
done
done
