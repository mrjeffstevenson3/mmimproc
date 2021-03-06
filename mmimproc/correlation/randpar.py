# Wrappers to invoke FSL's randomise_parallel routine.
import os
from mmimproc.utils import Shell, Binaries, WorkingContext
from mmimproc.utils.provenance import ProvenanceWrapper


def multirandpar(imageMatCombinations, designfile, masks=None, niterations=50, 
    workdir=os.getcwd(), outdir=None, tbss=False, shell=Shell(), t_thresh=0.0,
    binaries=Binaries(), context=WorkingContext, provenance=ProvenanceWrapper()):
    """ randomise_parallel on multiple images and/or multiple predictors

    Expects mask files to exist for each unique image prefix 
    (underscore-delineated); i.e. "GM_mod_merge.img" would require a "GM_mask"

    http://fsl.fmrib.ox.ac.uk/fsl/fslwiki/Randomise/UserGuide

    Default options / flags set are TFCE and Variant Smoothing.
    "for normal, 3D data (such as in an FSL-VBM analysis), you should just use 
    the -T option, while for TBSS analyses (that is in effect on the mostly "2D"
     white matter skeleton), you should use the --T2 option."

    Args:
        imageMatCombinations (dict): Dictionary with as keys the images and as 
		values the list of behavior .mat files to use for that image.
        designfile (str): FSL .con file with design.
        masks (dict): Optional dictionary with keys corresponding to images, and
            values the path(s) to the respective mask file to use. Defaults to 
            None, in which case mask files will be assumed to follow a naming 
            scheme (see above).
        niterations (int): Number of iterations to run. Defaults to 50.
        workdir (str): Will use context to switch to this directory during 
            processing.
        outdir (str): Where to store resulting files. Defaults to the directory
            where the input image file is.
        tbss (bool): Set to true for TBSS analyzed data, which will set the TFCE
            flag for randomise to T2, meaning 2 dimensional clustering. 
            Defaults to False.
        shell (mmimproc.utils.Shell): Override to inject a mock for shell calls.
        binaries (mmimproc.utils.Binaries): Provides paths to binaries
        context (mmimproc.utils.WorkingContext): Helps switching to working dir
        opts (mmimproc.utils.MmimprocOptions): General settings.

        randomise -i GM_mod_merg_s3 -m GM_mask -o fslvbm -d design.mat -t design.con -c 2.3 -n 5000
    """
    outfiles = []
    for image in imageMatCombinations.keys():
        datadir = os.path.dirname(image)
        if outdir is None:
            resultdir = datadir
        else:
            resultdir = outdir
        imagebasename = os.path.basename(image)
        imagename = os.path.basename(image).split('.')[0]
        ext = '.'.join(os.path.basename(image).split('.')[1:])
        maskfile = os.path.join(datadir, imagename.split('_')[0]+'_mask.'+ext)
        for mat in imageMatCombinations[image]:
            matname = os.path.basename(mat).split('.')[0]
            shell.run('mkdir -p {0}'.format(resultdir))
            resultfile = os.path.join(resultdir, 'randpar_n{0}_{1}_{2}'.format(
                niterations, imagename, matname))
            cmd = binaries.randpar
            cmd += ' -i {0}'.format(image)                  #input image
            cmd += ' -o {0}'.format(resultfile)   #output dir, file
            if masks is None:
                cmd += ' -m {0}'.format(maskfile) #follow naming scheme 
            else:
                cmd += ' -m {0}'.format(masks[image]) #masks specified in arg
            cmd += ' -d {0}'.format(mat)                #behavior .mat file
            cmd += ' -t {0}'.format(designfile)      #design/ contrast file
            cmd += ' -n {0}'.format(niterations)      #number of iterations
            if t_thresh:
                cmd += ' -c '+str(t_thresh)
            else:
                if tbss:
                    cmd += ' --T2'          # T= TFCE 2D for TBSS type data.
                else:
                    cmd += ' -T'          # T= TFCE 3D.
                cmd += ' -V'                            # V=variant smoothing,
            with context(workdir):
                provenance.record(cmd, transient=True)
            outfiles.append(resultfile)
    return outfiles



