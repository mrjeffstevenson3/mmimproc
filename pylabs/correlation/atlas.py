import nibabel, numpy


def report(image, atlas):
    """Report on statistics based on atlas regions

    Args:
        image (str): List of paths to images with statistic.
        atlas (str): Path to atlas
        opts (PylabsOptions): General settings

        filesys (pylabs.utils.Filesystem): Pass a mock here for testing purpose.
        listener: 

    Returns:
        list: path to .csv file created.
    """
    threshold = .95

    print(nibabel.load(image).shape)
    print(nibabel.load(atlas).shape)
    print(numpy.unique(nibabel.load(atlas).get_data()))
    print(numpy.unique(nibabel.load(image).get_data()))

# TODO:
# opts.visualize
# for each region, count supra-threshold voxels


