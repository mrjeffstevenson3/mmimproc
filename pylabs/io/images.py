import nibabel, numpy
from pylabs.utils import run_subprocess

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
    cmd = 'fslorient -copysform2qform ' + file
    run_subprocess(cmd)

def savenii(data, affine, outfile, header=None, minmax=('parse', 'parse'), qform_code=1):
    if header == None:
        img = nibabel.nifti1.Nifti1Image(data, affine)
    else:
        img = nibabel.nifti1.Nifti1Image(data, affine, header)
    if minmax[0] == 'parse':
        img.header['cal_min'] = data.min()
    else:
        img.header['cal_min'] = float(minmax[0])
    if minmax[1] == 'parse':
        img.header['cal_max'] = data.max()
    else:
        img.header['cal_max'] = float(minmax[1])
    img.set_qform(img.affine, code=qform_code)
    np.testing.assert_almost_equal(affine, img.get_qform(), 4,
                                   err_msg='output qform in header does not match input qform')
    nibabel.save(img, str(outfile))
