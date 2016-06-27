import numpy, nibabel, collections, os, pandas
from pylabs.correlation.atlas import atlaslabels


def statsByRegion(image, atlas, threshold=None):
    labels = atlaslabels(os.path.basename(atlas))
    img = nibabel.load(image)
    imgData = img.get_data()
    if len(imgData.shape) == 4:
        imgData = imgData[:,:,:,0]
        print('[pylabs] statsByRegion: Found multiple volumes, using first.')
    imgData = numpy.squeeze(imgData)
    
    atlasImg = nibabel.load(atlas)
    atlasData = atlasImg.get_data()
    if not imgData.shape == atlasData.shape:
        msg = ("Input image and atlas must have same dimensions. "+
            "Image: {0} Atlas: {1}".format(imgData.shape, atlasData.shape))
        raise ValueError(msg)


    regionIndices = numpy.unique(atlasData)
    nregions = len(regionIndices)
    regionMasks = []
    for index in regionIndices:
        regionMasks.append(atlasData == index)

    cols = ['all', 'k', 'average', 'superthreshold']
    stats = pandas.DataFrame(index=labels, columns=cols)
    for r, regionMask in enumerate(regionMasks):
        regionData = imgData[regionMask]
        stats['all'][r] = regionData
        stats['k'][r] = regionData.size
        stats['average'][r] = regionData.mean()
        if threshold:
            stats['superthreshold'][r] = regionData > threshold
    return stats

def averageByRegion(image, atlasfpath):
    return statsByRegion(image, atlasfpath)['average'].astype(float)

