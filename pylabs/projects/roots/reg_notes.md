* ANTS Templating happens when all subj T1s are acquired
    * uses ```buildtemplateparallel.sh``` or condor version
    * set flags: -c 2 -j 20 -n 0 -r 1    # no -z unless adult subj moving to MNI template directly
    * -c 2 = local multithreading -j 20 = 20 cpus for  multithreading
    * will set up condor version once cluster working
    * q: can we make template to fit MEG dipoles from ANTS template using make_spheres?
    
* Use ```antsRegistrationSyN.sh``` (with nearest neighbor interpolation) for multimodal to T1 reg
* convert affines from .mat to .txt with ConvertTransformFile * Use template warps & xforms to go from T1 to template
* do stats at template level
* Use ```antsRegistrationSyN.sh``` to go from template to MNI space for atlasing
* move stats to MNI to get atlasing and higher spacial results

### Registration pipeline
1. ```antsRegistrationSyN.sh``` for all multi-modal data to viable T1
    1. MEG dipole to subj spheres?
    2. only one xform for each modality needed if acquired in same session.
    3. use ```WarpImageMultiTransform``` for rest of images
    4. freesurfer run at this level. generates *aparc_aseg*
2. ```buildtemplateparallel.sh``` when all T1s aquired to make template.
3. move all modalities to template space using ```WarpImageMultiTransform``` and warp files from templating in 2.
4. do stats at template level
5. ```antsRegistrationSyN.sh``` to move template into MNI
6. move significant stats to MNI using ```WarpImageMultiTransform``` and warp files from 5
7. atlasing, tables, and higher level spacial mmpa 

