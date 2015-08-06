import nibabel
import numpy
import os


def withVoxelsOverThresholdOf(threshold):
    def inner(filepath):
        name = os.path.basename(filepath)
        img = nibabel.load(filepath)
        data = img.get_data()
        nvoxels = numpy.sum(data > threshold)
        msg = 'Found {0: >2d} voxels over threshold in {1}'
        if nvoxels > 0:
            print(msg.format(nvoxels, name))
        return nvoxels > 0
    return inner

def select(files, criterium):
    return [f for f in files if criterium(f)]

