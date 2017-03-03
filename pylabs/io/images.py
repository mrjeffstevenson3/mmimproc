import nibabel, numpy
from pylabs.utils import run_subprocess
from pathlib import *

def loadStack(files):
    data = []
    shapes = []
    affines = []
    for f, fpath in enumerate(files):
        print('Loading image {} of {}..'.format(f+1, len(files)))
        img = nibabel.load(fpath)
        #sdata = img.get_data()
        data.append(img.get_data())
        shapes.append(data.shape)
        affines.append(img.affine)
        if f == 0:
            affine = img.get_affine()
    print('Concatenating data..')
    data = numpy.array(data)
    for shape, affine in zip(shapes, affines):
        # ensure images have same dimensions and qforms
        numpy.testing.assert_almost_equal(shape, shapes[0], 4,
                                    err_msg='not all shapes match first shape in file list')
        numpy.testing.assert_almost_equal(affine[:3, 3], affines[0][:3, 3], 4,
                                       err_msg='not all affines match first qform in file list'+str(affines[0]))
    return data, affine

def combineAsVolumes(files, outfpath):
    data, affine = loadStack(files)
    data = numpy.rollaxis(data, 0, 4)
    nibabel.save(nibabel.Nifti1Image(data, affine), outfpath)

def copysform2qform(file):
    cmd = 'fslorient -copysform2qform ' + file
    run_subprocess(cmd)

def copyqform2sform(file):
    cmd = 'fslorient -copyqform2sform ' + file
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
    numpy.testing.assert_almost_equal(affine, img.get_qform(), 4,
                                   err_msg='output qform in header does not match input qform')
    nibabel.save(img, str(outfile))

def paired_sub(niifiles, outfname, order=0):
    for f in niifiles:
        if not (Path(f)).is_file():
            raise ValueError("cannot find file "+str(f))

