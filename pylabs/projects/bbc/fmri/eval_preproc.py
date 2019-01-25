import glob, shutil, os, niprov, numpy, pandas, nibabel
from os.path import join, basename, dirname, isfile, isdir, splitext
from fmr_runs import picks

#rootdir = '/home/jasper/mirror/js/bbc'
rootdir = '/diskArray/data/bbc/'
fmrdirtem = 'sub-bbc{}/ses-{}/fmri/'
fmrnametem = 'sub-bbc{}_ses-{}_fmri_{}.nii'
cols = {'sess':0, 'run':0, 'nvols':0, 'abs-avg':1,'abs-max':1, 'rel-avg':1, 'rel-max':1}
evaldata = pandas.DataFrame(columns=cols.keys())
motiondir = join(rootdir, 'eval', 'motion')
regdir = join(rootdir, 'eval', 'reg')
for subdir in (motiondir, regdir):
    if not isdir(subdir):
        os.makedirs(subdir)
picktem = '{}_ses-{}_run{}'
disptem = 'prefiltered_func_data_mcf_{}.rms'

for subjectpick in picks:

    subnum, session, run = subjectpick
    info = {'sess':session, 'run':run}
    subjectfmrdir = join(rootdir, fmrdirtem.format(subnum, session))
    featdirs = glob.glob(join(subjectfmrdir, '*.feat'))
    if not featdirs:
        continue
    indexLatest = numpy.array([d.count('+') for d in featdirs]).argmax()
    featdir = featdirs[indexLatest]
    picktag = picktem.format(subnum, session, run)
    shutil.copyfile(join(featdir , 'mc', 'disp.png'), 
                    join(motiondir, picktag+'.png'))
    shutil.copyfile(join(featdir, 'report_reg.html'), 
                    join(regdir, picktag+'.html'))
    for meas in ('abs', 'rel'):
        dispfpath = join(featdir , 'mc', disptem.format(meas))
        displacement = numpy.loadtxt(dispfpath)
        info[meas+'-avg'] = displacement.mean()
        info[meas+'-max'] = displacement.max()
    fmrname = fmrnametem.format(subnum, session, run)
    img = nibabel.load(join(subjectfmrdir, fmrname))
    info['nvols'] = img.shape[-1]
    evaldata.loc[subnum] = info
print(evaldata)
evaldata.to_csv('fmri_preproc_eval.csv')

