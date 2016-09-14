import itertools, glob, nibabel, os
from os.path import join
import pylabs.alignment.phantom
from pylabs.utils.paths import getlocaldataroot
from pylabs.qt1.naming import qt1filepath

targetfile = join(getlocaldataroot(),'phantom_qT1_slu',
    'phantom_alignment_target.nii.gz')

def coregisterPhantoms(uncoregfiles, projectdir, overwrite=False, dirstruct='BIDS'):
    provenance = ProvenanceWrapper()
    nfiles = len(uncoregfiles)
    outimages = []
    newAffine = nibabel.load(targetfile).get_affine()
    for f, image in enumerate(uncoregfiles):
        subjectfile = qt1filepath(image, projectdir, dirstruct)
        fname = os.path.basename(subjectfile)
        print('Aligning file {0} of {1}: {2}'.format(f, nfiles, fname))

        newFile = subjectfile.replace('.nii','_coreg302.nii')

        image['coreg'] = True
        image['coregtag'] = '_coreg'
        if os.path.isfile(newFile) and not overwrite:
            print('File exists, skipping..')
            outimages.append(image)
            continue

        try:
            xform = pylabs.alignment.phantom.align(subjectfile, targetfile, delta=10)
            pylabs.alignment.phantom.savetransformed(subjectfile, xform, newFile, newAffine)
        except Exception as e:
            print('Error aligning file: '+str(e))
        else:
            outimages.append(image)
            provenance.log(newFile, 'coregistration phantom', 
                [subjectfile, targetfile])

    return outimages # returns only coreg'd images

if __name__ == '__main__':
    rootdir = join(getlocaldataroot(),'phantom_qT1_disc')
    t1dirs = glob.glob(join(rootdir, 'T1*'))
    uncoregdirs = [d for d in t1dirs if 'reg' not in d]
    uncoregfilesByDir = [glob.glob(join(d, 'T1*.nii.gz')) for d in uncoregdirs]
    uncoregfiles = list(itertools.chain(*uncoregfilesByDir))
    uncoregfiles = [f for f in uncoregfiles if 'coreg' not in f]
    coregisterPhantoms(uncoregfiles, dirstruct='legacy')


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

