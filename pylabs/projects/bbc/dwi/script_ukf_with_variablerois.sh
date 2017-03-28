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
list2=`ls *withmf3S0_ec_thr1_mori_Left_SLF-43-81-83_UKF.vtk`


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
    cp ../../vtk_tensor_comp_run${run}/*aal_motor*.vtk base.vtk
    cp ../../vtk_tensor_comp_run${run}/*aal_motor*.vtk aal_motor.vtk
    echo "0" > usechannel.txt
    ${PYLABS}/pylabs/diffusion/readfiber_corpus_callosum_with_ceiling
    echo -n "${afile/.vtk/_nochannel.vtk} " >> ${DATADIR}/bbc/allvtk_channel_run${run}.txt
    cat dti_results.txt >> ${DATADIR}/bbc/allvtk_channel_run${run}.txt
    cp fnew.vtk ${afile/.vtk/_nochannel.vtk}
    ${PYLABS}/pylabs/diffusion/makevolumetric_fromvtk
    echo -n "${afile/.vtk/_channel.vtk} " >> ${DATADIR}/bbc/allvtk_channel_run${run}.txt
    cat dti_results.txt >> ${DATADIR}/bbc/allvtk_channel_run${run}.txt
    rm -f fnew.vtk
    echo "1" > usechannel.txt
    cp *JHU*Forceps_Major-9.vtk channel.vtk
    ${PYLABS}/pylabs/diffusion/readfiber_withchannel_ukf_fa1_injection_apdivisions
    ${PYLABS}/pylabs/diffusion/makecsv_fromvtk_ukf
    cp fnew.vtk ${afile/.vtk/_Forceps_Major_channel.vtk}
echo -n "${afile} " >> ${DATADIR}/bbc/allukf_channel_run${run}.txt
cat ukf_10regions.csv >> ${DATADIR}/bbc/allukf_channel_run${run}.txt

    echo -n "${afile/.vtk/_Forceps_Major_channel.vtk} " >> ${DATADIR}/bbc/allvtk_channel_run${run}.txt
    cat dti_results.txt >> ${DATADIR}/bbc/allvtk_channel_run${run}.txt
    rm -f fnew.vtk
    cp *JHU*Forceps_Minor-10.vtk channel.vtk
    ${PYLABS}/pylabs/diffusion/readfiber_withchannel_ukf_fa1_injection_apdivisions
    ${PYLABS}/pylabs/diffusion/makecsv_fromvtk_ukf
    cp fnew.vtk ${afile/.vtk/_Forceps_Minor_channel.vtk}
echo -n "${afile} " >> ${DATADIR}/bbc/allukf_channel_run${run}.txt
cat ukf_10regions.csv >> ${DATADIR}/bbc/allukf_channel_run${run}.txt

     echo -n "${afile/.vtk/_Forceps_Minor_channel.vtk} " >> ${DATADIR}/bbc/allvtk_channel_run${run}.txt
    cat dti_results.txt >> ${DATADIR}/bbc/allvtk_channel_run${run}.txt
    rm -f fnew.vtk
fi
if [[ "$afile" == *"$sub35"* ]]; then
cp ../../vtk_tensor_comp_run${run}/*base*.vtk base.vtk
cp ../../vtk_tensor_comp_run${run}/*aal_motor*.vtk aal_motor.vtk
cp *JHU*Left_CSP-3.vtk channel.vtk
${PYLABS}/pylabs/diffusion/readfiber_withchannel_ukf_fa1_injection_sidivisions
${PYLABS}/pylabs/diffusion/makecsv_fromvtk_ukf
cp fnew.vtk ${afile/.vtk/_channel.vtk}
echo -n "${afile} " >> ${DATADIR}/bbc/allukf_channel_run${run}.txt
cat ukf_10regions.csv >> ${DATADIR}/bbc/allukf_channel_run${run}.txt
fi
if [[ "$afile" == *"$sub123"* ]]; then
cp ../../vtk_tensor_comp_run${run}/*base*.vtk base.vtk
cp ../../vtk_tensor_comp_run${run}/*aal_motor*.vtk aal_motor.vtk
cp *JHU*Right_CSP-4.vtk channel.vtk
${PYLABS}/pylabs/diffusion/readfiber_withchannel_ukf_fa1_injection_sidivisions
${PYLABS}/pylabs/diffusion/makecsv_fromvtk_ukf
cp fnew.vtk ${afile/.vtk/_channel.vtk}
echo -n "${afile} " >> ${DATADIR}/bbc/allukf_channel_run${run}.txt
cat ukf_10regions.csv >> ${DATADIR}/bbc/allukf_channel_run${run}.txt
fi
if [[ "$afile" == *"$sub43"* ]]; then
cp ../../vtk_tensor_comp_run${run}/*Left_STG-MTG-18-20*.vtk base.vtk
cp ../../vtk_tensor_comp_run${run}/*Left_pre-postCentGyr-6-7*.vtk aal_motor.vtk
cp *JHU*LEFT_SLF-16.vtk channel.vtk
${PYLABS}/pylabs/diffusion/readfiber_withchannel_ukf_fa1_injection_apdivisions
${PYLABS}/pylabs/diffusion/makecsv_fromvtk_ukf
cp fnew.vtk ${afile/.vtk/_channel.vtk}
echo -n "${afile} " >> ${DATADIR}/bbc/allukf_channel_run${run}.txt
cat ukf_10regions.csv >> ${DATADIR}/bbc/allukf_channel_run${run}.txt
fi
if [[ "$afile" == *"$sub131"* ]]; then
cp ../../vtk_tensor_comp_run${run}/*Right_STG-MTG-106-108*.vtk base.vtk
cp ../../vtk_tensor_comp_run${run}/*Right_pre-postCentGyr-94-95*.vtk aal_motor.vtk
cp *JHU*Right_SLF-16.vtk channel.vtk
${PYLABS}/pylabs/diffusion/readfiber_withchannel_ukf_fa1_injection_apdivisions
${PYLABS}/pylabs/diffusion/makecsv_fromvtk_ukf
cp fnew.vtk ${afile/.vtk/_channel.vtk}
echo -n "${afile} " >> ${DATADIR}/bbc/allukf_channel_run${run}.txt
cat ukf_10regions.csv >> ${DATADIR}/bbc/allukf_channel_run${run}.txt
fi
done
done
