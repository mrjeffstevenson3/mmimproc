from os.path import join
import itertools, datetime
import nibabel, numpy, scipy.stats, scipy.ndimage
from pylabs.utils import progress


def nancount(A):
    return numpy.count_nonzero(numpy.isnan(A))

def nonnancount(A):
    return A.size - nancount(A)

def preproc(data):
    A = numpy.copy(data)

    #dismiss negative
    A[A < 0] = 0
    #dismiss extreme pos values
    uthresh = 20000
    A[A > uthresh] = uthresh
    zzero = (0-A.mean())/A.std()
    A = (A-A.mean())/A.std()

    # get rid of outliers
    thresh = 0.005 # outlier fraction one sided
    o = numpy.sort(A.ravel())[-int(thresh*A.size)] # outlier threshold
    A[A > o] = o

    #start at zero
    A = A + -zzero
    # plt.hist(A[A > 0].ravel(), 200)
    return A

def evaluate(target, subject):
    ztarget = preproc(target)
    zsubject = preproc(subject)
    diffmap = ztarget - zsubject
    return numpy.absolute(diffmap).mean()

## get data
datadir = join('data','phantom_align_samples')
targetfile = join(datadir,'T1_seir_mag_TR4000_2014-07-23_1.nii.gz')
subjectfile = join(datadir,'T1_seir_mag_TR4000_2014-07-03_1.nii.gz')
target = nibabel.load(targetfile).get_data()
subjectImg = nibabel.load(subjectfile)
subject = subjectImg.get_data()
affine = subjectImg.get_affine()

stat = evaluate(target, subject)
print('Baseline stat= {0}'.format(stat))

d = 10 # delta for transformations from center.
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

start = datetime.datetime.now()

for i, (x, y, r) in enumerate(alltransforms):

    shifted = scipy.ndimage.interpolation.shift(subject, [x, y])
    rot = scipy.ndimage.interpolation.rotate(shifted, r, reshape=False)
    stat = evaluate(target, rot)

    if verbose:
        msg = 'Transform {0} of {1}: x={2} y={3} r={4} \t stat= {5}'
        print(msg.format(i, ntransforms, x, y, r, stat))
    else:
        progress.progressbar(i, ntransforms, start)

    if stat < best:
        best = stat
        bestImage = rot
        bestTransform = (x,y,r)

print(' ')
msg = 'Best transform: x={0} y={1} r={2} \t stat= {stat}'
print(msg.format(*bestTransform, stat=best))
nibabel.save(nibabel.Nifti1Image(bestImage, affine), 'transformed.nii.gz')





