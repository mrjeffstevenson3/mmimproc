# Wrappers to invoke FSL's randomise_parallel routine.
import os
from pylabs.utils import Shell, PylabsOptions, Binaries, WorkingContext
import niprov


def multirandpar(images, mats, designfile, niterations=50, workdir=os.getcwd(),
    shell=Shell(), binaries=Binaries(), context=WorkingContext, 
    opts=PylabsOptions()):
    """ randomise_parallel on multiple images and/or multiple predictors

    Expects mask files to exist for each unique image prefix 
    (underscore-delineated); i.e. "GM_mod_merge.img" would require a "GM_mask"

    Default options / flags set are TFCE and Variant Smoothing.

    Args:
        images (list): List of image files
        mats (list): List of behavior data .mat files.
        designfile (str): FSL .con file with design.
        niterations (int): Number of iterations to run. Defaults to 50.
        workdir (str): Root dir in which to create matfiles subdir. Defaults 
            to current directory.
        shell (pylabs.utils.Shell): Override to inject a mock for shell calls.
        binaries (pylabs.utils.Binaries): Provides paths to binaries
        context (pylabs.utils.WorkingContext): Helps switching to working dir
        opts (pylabs.utils.PylabsOptions): General settings.
    """
    outfiles = []
    for image in images:
        datadir = os.path.dirname(image)
        imagebasename = os.path.basename(image)
        imagename = os.path.basename(image).split('.')[0]
        ext = '.'.join(os.path.basename(image).split('.')[1:])
        maskfile = os.path.join(datadir, imagename.split('_')[0]+'_mask.'+ext)
        resultsubdir = 'randpar_{0}_{1}'.format(niterations, imagename)
        for mat in mats:
            matname = os.path.basename(mat).split('.')[0]
            resultdir = os.path.join(datadir, resultsubdir)
            shell.run('mkdir -p {0}'.format(resultdir))
            resultfile = os.path.join(resultdir, 'randpar_{0}_{1}_{2}'.format(
                niterations, matname, imagebasename))
            cmd = binaries.randpar
            cmd += ' -i {0}'.format(image)                  #input image
            cmd += ' -o {0}'.format(resultfile)   #output dir, file
            cmd += ' -m {0}'.format(maskfile)               #mask file
            cmd += ' -d {0}'.format(mat)                #behavior .mat file
            cmd += ' -t {0}'.format(designfile)      #design/ contrast file
            cmd += ' -n {0}'.format(niterations)      #number of iterations
            cmd += ' -T'                # T= TFCE threshold free clustering.
            cmd += ' -V'                            # V=variant smoothing,
            with context(workdir):
                niprov.record(cmd, opts=opts)
            outfiles.append(resultfile)
    return outfiles



