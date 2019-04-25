dev plan 11/17/17:
level 1:

1. store all convert nifti dicts in project_converted.h5 file
    each subject has subj/ses key-groupid to referece later
2. same subj/ses/modality key-groupid used in project_registration.h5
    modalities may have multiple types of registrations/targets. ex:
    
    qT1:
        reg b1 to spgr30 - target=spgr30
            exkey: sub-nbwr431/ses-1/qt1/reg2spgr05
        reg spgr30 20 15 10 to spgr05, target = spgr05
    freesurfer:
        reg b1 to rms - target = rms
        
    dti:
        reg affine topup & topdn s0 to dti
        reg mni atlases to b0 for seed points
        
        
quest: store only dicts with info on files to use