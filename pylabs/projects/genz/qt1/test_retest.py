# 1st attempt at qt1 test retest cross validation
#####====== part 1 =========
# 1. run freesurf on all to get b1map phase. done
# 2. reg with ants all spgr and b1map for both sessions and between sessions (use fa 05 as ref)
# 3. fit both sessions both subjects qt1 with fitT1WholeBrain() using whole head mask with vial
# 4. cross validation with vial fits on neck
####====== part 2 ==========
# 5. setup and convert all phantoms
# 6. extract midline slices
# 7. fit all phantoms spgr and IR/IRTSE
# 8. register all phantoms
# 9. extract all values






if not Path(os.environ.get('ANTSPATH'), 'WarpImageMultiTransform').is_file():
    raise ValueError('must have ants installed with WarpImageMultiTransform in $ANTSPATH directory.')
if not Path(os.environ.get('ANTSPATH'), 'WarpTimeSeriesImageMultiTransform').is_file():
    raise ValueError('must have ants installed with WarpTimeSeriesImageMultiTransform in $ANTSPATH directory.')
if not (Path(*Path(os.environ.get('ANTSPATH')).parts[:-2]) / 'ANTs' / 'Scripts' / 'antsRegistrationSyN.sh').is_file():
    raise ValueError('must have ants installed with antsRegistrationSyN.sh in '+str(Path(*Path(os.environ.get('ANTSPATH')).parts[:-2]) / 'ANTs' / 'Scripts')+'or $ANTSPATH directory.')
elif not (Path(os.environ.get('ANTSPATH')) / 'antsRegistrationSyN.sh').is_file():
    raise ValueError('must have ants installed with antsRegistrationSyN.sh in $ANTSPATH directory.')
else:
    antsRegistrationSyN = Path(*Path(os.environ.get('ANTSPATH')).parts[:-2]) / 'ANTs' / 'Scripts' / 'antsRegistrationSyN.sh'
