from os.path import join
import nibabel, numpy, scipy.stats, scipy.ndimage
scipy.ndimage.interpolation.rotate

def nancount(A):
    return numpy.count_nonzero(numpy.isnan(A))

def nonnancount(A):
    return A.size - nancount(A)

datadir = join('data','phantom_align_samples')
targetfile = join(datadir,'T1_seir_mag_TR4000_2014-07-23_1.nii.gz')
subjectfile = join(datadir,'T1_seir_mag_TR4000_2014-07-03_1.nii.gz')


target = nibabel.load(targetfile).get_data()
subject = nibabel.load(subjectfile).get_data()



A = numpy.copy(target)

uthresh = 20000

#dismiss negative
A[A < 0] = 0
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



devimap = numpy.absolute(ztarget - zsubject)
stat = devimap.mean()

print(stat)


# rot = scipy.ndimage.interpolation.rotate(A,10,reshape=False)
