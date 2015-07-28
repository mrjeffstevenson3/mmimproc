import nibabel, numpy


def report(image, atlas, table=None):
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

    statsimg = nibabel.load(image)
    atlasimg = nibabel.load(atlas)
    if not statsimg.shape == atlasimg.shape:
        raise ValueError("Input image and atlas must have same dimensions")
    atlasImgData = atlasimg.get_data()
    statsImgData = statsimg.get_data()
    regionIndices = numpy.unique(atlasImgData)
    tabledata = []
    for r in regionIndices:
        regionMask = atlasImgData == r
        regionData = statsImgData[regionMask]
        kSignificant = (regionData > threshold).sum()
        tabledata.append(kSignificant)
    table.setData(tabledata)

