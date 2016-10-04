#!/usr/bin/env bash
set -x
meth=("" -w)
#tens=(_eddy_corrected.nii _ec_den4_dipy.nii _ec_den8_dipy.nii _eddy_corrected_restore_tensor_den8.nii _eddy_corrected_restore_tensor.nii)
tens=(_eddy_corrected.nii  _ec_restore_tensor.nii)
rfn=/media/DiskArray/shared_data/js/bbc/sub-bbc116/ses-1/dwi/sub-bbc116_ses-1_dti_15dir_b1000_1
bvals=${rfn}.bvals
bvecs=${rfn}_eddy_corrected.eddy_rotated_bvecs
brm=${rfn}_S0_brain_mask.nii
mas=(${rfn}_S0_brain-maskCC.nii.gz ${rfn}_S0_brain-maskCO.nii.gz ${rfn}_S0_brain-maskSL.nii.gz)
S0=${rfn}_S0.nii
rm -f ${rfn:0: -34}tensor_stats.txt ${rfn:0: -34}tmpresult.txt ${rfn:0: -34}tmpstat.txt
touch ${rfn:0: -34}tensor_stats.txt
for d in "${tens[@]}"; do
    for m in "${meth[@]}"; do
        if [[ ${d} == '_eddy_corrected.nii' ]] ||  [[ ${d} == '_ec_den4_dipy.nii' ]] || [[ ${d} == '_ec_den8_dipy.nii' ]]; then
            dtifit -k ${rfn}${d} -o ${rfn}${d:0: -4}`if [[ "${m}" == '-w' ]]; then echo _wls; else echo _ols; fi` \
                -m $brm -r $bvecs -b $bvals $m --save_tensor --sse
            dtigen -t ${rfn}${d:0: -4}`if [[ "${m}" == '-w' ]];  then echo _wls; else echo _ols; fi`_tensor \
                -o ${rfn}${d:0: -4}`if [[ "${m}" == '-w' ]];  then echo _wls; else echo _ols; fi`_dtigen \
                -b $bvals -r $bvecs -m $brm --s0=${S0}
            fslmaths ${rfn}${d:0: -4}`if [[ "${m}" == '-w' ]];  then echo _wls; else echo _ols; fi`_dtigen -thr 5 -uthr 10000 \
                -sub ${rfn}${d} ${rfn}${d:0: -4}`if [[ "${m}" == '-w' ]];  then echo _wls; else echo _ols; fi`_dtigen_sub${d:0: -4}
        elif [[ ${m} == '-w' ]]; then
            dtigen -t ${rfn}${d:0: -4} -o ${rfn}${d:0: -4}_dtigen -b $bvals -r $bvecs -m $brm --s0=${S0}
            if [[ ${d} == '_ec_restore_tensor.nii' ]];  then
                fslmaths ${rfn}${d:0: -4}_dtigen -thr 5 -uthr 10000 -sub ${rfn}_eddy_corrected.nii ${rfn}${d:0: -4}_dtigen_sub_eddy_corrected
            else
                fslmaths ${rfn}${d:0: -4}_dtigen -thr 5 -uthr 10000 -sub ${rfn}_ec_den8_dipy.nii ${rfn}${d:0: -4}_dtigen_sub_ec_den8_dipy
            fi
        fi
        for s in "${mas[@]}"; do
            if [[ ${d} == '_eddy_corrected.nii' ]] ||  [[ ${d} == '_ec_den4_dipy.nii' ]] || [[ ${d} == '_ec_den8_dipy.nii' ]];  then
                echo ${d:0: -4}`if [[ "${m}" == '-w' ]];  then echo _wls; else echo _ols; fi`_dtigen_sub${d:0: -4}_${s: -9: -7} \
                    > ${rfn:0: -34}tmpstat.txt
                ls -l $s
                fslstats -t ${rfn}${d:0: -4}`if [[ "${m}" == '-w' ]];  then echo _wls; else echo _ols; fi`_dtigen_sub${d:0: -4} \
                    -k $s -M >> ${rfn:0: -34}tmpstat.txt
            elif [[ ${d} == '_ec_restore_tensor.nii' ]] && [[ ${m} == '-w' ]];  then
                echo ${d:0: -4}_dtigen_sub_eddy_corrected_${s: -9: -7} > ${rfn:0: -34}tmpstat.txt
                fslstats -t ${rfn}${d:0: -4}_dtigen_sub_eddy_corrected -k $s -M >> ${rfn:0: -34}tmpstat.txt
            elif [[ ${d} == '_eddy_corrected_restore_tensor_den8.nii' ]] && [[ ${m} == '-w' ]];  then
                echo ${d:0: -4}_dtigen_sub_ec_den8_dipy_${s: -9: -7} > ${rfn:0: -34}tmpstat.txt
                fslstats -t ${rfn}${d:0: -4}_dtigen_sub_ec_den8_dipy -k $s -M >> ${rfn:0: -34}tmpstat.txt
            fi
            cat ${rfn:0: -34}tmpstat.txt
            paste ${rfn:0: -34}tensor_stats.txt ${rfn:0: -34}tmpstat.txt > ${rfn:0: -34}tmpresult.txt
            mv ${rfn:0: -34}tmpresult.txt ${rfn:0: -34}tensor_stats.txt
            echo finished $d $m $s
        done
    done
done
rm -f ${rfn:0: -34}tmpresult.txt ${rfn:0: -34}tmpstat.txt
