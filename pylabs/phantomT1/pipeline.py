from nipype.interfaces import fsl
from pylabs.regional import statsByRegion

vialAtlas = fsl.Info.standard_image('MNI152_T1_1mm_brain.nii.gz')

# find phantom raw files
# process raw files
    # coregister to atlas file

# get region/vial-wise data for each timepoint
vialTimeseries = numpy.zeros(ntimepoints, nvials)
for t, phantom in enumerate(scanTimeseries):
    regionalStats = statsByRegion(phantom, vialAtlas)
    vialTimeseries[t, :] = regionalStats['average'])

# plot development over time for each vial
