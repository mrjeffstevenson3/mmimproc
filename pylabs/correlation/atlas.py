import nibabel, numpy
from pylabs.utils.tables import TablePublisher


def report(images, atlas, regionnames=None, threshold = .95,
    relevantImageFilenameSegment=0, table=TablePublisher()):
    """Report on statistics based on atlas regions

    Args:
        image (list): List of paths to images with statistic.
        atlas (str): Path to atlas
        regionnames (list): List of labels for the atlas regions. Must be in the 
            order of the atlas indices. Should include a label for 0.
        threshold (float): Voxel threshold to use when counting. Defaults to 0.95
        relevantImageFilenameSegment (int): If the input stats image filename is
            broken up along underscores, which part of it to use as a column 
            header. Defaults to 0. (first element)
        opts (PylabsOptions): General settings
        table (TablePublisher): Table interface

    Returns:
        list: path to .csv file created.
    """
    # Gather data
    cols = [image.split('_')[relevantImageFilenameSegment] for image in images]
    print('Loading atlas..')
    atlasimg = nibabel.load(atlas)
    atlasImgData = atlasimg.get_data()
    regionIndices = numpy.unique(atlasImgData)
    regionMasks = []
    for index in regionIndices:
        regionMasks.append(atlasImgData == index)

    tabledata = numpy.full([len(regionIndices), len(images)],numpy.nan)
    for i, image in enumerate(images):
        print('Loading image {0} of {1}..'.format(i+1, len(images)))
        statsimg = nibabel.load(image)
        if not statsimg.shape == atlasimg.shape:
            raise ValueError("Input image and atlas must have same dimensions")
        statsImgData = statsimg.get_data()

        for r, regionMask in enumerate(regionMasks):
            regionData = statsImgData[regionMask]
            kSignificant = (regionData > threshold).sum()
            tabledata[r, i] = kSignificant
    # Create table
    table.setData(tabledata)
    if regionnames:
        table.setRowHeaders(regionnames)
    table.setColumnHeaders(cols)
    table.publish()

