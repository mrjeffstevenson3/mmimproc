#!/usr/bin/env bash
#this script reads a list of vtk files produced by reg_atlas_MNI2dwi.py and generates results files
#processing flag: 0=no channel, floor, or target, just vtk stats for whole fiber bundle;
#   1=channel only; 2=base only ; 3= vtk target only; 4=base and target together; 5=all - channel, base, target
proc_method=1
run=7
#set search sub-strings to identify vtk files
sub70=IFOF-45
sub158=IFOF-133
subcc=mori_CC
sub35=PostIntCap-35
sub123=PostIntCap-123
sub43=Left_SLF-43
sub131=Right_SLF-131
#get bbc subject directories
cd ${DATADIR}/bbc
#list=`python -c "from pylabs.projects.bbc.pairing import dwipairing; \
#    print(' '.join(['sub-bbc{sid}'.format(sid=str(s)) for s, ses, m, r in dwipairing]))"`
#list='sub-bbc108 sub-bbc211 sub-bbc231 sub-bbc241 sub-bbc243 sub-bbc249 sub-bbc253'
list=sub-bbc253
#list=`ls -d sub-bbc*`
#rm -f ${DATADIR}/bbc/allvtk_channel_run${run}.txt
#loop over subject dirs
for afolder in ${list}
do
echo working on ${afolder}
#get vtk files to process
cd ${DATADIR}/bbc/${afolder}/*/*/cuda_repol_std2_S0mf3_v5/UKF
#rm -f *_channel*
list2=`ls *mori*IFOF*[^_channel]_UKF.vtk *mori*SLF*[^_channel]_UKF.vtk`
#list2=sub-bbc253_ses-1_dti_15dir_b1000_1_withmf3S0_ec_thr1_mori_Left_IFOF-45-47_UKF.vtk

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
cp /mnt/users/js/bbc/holdaal/base.vtk .
cp /mnt/users/js/bbc/holdaal/aal_motor.vtk .
cp *JHU*Left_IFOF-11_model.vtk channel.vtk
${PYLABS}/pylabs/diffusion/readfiber_withchannel_ukf_fa1_injection_apdivisions_ifof
${PYLABS}/pylabs/diffusion/makecsv_fromvtk_ukf
cp fnew.vtk ${afile/.vtk/_channel.vtk}
echo -n "${afile} " >> ${DATADIR}/bbc/allukf_channel_run${run}.txt
cat ukf_10regions.csv >> ${DATADIR}/bbc/allukf_channel_run${run}.txt
cp ukf_10regions.csv ukf_10regions_${afile}.csv

fi
if [[ "$afile" == *"$sub158"* ]]; then
cp /mnt/users/js/bbc/holdaal/base.vtk .
cp /mnt/users/js/bbc/holdaal/aal_motor.vtk .
cp *JHU*Right_IFOF-12_model.vtk channel.vtk
${PYLABS}/pylabs/diffusion/readfiber_withchannel_ukf_fa1_injection_apdivisions_ifof
${PYLABS}/pylabs/diffusion/makecsv_fromvtk_ukf
cp fnew.vtk ${afile/.vtk/_channel.vtk}
echo -n "${afile} " >> ${DATADIR}/bbc/allukf_channel_run${run}.txt
cat ukf_10regions.csv >> ${DATADIR}/bbc/allukf_channel_run${run}.txt
cp ukf_10regions.csv ukf_10regions_${afile}.csv
fi
#special case for corpus callosum
if [[ "$afile" == *"$subcc"* ]]; then
cp /mnt/users/js/bbc/holdaal/base.vtk .
cp /mnt/users/js/bbc/holdaal/aal_motor.vtk .
     rm -f fnew.vtk
    echo "1" > usechannel.txt
    cp *JHU*Forceps_Major-9_model.vtk channel.vtk
    ${PYLABS}/pylabs/diffusion/readfiber_withchannel_ukf_fa1_injection_apdivisions
    ${PYLABS}/pylabs/diffusion/makecsv_fromvtk_ukf
    cp fnew.vtk ${afile/.vtk/_Forceps_Major_channel.vtk}
