import nibabel, numpy
import subprocess

def loadStack(files):
    data = []
    shapes = []
    for f, fpath in enumerate(files):
        print('Loading image {} of {}..'.format(f+1, len(files)))
        img = nibabel.load(fpath)
        sdata = img.get_data()
        shapes.append(sdata.shape)
        data.append(sdata)
    print('Concatenating data..')
    data = numpy.array(data)
    affine = img.get_affine()
    for shape in shapes:
        assert shape==shapes[0] # ensure images have same dimensions
    return data, affine

def combineAsVolumes(files, outfpath):
    data, affine = loadStack(files)
    data = numpy.rollaxis(data, 0, 4)
    nibabel.save(nibabel.Nifti1Image(data, affine), outfpath)

def copysform2qform(file):
    cmd = ['fslorient', '-copysform2qform', file]
    subprocess.check_call(cmd, shell=True)
