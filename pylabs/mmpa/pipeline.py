import os, glob
from os.path import join
import niprov
import nibabel, numpy
from pylabs.utils.paths import getlocaldataroot
from niprov.options import NiprovOptions
from pylabs.vbm.upsample import upsample1mm
opts = NiprovOptions()
opts.dryrun = True
opts.verbose = True

fs = getlocaldataroot()
resultdir = join(fs,'self_control/hbm_group_data/mmpa/')
mmpaDataFile = join(resultdir, 'data.npy')
images = []
measures = []
measureSubjects = []

## Behavior
behavdir = join(fs,'self_control/behavioral_data/behav_from_andy_march27_2015/')
csvfile = join(behavdir,'EF_and_Brain_july08_2015_Meq0_delta.csv')
niprov.add(csvfile)

## VBM
vbmsubjects = [
317, 328, 332, 334, 335, 347, 353, 364, 371, 376, 379, 381, 384, 385, 396]
vbmdir = join(fs,'self_control/hbm_group_data/vbm_15subj/workdir_v1/stats/')
#vbmimgs2mm = glob.glob(join(vbmdir, '?M_mod_merg_s4.nii.gz'))
#images += upsample1mm(vbmimgs2mm, opts=opts) # is this correct for 4D files?
vbmimages = glob.glob(join(vbmdir, '?M_mod_merg_s4_1mm.nii.gz'))
images += vbmimages
measures += [os.path.basename(i)[:2] for i in images]
measureSubjects += [vbmsubjects]*len(vbmimages)

## TBSS
tbsssubjects = [317, 322, 324, 328, 332, 334, 335, 341, 347, 353, 364, 370, 371, 
    376, 379, 381, 384, 385, 396 ]
tbssdir = join(fs,'self_control/hbm_group_data/tbss_19subj/workdir_thr1p5_v3/stats/')
imgtemplate = 'all_{0}_skeletonised.nii.gz'
tbssmeasures = ['F1', 'F2', 'FA', 'L1', 'MD', 'MO', 'RA', 'AD', 'L2', 'L3']
measures += tbssmeasures
skellist = [imgtemplate.format(m) for m in tbssmeasures]
images += [join(tbssdir,i) for i in skellist]
measureSubjects += [tbsssubjects]*len(tbssmeasures)

## FMRI
fmridir = join(fs,'self_control/hbm_group_data/fmri')
#hdrfilterOneContrast = join(fmridir, 'analyze', '*_Congruent_gt_Incongruent.hdr')
#hdrimagesOneContrast = sorted(glob.glob(hdrfilterOneContrast))
#fmrisubjects = sorted([int(os.path.basename(i)[:3]) for i in hdrimagesOneContrast])
fmrisubjects = [317, 318, 332, 334, 335, 347, 353, 364, 370, 371, 376, 379,
 381, 384, 385, 396]
## assuming fmri pipeline has ran.
contrasts = ['Congruent', 'Incongruent']
fmriimages = [join(fmridir, c+'.nii.gz') for c in contrasts]
images += fmriimages
measures += [c[:2] for c in contrasts]
measureSubjects += [fmrisubjects]*len(contrasts)
# remap. http://brainmap.wustl.edu/help/mapper.html

## MM
[niprov.add(img) for img in images]
commonSubjects = set.intersection(*map(set, 
    [fmrisubjects, vbmsubjects, tbsssubjects]))

nsubjects = len(commonSubjects)
nmeasures = len(measures)
spatialdims = (182, 218, 182)
# subjects * measures * x * y * z
data = numpy.zeros((nsubjects, nmeasures)+spatialdims)
for m, measure in enumerate(measures):
    print('Loading data for measure {0} of {1}'.format(m+1, len(measures)))
    img = nibabel.load(images[m])
    measureData = img.get_data()
    for s, subjectid in enumerate(commonSubjects):
        measureSubjectIndex = measureSubjects[m].index(subjectid)
        data[s, m, :, :, :] = measureData[:,:,:, measureSubjectIndex]
print('Saving data..')
numpy.save(mmpaDataFile, data)
niprov.log(mmpaDataFile, 'data to one file', images)




