**bbc pipeline notes**

**For VBM:**
1. Add file name glob wildcards to bbc_conv dict in conversion/brain_convert.py
2. convert PAR/REC using bbc/mr_preprocess.py
3. do brain extraction with bbc_bet.sh and QC
4. center QC'd brains with utils/niftidict.py (should move bulk to mr_preprocess.py)
5. buildtemplateparallel.sh -d 3 -c 2 -j 18 -r 1 -s CC -t GR -m 30x50x20 -n 0 -i 4 -o <outfile path/prepend> *.nii.gz
6. save qform header info and convert to analyse
7. run spm segment in batch mode
8. prepare design.con design.mat and design.grp (exchangeability blocks)
9. heal headers, convert to nifti, calc Jacobians, smooth and randomise with pylabs/projects/bbc/vbm_post_seg.sh

**For DTI**
1. Add file name glob wildcard to bbc_conv dict in conversion/brain_convert.py
2. convert PAR/REC using bbc/mr_preprocess.py (as above)
3. do brain extraction with bbc/dti_bet.sh
4. run QC with diffusion/dti_qc.py
to do:
5. need to build update to niftiDict function to add field 'QC': True
6. build query niftiDict function to get status of any variable and return values
7. build eddy current with subprocess and parallel
