from os.path import join
import itertools, datetime
import nibabel, numpy, scipy.stats, scipy.ndimage, niprov
from pylabs.utils import progress
# import niprov
# provenance = niprov.Context()

def nancount(A):
    return numpy.count_nonzero(numpy.isnan(A))

def nonnancount(A):
    return A.size - nancount(A)

def preproc(data):
    A = numpy.copy(data)
    A[A < 0] = 0
    uthresh = 20000
    A[A > uthresh] = uthresh
    return A

def evaluate(target, subject):
    ztarget = preproc(target)
    zsubject = preproc(subject)
    diffmap = ztarget - zsubject
    return numpy.absolute(diffmap).mean()

def transform(indata, tx, ty, rxy):
    shifted = scipy.ndimage.interpolation.shift(indata, [tx, ty], order=1)
    rot = scipy.ndimage.interpolation.rotate(shifted, rxy, reshape=False, order=1)
    return rot

def align(subjectfile, targetfile, delta=5):
    target = nibabel.load(targetfile).get_data()
    subjectImg = nibabel.load(subjectfile)
    subject = subjectImg.get_data()
    stat = evaluate(target, subject)
    print('Baseline stat= {0}'.format(stat))
    d = delta # delta for transformations from center.
    verbose = False
    ranges = {}
    dims = ['x','y','r']
    for dim in dims:
        ranges[dim] = range(-d, d+1)
    rangesInOrder = [ranges[dim] for dim in dims]
    transformSpaceDims = [len(dimrange) for dimrange in rangesInOrder]
    alltransforms =  list(itertools.product(*rangesInOrder))
    ntransforms = len(alltransforms)
    best = stat
    bestTransform = (0,0,0)
    start = datetime.datetime.now()
    for i, (x, y, r) in enumerate(alltransforms):
        transformed = transform(subject, x, y, r)
        stat = evaluate(target, transformed)
        if verbose:
            msg = 'Transform {0} of {1}: x={2} y={3} r={4} \t stat= {5}'
            print(msg.format(i, ntransforms, x, y, r, stat))
        else:
            progress.progressbar(i, ntransforms, start)
        if stat < best:
            best = stat
            bestImage = transformed
            bestTransform = (x,y,r)
    print(' ')
    msg = 'Best transform: x={0} y={1} r={2} \t stat= {stat}'
    print(msg.format(*bestTransform, stat=best))
    xform = {
        'tx':bestTransform[0],
        'ty':bestTransform[1],
        'rxy':bestTransform[2]
    }
    return xform

def savetransformed(subjectfile, xform, newfile, newAffine):
    indata = nibabel.load(subjectfile).get_data()
    xformdata = transform(indata, xform['tx'], xform['ty'], xform['rxy'])
    nibabel.save(nibabel.Nifti1Image(xformdata, newAffine), newfile)

def alignAndSave(subjectfile, targetfile, newfile=None, provenance=None):
    if not provenance:
        provenance = niprov.Context()
    if not newfile:
        newfile = subjectfile.replace('.nii','_coreg.nii')
    newAffine = nibabel.load(targetfile).get_affine()
    xform = align(subjectfile, targetfile, delta=10)
    indata = nibabel.load(subjectfile).get_data()
    xformdata = transform(indata, xform['tx'], xform['ty'], xform['rxy'])
    nibabel.save(nibabel.Nifti1Image(xformdata, newAffine), newfile)
    provenance.log(newfile, 'coregistration phantom', [subjectfile, targetfile])
    return newfile

def applyXformAndSave(xform, subjectfile, targetfile, newfile=None, 
        provenance=None):
    if not provenance:
        provenance = niprov.Context()
    if not newfile:
        newfile = subjectfile.replace('.nii','_coreg.nii')
    newAffine = nibabel.load(targetfile).get_affine()
    indata = nibabel.load(subjectfile).get_data()
    xformdata = transform(indata, xform['tx'], xform['ty'], xform['rxy'])
    nibabel.save(nibabel.Nifti1Image(xformdata, newAffine), newfile)
    provenance.log(newfile, 'coregistration phantom', [subjectfile, targetfile])
    return newfile






