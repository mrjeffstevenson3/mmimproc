import glob, os, pandas, numpy, niprov, nibabel
from os.path import join
from pylabs.utils.paths import getlocaldataroot, getnetworkdataroot
import pylabs.correlation.correlate as correlate
import pylabs.correlation.scatter as scatter
from pylabs.qt1.vectorfitting import fitT1WholeBrain
from pylabs.conversion.helpers import par2mni_1file as conv
from pylabs.qt1.b1mapcoreg import b1mapcoreg_1file
import pylabs.masking as masking
from nipype.interfaces import fsl
from scipy.ndimage.filters import gaussian_filter
provenance = niprov.Context()

## behavior
from pylabs.projects.roots.behavior import selectedvars
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
    print('Converting parrecs for {} of {}: {}'.format(s+1, nsubjects, subject))
    sessiondir = join(projectdir, subject, 'ses-1')
    qt1dir = join(sessiondir, 'qt1')
    if not os.path.isdir(qt1dir):
        os.mkdir(qt1dir)
    outfpath = join(qt1dir, '{}_t1.nii.gz'.format(subject))
    parrecdir = join(sessiondir, 'source_parrec')
    parsfiles = glob.glob(join(parrecdir, '*T1_MAP*.PAR'))

    ## parrec to nifti conversion
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
    print('T1 fitting subject {} of {}: {}'.format(s, nsubjects, subject))
    fitT1WholeBrain(sfiles, b1file, outfpath)

    ## align subject to target subject
    if ref is None:
        ref = outfpath
    refsub = os.path.basename(ref).split('_')[0]
    print('Aligning {} of {}'.format(s+1, nsubjects))
    aligned = outfpath.replace('.nii.gz', '_flirt2{}'.format(refsub))
    flt = fsl.FLIRT(bins=640, cost_func='mutualinfo')
    flt.inputs.in_file = outfpath
    flt.inputs.reference = ref
    flt.inputs.out_file = aligned
    flt.inputs.out_matrix_file = aligned
    flt.inputs.interp = 'nearestneighbour'
    flt.run() 
    alignedfpath = aligned+'.nii.gz'

    ## smooth
    sigma = 2
    print('Smoothing {} of {}'.format(s+1, nsubjects))
    smoothfile = alignedfpath.replace('.nii', '_sigma{}.nii'.format(sigma))
    img = nibabel.load(alignedfpath)
    data = img.get_data()
    affine = img.get_affine()
    smoothdata = gaussian_filter(data, sigma)
    nibabel.save(nibabel.Nifti1Image(smoothdata, affine), smoothfile)
    subjectfiles.append(smoothfile)

## correlation
subjectfiles = sorted(subjectfiles)
statfiles = correlate.wholeBrain(subjectfiles, behavior, 
                outdir = resultsdir, niterations = 5) # 30mins
## scatterplots
scatter.forLowestPvalue(subjectfiles, behavior, statfiles)

## Clustering, clustertable? see nipy.labs.statistical_mapping.cluster_stats




