#!/usr/bin/env bash
#this script reads a list of vtk files produced by reg_atlas_MNI2dwi.py and generates results files
#processing flag: 0=no channel, floor, or target, just vtk stats for whole fiber bundle;
#   1=channel only; 2=base only ; 3= vtk target only; 4=base and target together; 5=all - channel, base, target
proc_method=1
run=7
#set search sub-strings to identify vtk files
sub70=IFOF-45x
sub158=IFOF-133x
subcc=mori_CC
sub35=PostIntCap-35
sub123=PostIntCap-123
sub43=SLF-43
sub131=SLF-131
#get bbc subject directories
cd ${DATADIR}/bbc
list=`python -c "from pylabs.projects.bbc.pairing import dwipairing; \
    print(' '.join(['sub-bbc{sid}'.format(sid=str(s)) for s, ses, m, r in dwipairing]))"`
#list='sub-bbc108 sub-bbc211 sub-bbc231 sub-bbc241 sub-bbc243 sub-bbc249 sub-bbc253'
#list=sub-bbc101
#list=`ls -d sub-bbc*`
#rm -f ${DATADIR}/bbc/allvtk_channel_run${run}.txt
#loop over subject dirs
for afolder in ${list}
do
echo working on ${afolder}
#get vtk files to process
cd ${DATADIR}/bbc/${afolder}/*/*/vtk_tensor_comp_run${run}
#rm -f *_channel*
#list2=`ls *wls_fsl_tensor_medfilt*[^_channel].vtk *ols_fsl_tensor_medfilt*[^_channel].vtk *ols_dipy_tensor_medfilt*[^_channel].vtk \
#          *wls_dipy_tensor_medfilt*[^_channel].vtk`
list2=`ls *wls_fsl_tensor_medfilt*[^_channel].vtk *ols_fsl_tensor_medfilt*[^_channel].vtk`
#list2=`ls sub-bbc243_ses-1_dti_15dir_b1000_1_eddy_corrected_repol_std2_wls_fsl_tensor_medfilt_mori_CC.vtk`
#list2=sub-bbc253_ses-1_dti_15dir_b1000_1_eddy_corrected_repol_std2_wls_fsl_tensor_mori_RightPostIntCap-123.vtk
#list2=sub-bbc253_ses-1_dti_15dir_b1000_1_eddy_corrected_repol_std2_wls_fsl_tensor_medfilt_mori_CC.vtk
#list2=sub-bbc243_ses-1_dti_15dir_b1000_1_eddy_corrected_repol_std2_wls_fsl_tensor_medfilt_mori_RightPostIntCap-123.vtk
#list2=sub-bbc243_ses-1_dti_15dir_b1000_1_eddy_corrected_repol_std2_wls_fsl_tensor_medfilt_mori_LeftPostIntCap-35.vtk
#list2=sub-bbc101_ses-2_dti_15dir_b1000_1_eddy_corrected_repol_std2_wls_dipy_tensor_medfilt_mori_Left_SLF-43.vtk
S0_fname=`basename ../${afolder}*_S0_brain.nii`
fslhd -x ../*_S0_brain.nii > S0_hdr.txt

grep sto_ijk S0_hdr.txt > z.txt
xoffset=`cat z.txt | awk '{ print $7 }'`
yoffset=`cat z.txt | awk '{ print $11 }'`
zoffset=`cat z.txt | awk '{ print $15 }'`
echo $xoffset $yoffset $zoffset > offsets.txt

fslchfiletype ANALYZE ../${S0_fname}.nii S0.hdr
qform=`fslorient -getqform ../${S0_fname}`

#loop over vtk files
for afile in ${list2}
do
echo working on ${afile}
FILESIZE=$(stat -c%s "$afile")
echo $FILESIZE > filesize.txt
rm -f base.vtk aal_motor.vtk channel.vtk fnew.vtk fnew1.vtk f.vtk usechannel.txt proc_method.txt
echo "1" > usechannel.txt
echo "1" > procmethod.txt

cp ${afile} f.vtk
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
#special case for corpus callosum
if [[ "$afile" == *"$subcc"* ]]; then
    cp *aal_motor*.vtk base.vtk
    cp *aal_motor*.vtk aal_motor.vtk
    echo "0" > usechannel.txt
    ${PYLABS}/pylabs/diffusion/readfiber_corpus_callosum_with_ceiling
    echo -n "${afile/.vtk/_nochannel.vtk} " >> ${DATADIR}/bbc/allvtk_channel_run${run}.txt
    cat dti_results.txt >> ${DATADIR}/bbc/allvtk_channel_run${run}.txt
    cp fnew.vtk ${afile/.vtk/_nochannel.vtk}
    ${PYLABS}/pylabs/diffusion/makevolumetric_fromvtk
    fslchfiletype NIFTI_GZ newvolume.hdr ${afile/.vtk/_channel.nii.gz}
    fslorient -setqform $qform ${afile/.vtk/_channel.nii.gz}
    fslorient -copyqform2sform ${afile/.vtk/_channel.nii.gz}
    fslmaths ${afile/.vtk/_channel.nii.gz} -bin ${afile/.vtk/_channel_bin.nii.gz}
    echo -n "${afile/.vtk/_channel.vtk} " >> ${DATADIR}/bbc/allvtk_channel_run${run}.txt
    cat dti_results.txt >> ${DATADIR}/bbc/allvtk_channel_run${run}.txt
    rm -f fnew.vtk
    echo "1" > usechannel.txt
    cp *JHU*Forceps_Major-9.vtk channel.vtk
    ${PYLABS}/pylabs/diffusion/readfiber_withchannel_test
    ${PYLABS}/pylabs/diffusion/makevolumetric_fromvtk
    cp fnew.vtk ${afile/.vtk/_Forceps_Major_channel.vtk}
    fslchfiletype NIFTI_GZ newvolume.hdr ${afile/.vtk/_Forceps_Major_channel.nii.gz}
    fslorient -setqform $qform ${afile/.vtk/_Forceps_Major_channel.nii.gz}
    fslorient -copyqform2sform ${afile/.vtk/_Forceps_Major_channel.nii.gz}
    fslmaths ${afile/.vtk/_Forceps_Major_channel} -bin ${afile/.vtk/_Forceps_Major_channel_bin}
    echo -n "${afile/.vtk/_Forceps_Major_channel.vtk} " >> ${DATADIR}/bbc/allvtk_channel_run${run}.txt
    cat dti_results.txt >> ${DATADIR}/bbc/allvtk_channel_run${run}.txt
    rm -f fnew.vtk
    cp *JHU*Forceps_Minor-10.vtk channel.vtk
    ${PYLABS}/pylabs/diffusion/readfiber_withchannel_test
    ${PYLABS}/pylabs/diffusion/makevolumetric_fromvtk
    cp fnew.vtk ${afile/.vtk/_Forceps_Minor_channel.vtk}
    fslchfiletype NIFTI_GZ newvolume.hdr ${afile/.vtk/_Forceps_Minor_channel.nii.gz}
    fslorient -setqform $qform ${afile/.vtk/_Forceps_Minor_channel.nii.gz}
    fslorient -copyqform2sform ${afile/.vtk/_Forceps_Minor_channel.nii.gz}
    fslmaths ${afile/.vtk/_Forceps_Minor_channel} -bin ${afile/.vtk/_Forceps_Minor_channel_bin}
    echo -n "${afile/.vtk/_Forceps_Minor_channel.vtk} " >> ${DATADIR}/bbc/allvtk_channel_run${run}.txt
    cat dti_results.txt >> ${DATADIR}/bbc/allvtk_channel_run${run}.txt
    rm -f fnew.vtk
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
if [[ "$afile" != *"$subcc"* ]]; then
${PYLABS}/pylabs/diffusion/readfiber_withchannel_test
${PYLABS}/pylabs/diffusion/makevolumetric_fromvtk
cp fnew.vtk ${afile/.vtk/_channel.vtk}
fslchfiletype NIFTI_GZ newvolume.hdr ${afile/.vtk/_channel.nii.gz}
fslorient -setqform $qform ${afile/.vtk/_channel.nii.gz}
fslorient -copyqform2sform ${afile/.vtk/_channel.nii.gz}
fslmaths ${afile/.vtk/_channel.nii.gz} -bin ${afile/.vtk/_channel_bin.nii.gz}
echo "finished with ${afile}"
echo -n "${afile} " >> ${DATADIR}/bbc/allvtk_channel_run${run}.txt
cat dti_results.txt >> ${DATADIR}/bbc/allvtk_channel_run${run}.txt
fi
done
done
