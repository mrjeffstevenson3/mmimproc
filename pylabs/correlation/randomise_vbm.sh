for afile in GM_mod_merg_s2.nii.gz WM_mod_merg_s2.nii.gz; 
    do mkdir -p behav_results500_${afile:0:2}_v1; 
    for behav in SOPT41corr*.mat; 
        do randomise_parallel -i ${afile} \
            -o ./behav_results500_${afile:0:2}_v1/out_n500_test20 \
            -m ${afile:0:2}_mask -d ${behav} -t scs_design2col.con \
            -n 500 -T -V; 
    done; 
done



#for afile in `imglob GM_mod_merg*`; 
#    do mkdir -p behav_results5000_${afile:0:2}_${afile:12:2}; 
#    for behav in `ls spa??c3_de_dti.mat`; 
#        do randomise_parallel -i ${afile} \
#            -o ./behav_results5000_${afile:0:2}_${afile:12:2}/out_${afile:0:2}_vbm${afile:12:2}_3col_gend_cov_${behav:0:7} \
#            -m ${afile:0:2}_mask -d ${behav} -t spalccs_design3col.con \
#            -n 5000 -T -V; 
#    done; 
#done
