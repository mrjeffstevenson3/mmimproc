import os, inspect
from pathlib import *
import nibabel, numpy, pylabs
from pylabs.utils.tables import TablePublisher
from pylabs.utils import Filesystem
from pylabs.utils.provenance import ProvenanceWrapper
provenance = ProvenanceWrapper()
filesys = Filesystem()
pylabs_atlasdir = Path(*Path(inspect.getabsfile(pylabs)).parts[:-2]) / 'data' / 'atlases'

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

def atlaslabels(atlasfilename, filesys=Filesystem()):
    return filesys.readlines('data/atlaslabels/{0}.txt'.format(atlasfilename))

def make_mask_fm_atlas_parts(atlas, roi_list, mask_fname):
    if not filesys.fileExists(atlas):
        raise IOError(atlas + " atlas file File Doesn't Exist. Please check.")
    img = nibabel.load(atlas)
    img_data = img.get_data()
    mask = numpy.zeros(img_data.shape)
    for roi in roi_list:
        mask[img_data == roi] = 1
    mask_img = nibabel.Nifti1Image(mask, img.affine, img.header)
    mask_img.set_qform(img.affine, code=1)
    mask_img.header['cal_max'] = 1
    nibabel.save(mask_img, mask_fname)
    roi_list_dict = {}
    roi_list_dict['roi_list'] = roi_list
    provenance.log(mask_fname, 'extract roi_list regions from atlas into mask', atlas, script=__file__, provenance=roi_list_dict)
    return

def make_mask_fm_tracts(atlas, volidx, thresh, mask_fname):
    if not filesys.fileExists(atlas):
        raise IOError(atlas + " atlas file File Doesn't Exist. Please check.")
    img = nibabel.load(atlas)
    img_data = img.get_data()
    if len(img_data.shape) != 4:
        raise IOError(atlas + " atlas file File Doesn't have 4 Dims. must be a 4D tract probability Vol.")
    mask = numpy.zeros(img_data.shape[:3])
    mask[img_data[..., volidx - 1] > thresh['thr']] = 1
    mask_img = nibabel.Nifti1Image(mask, img.affine, img.header)
    mask_img.set_qform(img.affine, code=1)
    mask_img.header['cal_max'] = 1
    nibabel.save(mask_img, mask_fname)
    provenance.log(mask_fname, 'extract roi_list regions from atlas into mask', atlas, script=__file__,
                   provenance={'vol indx': volidx, 'thresh': thresh['thr']})
    return
