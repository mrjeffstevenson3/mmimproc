import itertools, glob, nibabel
from os.path import join
import pylabs.alignment.phantom
from pylabs.utils.paths import getlocaldataroot

rootdir = join(getlocaldataroot(),'phantom_qT1_disc')
t1dirs = glob.glob(join(rootdir, 'T1*'))
uncoregdirs = [d for d in t1dirs if 'reg' not in d]
uncoregfilesByDir = [glob.glob(join(d, '*.nii.gz')) for d in uncoregdirs]
uncoregfiles = list(itertools.chain(*uncoregfilesByDir))
nfiles = len(uncoregfiles)

datadir = join('data','phantom_align_samples')
targetfile = join(datadir,'T1_seir_mag_TR4000_2014-07-23_1.nii.gz')
newAffine = nibabel.load(targetfile).get_affine()

for f, subjectfile in enumerate(uncoregfiles):
    print('Aligning file {0} of {1}'.format(f, nfiles))

    newFile = subjectfile.replace('.nii','_coreg723.nii')
    xform = pylabs.alignment.phantom.align(subjectfile, targetfile, delta=7)
    pylabs.alignment.phantom.savetransformed(subjectfile, xform, newFile, newAffine)

#    ornt = io_orientation(np.diag([-1, 1, 1, 1]).dot(pr_img.affine))
#    t_aff = inv_ornt_aff(ornt, pr_img.shape)
#    affine = np.dot(pr_img.affine, t_aff)
#    in_data_ras = apply_orientation(in_data, affine)
#xaffine = pylabs.alignment.spaces.xform2affine(**xform)
#xform = {
#    'tx':x,
#    'ty':y,
#    'rxy':r,
#}
