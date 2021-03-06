import mmimproc
mmimproc.datadir.target = 'jaba'
from pathlib import *
import nibabel, numpy
from mmimproc.utils import run_subprocess, replacesuffix, ProvenanceWrapper
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
        sdata = img.get_data().astype(numpy.float64)
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

def savenii(data, affine, outfile, header=None, minmax=('parse', 'parse'), qform_code=1, xyz_units=2, t_units=8):
    """
    see https://github.com/nipy/nibabel/blob/master/nibabel/nifti1.py for code explanations
    :param data: numpy array to be made into nifti image
    :param affine: affine of image
    :param outfile: output file name
    :param header: if header pre-constructed and you wish to pass this as nifti header
    :param minmax: to force default image range. eg for FA image minmax=(0,1)
    :param qform_code: see url above. usually 1=scanner, 2=registered and moved to new non-scanner space
    :param xyz_units: usually mm=2. see url above
    :param t_units: usually sec=8.
    :return:
    """
    if header is None:
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
    img.set_qform(affine, code=qform_code)
    img.set_sform(affine, code=qform_code)
    img.header.set_xyzt_units(xyz_units, t_units)
    numpy.testing.assert_almost_equal(affine, img.affine, 4,
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


def gz2nii(file, delete_gz=False):
    with gzip.open(str(file), 'rb') as src, open(str(replacesuffix(file, '.nii')), 'wb') as dest:
        shutil.copyfileobj(src, dest)
        if delete_gz:
            Path(file).unlink()

def get_ext(file):
    file = Path(file)
    if not any('.nii' in ex for ex in file.suffixes):
        raise ValueError(str(file) + ' file is not nifti with .nii or .nii.gz ext. please check')
    if len(file.suffixes) == 1 and file.suffixes[0] == '.nii':
        return '.nii'
    if len(file.suffixes) == 2 and file.suffixes[0] == '.nii' and file.suffixes[1] == '.gz':
        return '.nii.gz'
    else:
        return None