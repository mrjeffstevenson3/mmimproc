#!/usr/bin/env bash
#this script reads a list of vtk files produced by reg_atlas_MNI2dwi.py and generates results files
#processing flag: 0=no channel, floor, or target, just vtk stats for whole fiber bundle;
#   1=channel only; 2=base only ; 3= vtk target only; 4=base and target together; 5=all - channel, base, target
proc_method=1
run=7
#set search sub-strings to identify vtk files
sub70=IFOF-45
sub158=IFOF-133x
subcc=mori_CC
sub35=PostIntCap-35
sub123=PostIntCap-123
sub43=SLF-43
sub131=SLF-131
cd ${DATADIR}/bbc
#list=`python -c "from pylabs.projects.bbc.pairing import dwipairing; \
#    print(' '.join(['sub-bbc{sid}'.format(sid=str(s)) for s, ses, m, r in dwipairing]))"`
#list='sub-bbc108 sub-bbc211 sub-bbc231 sub-bbc241 sub-bbc243 sub-bbc249 sub-bbc253'
list=sub-bbc253



for afolder in ${list}
do
echo working on ${afolder}
#get vtk files to process
cd ${DATADIR}/bbc/${afolder}/*/*/cuda_repol_std2_S0mf3_v5/UKF
#rm -f *_channel*
#list2=`ls *mori*Left_SLF*[^_channel]_UKF.vtk`
list2=sub-bbc253_ses-1_dti_15dir_b1000_1_withmf3S0_ec_thr1_mori_Left_IFOF-45-47_UKF.vtk

#loop over vtk files
for afile in ${list2}
do
echo working on ${afile}
FILESIZE=$(stat -c%s "$afile")
echo $FILESIZE > filesize.txt
rm -f base.vtk aal_motor.vtk channel.vtk fnew.vtk fnew1.vtk f.vtk usechannel.txt proc_method.txt
echo "1" > usechannel.txt
echo "1" > procmethod.txt
cp filesize.txt /mnt/users/js/bbc/sub-bbc253/ses-1/stats_in_subj_space/toddtest
cp usechannel.txt /mnt/users/js/bbc/sub-bbc253/ses-1/stats_in_subj_space/toddtest
cp procmethod.txt /mnt/users/js/bbc/sub-bbc253/ses-1/stats_in_subj_space/toddtest


if [[ "$afile" == *"$sub70"* ]]; then
cd /mnt/users/js/bbc/sub-bbc253/ses-1/stats_in_subj_space/toddtest
fslhd -x stats > S0_hdr.txt

grep sto_ijk S0_hdr.txt > z.txt
xoffset=`cat z.txt | awk '{ print $7 }'`
yoffset=`cat z.txt | awk '{ print $11 }'`
zoffset=`cat z.txt | awk '{ print $15 }'`
echo $xoffset $yoffset $zoffset > offsets.txt
rm stats1*
cp foster_FA_CTOPPrnCS_tpos_cluster_index_cthr10_regtempl2dwi.nii stats1.nii.gz
fslchfiletype ANALYZE stats1

cp ${DATADIR}/bbc/${afolder}/*/*/cuda_repol_std2_S0mf3_v5/UKF/${afile} f.vtk
cp /mnt/users/js/bbc/holdaal/base.vtk .
cp /mnt/users/js/bbc/holdaal/aal_motor.vtk .
cp ${DATADIR}/bbc/${afolder}/*/*/cuda_repol_std2_S0mf3_v5/UKF/*JHU*Left_SLF-15_model.vtk channel.vtk
${PYLABS}/pylabs/diffusion/writefiber_withpaint_with_multiplestats_may09_2017_ad
cp fnew.vtk ${afile/.vtk/_stats_ad.vtk}

fi

if [[ "$afile" == *"$sub158"* ]]; then
cp /mnt/users/js/bbc/holdaal/base.vtk .
cp /mnt/users/js/bbc/holdaal/aal_motor.vtk .
cp *JHU*Right_IFOF-12_model.vtk channel.vtkfi
fi
#special case for corpus callosum
if [[ "$afile" == *"$subcc"* ]]; then
cp /mnt/users/js/bbc/holdaal/base.vtk .
cp /mnt/users/js/bbc/holdaal/aal_motor.vtk .
     rm -f fnew.vtk
    echo "1" > usechannel.txt
    cp *JHU*Forceps_Major-9_model.vtk channel.vtk
fi
if [[ "$afile" == *"$sub35"* ]]; then
cp /mnt/users/js/bbc/holdaal/base.vtk .
cp /mnt/users/js/bbc/holdaal/aal_motor.vtk .
cp *JHU*Left_CSP-3_model.vtk channel.vtk
fi
if [[ "$afile" == *"$sub123"* ]]; then
cp /mnt/users/js/bbc/holdaal/base.vtk .
cp /mnt/users/js/bbc/holdaal/aal_motor.vtk .
cp *JHU*Right_CSP-4_model.vtk channel.vtk
fi
if [[ "$afile" == *"$sub43"* ]]; then
cd /mnt/users/js/bbc/sub-bbc253/ses-1/stats_in_subj_space/toddtest
fslhd -x stats > S0_hdr.txt

grep sto_ijk S0_hdr.txt > z.txt
xoffset=`cat z.txt | awk '{ print $7 }'`
yoffset=`cat z.txt | awk '{ print $11 }'`
zoffset=`cat z.txt | awk '{ print $15 }'`
echo $xoffset $yoffset $zoffset > offsets.txt
rm stats1*
cp stats.nii.gz stats1.nii.gz
fslchfiletype ANALYZE stats1

cp ${DATADIR}/bbc/${afolder}/*/*/cuda_repol_std2_S0mf3_v5/UKF/${afile} f.vtk
cp /mnt/users/js/bbc/holdaal/base.vtk .
cp /mnt/users/js/bbc/holdaal/aal_motor.vtk .
cp ${DATADIR}/bbc/${afolder}/*/*/cuda_repol_std2_S0mf3_v5/UKF/*JHU*Left_SLF-15_model.vtk channel.vtk
${PYLABS}/pylabs/diffusion/writefiber_withpaint_with_multiplestats_may09_2017_ad
cp fnew.vtk ${afile/.vtk/_stats_ad.vtk}
${PYLABS}/pylabs/diffusion/writefiber_withpaint_with_multiplestats_may09_2017_gm
cp fnew.vtk ${afile/.vtk/_stats_gm.vtk}
${PYLABS}/pylabs/diffusion/writefiber_withpaint_with_multiplestats_may09_2017_wm
cp fnew.vtk ${afile/.vtk/_stats_wm.vtk}
${PYLABS}/pylabs/diffusion/writefiber_withpaint_with_multiplestats_may09_2017_md
cp fnew.vtk ${afile/.vtk/_stats_md.vtk}
${PYLABS}/pylabs/diffusion/writefiber_withpaint_with_multiplestats_may09_2017_ct
cp fnew.vtk ${afile/.vtk/_stats_ct.vtk}
fi
if [[ "$afile" == *"$sub131"* ]]; then
cp /mnt/users/js/bbc/holdaal/base.vtk .
cp /mnt/users/js/bbc/holdaal/aal_motor.vtk .
cp *JHU*Right_SLF-16_model.vtk channel.vtk
fi
done
done

