import numpy, nibabel, collections


def statsByRegion(image, atlas):
    img = nibabel.load(image)
    atlasImg = nibabel.load(atlas)
    if not img.shape == atlasImg.shape:
        raise ValueError("Input image and atlas must have same dimensions")

    atlasImgData = atlasImg.get_data()
    regionIndices = numpy.unique(atlasImgData)
    nregions = len(regionIndices)
    regionMasks = []
    for index in regionIndices:
        regionMasks.append(atlasImgData == index)

    imgData = img.get_data()
    stats = collections.defaultdict(lambda : numpy.zeros((nregions,)))
    for r, regionMask in enumerate(regionMasks):
        regionData = imgData[regionMask]
        stats['average'][r] = regionData.mean()
    return stats
