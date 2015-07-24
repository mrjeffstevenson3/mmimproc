

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


