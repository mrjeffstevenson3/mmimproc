import nibabel
import numpy


def withVoxelsOverThresholdOf(threshold):
    def inner(filepath):
        img = nibabel.load(filepath)
        data = img.get_data()
        return numpy.any(data > threshold)
    return inner

def select(files, criterium):
    return [f for f in files if criterium(f)]

