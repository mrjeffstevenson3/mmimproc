for afile in GM_mod_merg_s2.nii.gz WM_mod_merg_s2.nii.gz; 
    do mkdir -p behav_results500_${afile:0:2}_v1; 
    for behav in SOPT41corr*.mat; 
        do randomise_parallel -i ${afile} \
            -o ./behav_results500_${afile:0:2}_v1/out_n500_test20 \
            -m ${afile:0:2}_mask -d ${behav} -t scs_design2col.con \
            -n 500 -T -V; 
    done; 
done
