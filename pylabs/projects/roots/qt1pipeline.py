import glob, os, pandas, numpy, niprov, nibabel
from os.path import join
from pylabs.utils.paths import getlocaldataroot, getnetworkdataroot
from pylabs.correlation.correlate import correlateWholeBrain
from pylabs.qt1.vectorfitting import fitT1WholeBrain
from pylabs.conversion.helpers import par2mni_1file as conv
from pylabs.qt1.b1mapcoreg import b1mapcoreg_1file
from nipype.interfaces import fsl
from scipy.ndimage.filters import gaussian_filter
provenance = niprov.Context()

## behavior
from pylabs.projects.roots.behavior import selectedvars
behavior = selectedvars.T

## directories
#fs = getlocaldataroot()
fs = getnetworkdataroot()
projectdir = join(fs, 'roots_of_empathy')
resultsdir = join(projectdir, 'correlations_qt1')
if not os.path.isdir(resultsdir):
    os.mkdir(resultsdir)
subjects = ['sub-2013-C0{}'.format(s) for s in behavior.index.values]
nsubjects = len(subjects)

# convert to nifti and fit T1
t1files = []
for s, subject in enumerate(subjects):
    print('Converting parrecs for {} of {}: {}'.format(s+1, nsubjects, subject))
    sessiondir = join(projectdir, subject, 'ses-1')
    qt1dir = join(sessiondir, 'qt1')
    if not os.path.isdir(qt1dir):
        os.mkdir(qt1dir)
    outfpath = join(qt1dir, '{}_t1.nii.gz'.format(subject))
    parrecdir = join(sessiondir, 'source_parrec')
    parsfiles = glob.glob(join(parrecdir, '*T1_MAP*.PAR'))
    sfiles = [conv(p) for p in parsfiles]
    parb1file = glob.glob(join(parrecdir, '*B1MAP*.PAR'))[0]
    b1fileLowRes = conv(parb1file)
    b1file = b1mapcoreg_1file(b1fileLowRes, sfiles[0])
    print('T1 fitting subject {} of {}: {}'.format(s, nsubjects, subject))
    fitT1WholeBrain(sfiles, b1file, outfpath)
    t1files.append(outfpath)


## align
alignedfiles = []
ref = t1files[0]
refsub = os.path.basename(ref).split('_')[1]
for s, unaligned in enumerate(t1files):
    print('Aligning {} of {}'.format(s+1, nsubjects))
    aligned = unaligned.replace('.nii', '_flirt2{}.nii'.format(refsub))
    flt = fsl.FLIRT(bins=640, cost_func='mutualinfo')
    flt.inputs.in_file = unaligned
    flt.inputs.reference = ref
    flt.inputs.out_file = aligned
    flt.inputs.out_matrix_file = aligned.replace('.nii.gz', '.mat')
    flt.inputs.interp = 'nearestneighbour'
    flt.run() 
    alignedfiles.append(aligned)

## smooth
sigma = 2
smoothedfiles = []
for s, unsmoothfile in enumerate(alignedfiles):
    print('Smoothing {} of {}'.format(s+1, nsubjects))
    smoothfile = unsmoothfile.replace('.nii', '_sigma{}.nii'.format(sigma))
    img = nibabel.load(unsmoothfile)
    data = img.get_data()
    affine = img.get_affine()
    smoothdata = gaussian_filter(data, sigma)
    nibabel.save(nibabel.Nifti1Image(smoothdata, affine), smoothfile)
    smoothedfiles.append(smoothfile)

## correlation
cfiles = sorted(smoothedfiles)
outfiles = correlateWholeBrain(cfiles, behavior, 
                outdir = resultsdir, niterations = 500) # 30mins
## Clustering, clustertable? see nipy.labs.statistical_mapping.cluster_stats




