***to do:***
make all_<project>_subjects_info.h5 intermetiates hdf file with bids structure all level 1 preproc
    1. save niftdict to hdf                     name: sid/session/convertion/niftidict
    2. save gaba fits to hdf  (make df)         name: sid/session/mrs/gaba_fits
    3. save glu & other metab to hdf            name: sid/session/mrs/glutamate_plus_metabs
    4. save %CSF to hdf (make df)               name: sid/session/mrs/CSF_correction_factor
make mrs group level hdf file called <project>_mrs_group_results.h5
    1. save corrected data to hdf (done)        name: CSFcorrected_mrs_data
    2. save left side corrected data  (done)    name: left_side_glutamate_and_other_metabolites
    3. save right side corrected data  (done)   name: right_side_glutamate_and_other_metabolites
    4. save fortran stats and correlations      name: fortran/stats and /correlations and /figures
    5. save python stats and correlations       name: python/stats and /correlations and /figures
    
qT1 workflow:
    1. bet TR1 and make b1 map from mag images using calcb1map
    2. bet spgr's and reg to spgr20 (or highest fa) using ants
    3. reg b1map phase to spgr using ants 
    4. calc qT1 using non-linear exp fit
    5. calc phantom equation for that day and apply