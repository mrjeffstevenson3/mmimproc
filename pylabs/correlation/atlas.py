import nibabel, numpy
from pylabs.utils.tables import TablePublisher


def report(image, atlas, regionnames=None, table=TablePublisher()):
    """Report on statistics based on atlas regions

    Args:
        image (str): List of paths to images with statistic.
        atlas (str): Path to atlas
        regionnames (list): List of labels for the atlas regions. Must be in the 
            order of the atlas indices. Should include a label for 0.
        opts (PylabsOptions): General settings
        table (TablePublisher): Table interface

    Returns:
        list: path to .csv file created.
    """
    threshold = .95
    # Gather data
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
    # Create table
    table.setData(tabledata)
    if regionnames:
        table.setRowHeaders(regionnames)
    table.publish()

