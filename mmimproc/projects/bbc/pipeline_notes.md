**bbc pipeline notes**

**For VBM:**
1. Add file name glob wildcards to bbc_conv dict in conversion/brain_convert.py
2. convert PAR/REC using bbc/mr_preprocess.py
3. do brain extraction with bbc_bet.sh and QC <-- convert to python
4. center QC'd brains with utils/niftidict.py (should move bulk to mr_preprocess.py)
5. buildtemplateparallel.sh -d 3 -c 2 -j 18 -r 1 -s CC -t GR -m 30x50x20 -n 0 -i 4 -o <outfile path/prepend> *.nii.gz
6. save qform header info and convert to analyse
7. run spm segment in batch mode
8. prepare design.con design.mat and design.grp (exchangeability blocks)
9. heal headers, convert to nifti, calc Jacobians, smooth and randomise with mmimproc/projects/bbc/vbm_post_seg.sh
10. run FDR with clustering using group_correl_p2.py note masking problem with GM outside brain.


**For DTI**
1. Add file name glob wildcard to bbc_conv dict in conversion/brain_convert.py
2. convert PAR/REC using bbc/mr_preprocess.py (as above)
3. now in eddy.py: do brain extraction with bbc/dti_bet.sh <- make into python
4. run QC with diffusion/dti_qc.py    <-- make reporting summary script
5. run eddy.py cuda eddy current correction (includes filter S0, test eddy with S0 replaced with reg2templ_3DT2)
6. run bbc_dti_fit.py dti fit methods OLS, WLS, Restore, and UKF
7. dti reg module that generates warp and affines using reg_direct_dwi2template
8. apply inverse warps to mori atlas and generate VTKs for dti deathmatch
8. apply forward warps and affines moving to template space
9. filter and extract tensor from dipy and reg to template and atlases
still to do:
10. generate mat files
11. run paired randomise runs on all dti measures
todo - rethink items 5 and 6:
5. need to build function to update niftiDict and google spreadsheet to add field 'QC': True
6. build query niftiDict function to get status of any variable and return values

**for MEG**
1. make affine xform path from vbm whole head subj to template space
2. Manual rotate/allign to polhemus using freeview saving xfm file (and test)

**Forward path subj dti thru template to MNI:**
path in space:
FA-->warp/affine to T1 comroll-->warp/afffine to template T1-->warp/affine to MNI/atlas
ref=MNI 1mm or 2mm
Warp matrix execution order is:
T1 template->MNI Warp, T1 template->MNI Affine, T1com->T1 template Warp, T1com->T1 template affine, FA->T1com Warp, FA->T1com affine

**Reverse path MNI to subject dti used for atlas/ROI:**
path in space:
MNI/atlas-->Inverse warp/affine to template T1-->Inverse warp/affine to comroll T1-->Inverse warp/affine to subject FA/dwi
ref=FA
Warp matrix execution order is:
-i FA->T1com affine, FA->T1com Warp, -i T1com->T1 template affine, T1com->T1 template Warp, -i T1 template->MNI Affine, T1 template->MNI Warp

**Forward path subj dti to template**
path in space:
FA-->warp/affine to T1 comroll-->warp/afffine to template T1
ref=template
Warp matrix execution order is:
T1com->T1 template Warp, T1com->T1 template affine, FA->T1com Warp, FA->T1com affine

**class objects needed:**
conversion object with defaults for each modality.
    set up project specific tech info variables
    saves/stores found/converted objects
brain extraction and masking with defaults
    must be able to preserve overrides for -f 0.3 defaults
    store object on niprov?
VBM templating as prelim to reg
Reg class to capture all templating files and pathways to/from all modalities