import glob, shutil, os, niprov
from os.path import join, basename, dirname, isfile, isdir
from nipype.interfaces import fsl
from mmimproc.utils._context import WorkingContext

#indir = '/home/jasper/mirror/js/bbc'
indir = '/diskArray/data/bbc/'
provenance = niprov.ProvenanceContext()


for subjectdir in glob.glob(join(indir, 'sub-*')):
    wemprs = glob.glob(join(subjectdir,'*','anat','*wempr_1.nii*'))
    for fpath in wemprs:
        print('Skullstripping '+basename(fpath))
        with WorkingContext(dirname(fpath)):
            result = fsl.BET(in_file=fpath, mask=True, frac=.3).run()
            img = provenance.log(result.outputs.out_file, 'skullstrip', fpath)
            img.viewSnapshot()

