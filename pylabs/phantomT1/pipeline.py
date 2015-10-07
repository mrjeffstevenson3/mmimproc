from nipype.interfaces import fsl
from pylabs.regional import statsByRegion
import matplotlib.pyplot as plt

vialAtlas = fsl.Info.standard_image('MNI152_T1_1mm_brain.nii.gz')

# find phantom raw files
# process raw files
    # coregister to atlas file

# get region/vial-wise data for each timepoint
vialTimeseries = numpy.zeros(ntimepoints, nvials)
for t, phantom in enumerate(scanTimeseries):
    print('Examining scan {0} of {1}'.format(t,ntimepoints))
    regionalStats = statsByRegion(phantom, vialAtlas)
    vialTimeseries[t, :] = regionalStats['average'])

# plot development over time for each vial
plt.plot(numpy.arange(ntimepoints), vialTimeseries) 
plt.show()
