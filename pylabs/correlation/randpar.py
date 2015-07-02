# Wrappers to invoke FSL's randomise_parallel routine.
from pylabs.utils import Shell


def multirandpar(images, shell=Shell()):
    # randomise_parallel on multiple images and/or multiple predictors
    for image in images:
        cmd = 'randomize_parallel -i {0} '.format(image)        #input image
        cmd = cmd+'-o randpar_{0}/x'.format(image.split('.')[0]) #output dir
        shell.run(cmd)



