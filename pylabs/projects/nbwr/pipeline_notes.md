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