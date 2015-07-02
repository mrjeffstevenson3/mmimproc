# Wrappers to invoke FSL's randomise_parallel routine.
from pylabs.utils import Shell


def multirandpar(images, shell=Shell()):
    # randomise_parallel on multiple images and/or multiple predictors
    for image in images:
        shell.run('randomize_parallel -i '+image)



