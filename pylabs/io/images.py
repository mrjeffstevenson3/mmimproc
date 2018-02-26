import pylabs
import nibabel, numpy
from pylabs.utils import run_subprocess, replacesuffix, ProvenanceWrapper
from pathlib import *
import shutil, gzip
#set up provenance
prov = ProvenanceWrapper()

def loadStack(files):
    data = []
    shapes = []
    affines = []
    for f, fpath in enumerate(files):
        print('Loading image {} of {}..'.format(f+1, len(files)))
        img = nibabel.load(str(fpath))
        sdata = img.get_data()
        data.append(sdata)
        shapes.append(sdata.shape)
        affines.append(img.affine)
    print('Concatenating data..')
    data = numpy.array(data)
    for shape, aff in zip(shapes, affines):
        # ensure images have same dimensions and qforms
        numpy.testing.assert_almost_equal(shapes[0], shape, 3, err_msg='resolutions do not match. array shapes must be the same.')
        numpy.testing.assert_almost_equal(affines[0], aff, 3, err_msg='affines do not match. images may be in different spaces.')
    return data, affines[0]

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
    numpy.testing.assert_almost_equal(affine, img.get_qform(), 3,
                                   err_msg='output qform in header does not match input qform')
    nibabel.save(img, str(outfile))
    return

def paired_sub(niifiles, outfname, minuend=0):
    if int(minuend) not in [0,1]:
        raise ValueError('minuend defines image in list to subtract other image from. must be either 0 or 1.')
    if len(niifiles) != 2:
        raise ValueError('1st arg must be list with 2 valid nifti files to subtract.')
    for f in niifiles:
        if not (Path(f)).is_file():
            raise ValueError("cannot find file "+str(f))
    data, affine = loadStack(niifiles)
    data = numpy.rollaxis(data, 0, 4)
    if minuend == 0:
        subtrahend = 1
    elif minuend == 1:
        subtrahend = 0
    print('Subtracting data..')
    sub_data = numpy.subtract(data[:,:,:,minuend],  data[:,:,:,subtrahend])
    savenii(sub_data, affine, outfname)


def gz2nii(file):
    with gzip.open(str(file), 'rb') as src, open(str(replacesuffix(file, '.nii')), 'wb') as dest:
        shutil.copyfileobj(src, dest)