echo -n "${afile} Forceps_Major" >> ${DATADIR}/bbc/allukf_channel_run${run}.txt
cat ukf_10regions.csv >> ${DATADIR}/bbc/allukf_channel_run${run}.txt
cp ukf_10regions.csv ukf_10regions_${afile}_Forceps_Major.csv

    echo -n "${afile/.vtk/_Forceps_Major_channel.vtk} " >> ${DATADIR}/bbc/allvtk_channel_run${run}.txt
    cat dti_results.txt >> ${DATADIR}/bbc/allvtk_channel_run${run}.txt
    rm -f fnew.vtk
    cp *JHU*Forceps_Minor-10_model.vtk channel.vtk
    ${PYLABS}/pylabs/diffusion/readfiber_withchannel_ukf_fa1_injection_apdivisions
    ${PYLABS}/pylabs/diffusion/makecsv_fromvtk_ukf
    cp fnew.vtk ${afile/.vtk/_Forceps_Minor_channel.vtk}
echo -n "${afile} Forceps_Minor" >> ${DATADIR}/bbc/allukf_channel_run${run}.txt
cat ukf_10regions.csv >> ${DATADIR}/bbc/allukf_channel_run${run}.txt
cp ukf_10regions.csv ukf_10regions_${afile}_Forceps_Minor.csv
     echo -n "${afile/.vtk/_Forceps_Minor_channel.vtk} " >> ${DATADIR}/bbc/allvtk_channel_run${run}.txt
    cat dti_results.txt >> ${DATADIR}/bbc/allvtk_channel_run${run}.txt
    rm -f fnew.vtk
fi
if [[ "$afile" == *"$sub35"* ]]; then
cp /mnt/users/js/bbc/holdaal/base.vtk .
cp /mnt/users/js/bbc/holdaal/aal_motor.vtk .
cp *JHU*Left_CSP-3_model.vtk channel.vtk
${PYLABS}/pylabs/diffusion/readfiber_withchannel_ukf_fa1_injection_sidivisions
${PYLABS}/pylabs/diffusion/makecsv_fromvtk_ukf
cp fnew.vtk ${afile/.vtk/_channel.vtk}
echo -n "${afile} " >> ${DATADIR}/bbc/allukf_channel_run${run}.txt
cat ukf_10regions.csv >> ${DATADIR}/bbc/allukf_channel_run${run}.txt
cp ukf_10regions.csv ukf_10regions_${afile}.csv
fi
if [[ "$afile" == *"$sub123"* ]]; then
cp /mnt/users/js/bbc/holdaal/base.vtk .
cp /mnt/users/js/bbc/holdaal/aal_motor.vtk .
cp *JHU*Right_CSP-4_model.vtk channel.vtk
${PYLABS}/pylabs/diffusion/readfiber_withchannel_ukf_fa1_injection_sidivisions
${PYLABS}/pylabs/diffusion/makecsv_fromvtk_ukf
cp fnew.vtk ${afile/.vtk/_channel.vtk}
echo -n "${afile} " >> ${DATADIR}/bbc/allukf_channel_run${run}.txt
cat ukf_10regions.csv >> ${DATADIR}/bbc/allukf_channel_run${run}.txt
cp ukf_10regions.csv ukf_10regions_${afile}.csv
fi
if [[ "$afile" == *"$sub43"* ]]; then
cp /mnt/users/js/bbc/holdaal/base.vtk .
cp /mnt/users/js/bbc/holdaal/aal_motor.vtk .
cp *JHU*Left_SLF-15_model.vtk channel.vtk
${PYLABS}/pylabs/diffusion/readfiber_withchannel_ukf_fa1_injection_slf_left
${PYLABS}/pylabs/diffusion/makecsv_fromvtk_ukf_slf
cp fnew.vtk ${afile/.vtk/_channel.vtk}
echo -n "${afile} " >> ${DATADIR}/bbc/allukf_channel_run${run}.txt
cat ukf_10regions.csv >> ${DATADIR}/bbc/allukf_channel_run${run}.txt
cp ukf_10regions.csv ukf_10regions_${afile}.csv
fi
if [[ "$afile" == *"$sub131"* ]]; then
cp /mnt/users/js/bbc/holdaal/base.vtk .
cp /mnt/users/js/bbc/holdaal/aal_motor.vtk .
cp *JHU*Right_SLF-16_model.vtk channel.vtk
${PYLABS}/pylabs/diffusion/readfiber_withchannel_ukf_fa1_injection_slf_right
${PYLABS}/pylabs/diffusion/makecsv_fromvtk_ukf_slf
cp fnew.vtk ${afile/.vtk/_channel.vtk}
echo -n "${afile} " >> ${DATADIR}/bbc/allukf_channel_run${run}.txt
cat ukf_10regions.csv >> ${DATADIR}/bbc/allukf_channel_run${run}.txt
cp ukf_10regions.csv ukf_10regions_${afile}.csv
fi
done
done
