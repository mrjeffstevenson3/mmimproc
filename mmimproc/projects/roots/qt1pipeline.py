import glob, os, pandas, numpy, nibabel
from os.path import join
from mmimproc.utils.paths import getlocaldataroot, getnetworkdataroot
import mmimproc.correlation.correlate as correlate
import mmimproc.correlation.scatter as scatter
from mmimproc.clustering import clusterminsize
from mmimproc.atlassing import atlasWiseSignificantVoxelsFrame
from mmimproc.transformations.standard import standardizeBasedOnAbsoluteMask
from mmimproc.qt1.vectorfitting import fitT1WholeBrain
from mmimproc.conversion.helpers import par2mni_1file as conv
from mmimproc.qt1.b1mapcoreg import b1mapcoreg_1file
import mmimproc.masking as masking
from nipype.interfaces import fsl
from scipy.ndimage.filters import gaussian_filter
provenance = ProvenanceWrapper()

## behavior
from mmimproc.projects.roots.behavior import selectedvars
behavior = selectedvars.T

## directories
fs = getnetworkdataroot()
projectdir = join(fs, 'roots_of_empathy')
resultsdir = join(projectdir, 'correlations_qt1')
if not os.path.isdir(resultsdir):
    os.mkdir(resultsdir)
subjects = ['sub-2013-C0{}'.format(s) for s in behavior.index.values]
nsubjects = len(subjects)

# convert to nifti and fit T1
ref = None
subjectfiles = []
for s, subject in enumerate(subjects):
    print('Subject {} of {}: {}'.format(s+1, nsubjects, subject))
    sessiondir = join(projectdir, subject, 'ses-1')
    qt1dir = join(sessiondir, 'qt1')
    if not os.path.isdir(qt1dir):
        os.mkdir(qt1dir)
    outfpath = join(qt1dir, '{}_t1.nii.gz'.format(subject))
    parrecdir = join(sessiondir, 'source_parrec')
    parsfiles = glob.glob(join(parrecdir, '*T1_MAP*.PAR'))

    ## parrec to nifti conversion
    print('Converting parrecs..')
    sfiles = [conv(p) for p in parsfiles]
    parb1file = glob.glob(join(parrecdir, '*B1MAP*.PAR'))[0]
    b1fileLowRes = conv(parb1file)

    ## b1 file coregistration
    b1file = b1mapcoreg_1file(b1fileLowRes, sfiles[0])

    ## brain mask
    brainMask = masking.skullStrippedMask(sorted(sfiles)[0], provenance)
    sfiles = [masking.apply(brainMask, f, provenance) for f in sfiles]
    b1file = masking.apply(brainMask, b1file, provenance)

    ## T1 fitting
    print('T1 fitting..')
    fitT1WholeBrain(sfiles, b1file, outfpath, maxval=7000)

    ## align subject to target subject
    if ref is None:
        ref = outfpath
    refsub = os.path.basename(ref).split('_')[0]
    print('Aligning..')
    aligned = outfpath.replace('.nii.gz', '_flirt2{}'.format(refsub))
    flt = fsl.FLIRT(bins=640, cost_func='mutualinfo')
    flt.inputs.in_file = outfpath
    flt.inputs.reference = ref
    flt.inputs.out_file = aligned
    flt.inputs.out_matrix_file = aligned
    flt.inputs.interp = 'nearestneighbour'
    flt.run() 
    alignedfpath = aligned+'.nii.gz'
    #provenance.add(alignedfpath)
    stdfpath = standardizeBasedOnAbsoluteMask(alignedfpath, 
        os.path.dirname(alignedfpath))

    ## smooth
    sigma = 1.5
    print('Smoothing..')
    smoothfile = stdfpath.replace('.nii', '_sigma{}.nii'.format(sigma))
    img = nibabel.load(stdfpath)
    data = img.get_data()
    affine = img.get_affine()
    smoothdata = gaussian_filter(data, sigma)
    nibabel.save(nibabel.Nifti1Image(smoothdata, affine), smoothfile)
    subjectfiles.append(smoothfile)

## correlation
subjectfiles = sorted(subjectfiles)
statfiles, pcorr, tcorr = correlate.wholeBrain(subjectfiles, behavior, 
                outdir = resultsdir, niterations = 1000) # 30mins

## cluster thresholding
statfiles, clutables, clumaps = clusterminsize(statfiles, pcorr, minsize=10)

## table
atlasfpath = 'data/atlases/JHU_MNI_SS_WMPM_Type_I_matched.nii.gz'
frame = atlasWiseSignificantVoxelsFrame(statfiles, pmax=pcorr, atlas=atlasfpath)
#frame = frame.dropna(how='all', axis=1)
#frame = frame.loc[:, (frame != 0).any(axis=0)]
frame.to_json('roots_qt1.json')
frame.to_csv('roots_qt1.csv')

## scatterplots
#scatter.forLowestPvalue(subjectfiles, behavior, statfiles)
scatter.forClusters(subjectfiles, behavior, clumaps, clutables)








