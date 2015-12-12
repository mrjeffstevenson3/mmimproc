import glob, pickle, shutil, datetime, os, nibabel
from os.path import join
from pylabs.utils.paths import getlocaldataroot


imageDict = {}
rootdir = join(getlocaldataroot(),'phantom_qT1_disc')
newdir = join(rootdir,'T1_gilad_spgr_mag_TR11p0')
if not os.path.isdir(newdir):
    os.mkdir(newdir)
fnametem = 'T1_gilad_spgr_mag_TR11p0_{0}_1_b1corr.nii.gz'

sessiondirs = glob.glob(join(rootdir,'phantom_qT1*'))
for sessiondir in sessiondirs:
    filepath = join(sessiondir,'fitted_spgr_qT1','T13DNFA_fixed_b1.nii.gz')
    if os.path.isfile(filepath):
        print(filepath)
        datestr = os.path.basename(sessiondir).split('_')[-1]
        date =  datetime.datetime.strptime(datestr, '%Y%m%d').date()
        key = (date, 'gilad_spgr', 11.0, 1)
        imageDict[key] = None
        newfilepath = join(newdir, fnametem.format(date))
        #shutil.copy(filepath, newfilepath)

        maskfname = 'orig_seir_ti_3000_tr_4000_mag_1slmni_1_mask.nii'
        maskfile = join(sessiondir,'fitted_seir_qT1',maskfname)
        if not os.path.isfile(maskfile):
            print('No mask for {0}.'.format(date))
            continue
        maskimg = nibabel.load(maskfile)
        if not maskimg.shape == (182,218):
            print('Faulty mask for {0}.'.format(date))
            continue
        unmaskedimg = nibabel.load(filepath)
        newdata = unmaskedimg.get_data() * maskimg.get_data()
        newimg = nibabel.Nifti1Image(newdata, unmaskedimg.get_affine())
        nibabel.save(newimg, newfilepath)


imageDictFile = join(rootdir,'phantom_disc_dict_gilad.txt')
pickle.dump(imageDict, open( imageDictFile, 'wb'))




