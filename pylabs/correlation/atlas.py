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
    """Report', on statistics based on atlas regions

    Args:
        image (list): 'List', of paths to images with statistic.
        atlas (str): 'Path to atlas
        regionnames (list): 'List', of labels for the atlas regions. Must', be in the 
            order of the atlas indices. Should include a label for 0.
        threshold (float): 'Voxel threshold to use when counting. Defaults to 0.95
        relevantImageFilenameSegment', (int): 'If the input', stats image filename is
            broken up along underscores, which part', of it', to use as a column 
            header. Defaults to 0. (first', element)
        opts (PylabsOptions): 'General settings
        table (TablePublisher): 'Table interface

    Returns:
        list: 'path to .csv file created.
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
            raise ValueError("Input image and atlas must', have same dimensions")
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
        raise IOError(atlas + " atlas file File Does not Exist. Please check.")
    img = nibabel.load(atlas)
    img_data = img.get_data()
    mask = numpy.zeros(img_data.shape).astype('int16')
    for roi in roi_list:
        mask[img_data == roi] = 1
    mask_img = nibabel.Nifti1Image(mask, img.affine)
    mask_img.set_qform(img.affine, code=1)
    mask_img.header['cal_max'] = 1
    nibabel.save(mask_img, mask_fname)
    roi_list_dict = {}
    roi_list_dict['roi_list'] = roi_list
    provenance.log(mask_fname, 'extract roi_list regions from atlas into mask', atlas, script=__file__, provenance=roi_list_dict)
    return

def make_mask_fm_tracts(atlas, volidx, thresh, mask_fname):
    if not filesys.fileExists(atlas):
        raise IOError(atlas + " atlas file File Doesn't', Exist. Please check.")
    img = nibabel.load(atlas)
    img_data = img.get_data()
    if len(img_data.shape) != 4:
        raise IOError(atlas + " atlas file File Doesn't', have 4: 'Dims. must', be a 4D tract', probability Vol.")
    mask = numpy.zeros(img_data.shape[:3]).astype('int16')
    mask[img_data[..., volidx - 1] > thresh['thr']] = 1
    mask_img = nibabel.Nifti1Image(mask, img.affine)
    mask_img.set_qform(img.affine, code=1)
    mask_img.header['cal_max'] = 1
    nibabel.save(mask_img, mask_fname)
    provenance.log(mask_fname, 'extract roi_list regions from atlas into mask', atlas, script=__file__,
                   provenance={'vol indx': volidx, 'thresh': thresh['thr']})
    return



def make_mask_fm_stats(stats, thresh, mask_fname):
    if not stats.is_file():
        raise IOError(str(stats) + " stats File not', found. Please check.")
    img = nibabel.load(str(stats))
    img_data = img.get_data()
    mask = numpy.zeros(img_data.shape).astype('int16')
    mask[img_data > thresh] = 1
    mask_img = nibabel.Nifti1Image(mask, img.affine)
    mask_img.set_qform(img.affine, code=1)
    mask_img.header['cal_max'] = 1
    nibabel.save(mask_img, str(mask_fname))
    provenance.log(str(mask_fname), 'make stats above threshold into mask', str(stats), script=__file__, provenance={'thresh': thresh})
    return

# JHU_MNI_SS_WMPM_Type-I_SlicerLUT.txt
mori_region_labels = {
        0: 'Background',
        1: 'SUPERIOR_PARIETAL_LOBULE_left',
        2: 'CINGULATE_GYRUS_left',
        3: 'SUPERIOR_FRONTAL_GYRUS_left',
        4: 'MIDDLE_FRONTAL_GYRUS_left',
        5: 'INFERIOR_FRONTAL_GYRUS_left',
        6: 'PRECENTRAL_GYRUS_left',
        7: 'POSTCENTRAL_GYRUS_left',
        8: 'ANGULAR_GYRUS_left',
        9: 'PRE-CUNEUS_left',
        10: 'CUNEUS_left',
        11: 'LINGUAL_GYRUS_left',
        12: 'FUSIFORM_GYRUS_left',
        13: 'PARAHIPPOCAMPAL_GYRUS_left',
        14: 'SUPERIOR_OCCIPITAL_GYRUS_left',
        15: 'INFERIOR_OCCIPITAL_GYRUS',
        16: 'MIDDLE_OCCIPITAL_GYRUS',
        17: 'ENTORHINAL_AREA',
        18: 'SUPERIOR_TEMPORAL_GYRUS',
        19: 'INFERIOR_TEMPORAL_GYRUS',
        20: 'MIDDLE_TEMPORAL_GYRUS',
        21: 'LATERAL_FRONTO-ORBITAL_GYRUS',
        22: 'MIDDLE_FRONTO-ORBITAL_GYRUS',
        23: 'SUPRAMARGINAL_GYRUS',
        24: 'GYRUS_RECTUS',
        25: 'INSULAR',
        26: 'AMYGDALA',
        27: 'HIPPOCAMPUS',
        28: 'CEREBELLUM',
        29: 'Corticospinal_tract_left',
        30: 'Inferior_cerebellar_peduncle_left',
        31: 'Medial_lemniscus_left',
        32: 'Superior_cerebellar_peduncle_left',
        33: 'Cerebral_peduncle_left',
        34: 'Anterior_limb_of_internal_capsule_left',
        35: 'Posterior_limb_of_internal_capsule_left',
        36: 'Posterior_thalamic_radiation_left',
        37: 'Anterior_corona_radiata_left',
        38: 'Superior_corona_radiata_left',
        39: 'Posterior_corona_radiata_left',
        40: 'Cingulum_(cingulate_gyrus)_left',
        41: 'Cingulum_(hippocampus)_left',
        42: 'Fornix(cres)_Stria_terminalis_left',
        43: 'Superior_longitudinal_fasciculus_left',
        44: 'Superior_fronto-occipital_fasciculus_left',
        45: 'Inferior_fronto-occipital_fasciculus_left',
        46: 'Sagittal_stratum_left',
        47: 'External_capsule_left',
        48: 'Uncinate_fasciculus_left',
        49: 'Pontine_crossing_tract_left',
        50: 'Middle_cerebellar_peduncle_left',
        51: 'Fornix_(column_and_body)_left',
        52: 'Genu_of_corpus_callosum_left',
        53: 'Body_of_corpus_callosum_left',
        54: 'Splenium_of_corpus_callosum_left',
        55: 'Retrolenticular_part_of_internal_capsule_left',
        56: 'Red_Nucleus_left',
        57: 'Substancia_Nigra_left',
        58: 'Tapatum_left',
        59: 'CAUDATE_NUCLEUS_left',
        60: 'PUTAMEN_left',
        61: 'THALAMUS_left',
        62: 'GLOBUS_PALLIDUS_left',
        63: 'MIDBRAIN_left',
        64: 'PONS_left',
        65: 'MEDULLA_left',
        66: 'SUPERIOR_PARIETAL_WM_left',
        67: 'Cingulum_WM_left',
        68: 'SUPERIOR_FRONTAL_WM_left',
        69: 'MIDDLE_FRONTAL_WM_left',
        70: 'INFERIOR_FRONTAL_WM_left',
        71: 'PRECENTRAL_WM_left',
        72: 'POSTCENTRAL_WM_left',
        73: 'ANGULAR_WM_left',
        74: 'PRE-CUNEUS_WM_left',
        75: 'CUNEUS_WM_left',
        76: 'LINGUAL_WM_left',
        77: 'FUSIFORM_WM_left',
        78: 'SUPERIOR_OCCIPITAL_WM_left',
        79: 'INFERIOR_OCCIPITAL_WM_left',
        80: 'MIDDLE_OCCIPITAL_WM_left',
        81: 'SUPERIOR_TEMPORAL_WM_left',
        82: 'INFERIOR_TEMPORAL_WM_left',
        83: 'MIDDLE_TEMPORAL_WM_left',
        84: 'LATERAL_FRONTO-ORBITAL_WM_left',
        85: 'MIDDLE_FRONTO-ORBITAL_WM_left',
        86: 'SUPRAMARGINAL_WM_left',
        87: 'RECTUS_WM_left',
        88: 'CEREBELLUM_WM_left',
        89: 'SUPERIOR_PARIETAL_LOBULE_right',
        90: 'CINGULATE_GYRUS_right',
        91: 'SUPERIOR_FRONTAL_GYRUS_right',
        92: 'MIDDLE_FRONTAL_GYRUS_right',
        93: 'INFERIOR_FRONTAL_GYRUS_right',
        94: 'PRECENTRAL_GYRUS_right',
        95: 'POSTCENTRAL_GYRUS_right',
        96: 'ANGULAR_GYRUS_right',
        97: 'PRE-CUNEUS_right',
        98: 'CUNEUS_right',
        99: 'LINGUAL_GYRUS_right',
        100: 'FUSIFORM_GYRUS_right',
        101: 'PARAHIPPOCAMPAL_GYRUS_right',
        102: 'SUPERIOR_OCCIPITAL_GYRUS_right',
        103: 'INFERIOR_OCCIPITAL_GYRUS_right',
        104: 'MIDDLE_OCCIPITAL_GYRUS_right',
        105: 'ENTORHINAL_AREA_right',
        106: 'SUPERIOR_TEMPORAL_GYRUS_right',
        107: 'INFERIOR_TEMPORAL_GYRUS_right',
        108: 'MIDDLE_TEMPORAL_GYRUS_right',
        109: 'LATERAL_FRONTO-ORBITAL_GYRUS_right',
        110: 'MIDDLE_FRONTO-ORBITAL_GYRUS_right',
        111: 'SUPRAMARGINAL_GYRUS_right',
        112: 'GYRUS_RECTUS_right',
        113: 'INSULAR_right',
        114: 'AMYGDALA_right',
        115: 'HIPPOCAMPUS_right',
        116: 'CEREBELLUM_right',
        117: 'Corticospinal_tract_right',
        118: 'Inferior_cerebellar_peduncle_right',
        119: 'Medial_lemniscus_right',
        120: 'Superior_cerebellar_peduncle_right',
        121: 'Cerebral_peduncle_right',
        122: 'Anterior_limb_of_internal_capsule_right',
        123: 'Posterior_limb_of_internal_capsule_right',
        124: 'Posterior_thalamic_radiation_right',
        125: 'Anterior_corona_radiata_right',
        126: 'Superior_corona_radiata_right',
        127: 'Posterior_corona_radiata_right',
        128: 'Cingulum_(cingulate_gyrus)_right',
        129: 'Cingulum_(hippocampus)_right',
        130: 'Fornix(cres)_Stria_terminalis_right',
        131: 'Superior_longitudinal_fasciculus_right',
        132: 'Superior_fronto-occipital_fasciculus_right',
        133: 'Inferior_fronto-occipital_fasciculus_right',
        134: 'Sagittal_stratum_right',
        135: 'External_capsule_right',
        136: 'Uncinate_fasciculus_right',
        137: 'Pontine_crossing_tract_right',
        138: 'Middle_cerebellar_peduncle_right',
        139: 'Fornix_right',
        140: 'Genu_of_corpus_callosum_right',
        141: 'Body_of_corpus_callosum_right',
        142: 'Splenium_of_corpus_callosum_right',
        143: 'Retrolenticular_part_of_internal_capsule_right',
        144: 'Red_Nucleus_right',
        145: 'Substancia_Nigra_right',
        146: 'Tapatum_right',
        147: 'CAUDATE_NUCLEUS_right',
        148: 'PUTAMEN_right',
        149: 'THALAMUS_right',
        150: 'GLOBUS_PALLIDUS_right',
        151: 'MIDBRAIN_right',
        152: 'PONS_right',
        153: 'MEDULLA_right',
        154: 'SUPERIOR_PARIETAL_WM_right',
        155: 'Cingulum_WM_right',
        156: 'SUPERIOR_FRONTAL_WM_right',
        157: 'MIDDLE_FRONTAL_WM_right',
        158: 'INFERIOR_FRONTAL_WM_right',
        159: 'PRECENTRAL_WM_right',
        160: 'POSTCENTRAL_WM_right',
        161: 'ANGULAR_WM_right',
        162: 'PRE-CUNEUS_WM_right',
        163: 'CUNEUS_WM_right',
        164: 'LINGUAL_WM_right',
        165: 'FUSIFORM_WM_right',
        166: 'SUPERIOR_OCCIPITAL_WM_right',
        167: 'INFERIOR_OCCIPITAL_WM_right',
        168: 'MIDDLE_OCCIPITAL_WM_right',
        169: 'SUPERIOR_TEMPORAL_WM_right',
        170: 'INFERIOR_TEMPORAL_WM_right',
        171: 'MIDDLE_TEMPORAL_WM_right',
        172: 'LATERAL_FRONTO-ORBITAL_WM_right',
        173: 'MIDDLE_FRONTO-ORBITAL_WM_right',
        174: 'SUPRAMARGINAL_WM_right',
        175: 'RECTUS_WM_right',
        176: 'CEREBELLUM_WM_right',
        }

# from fsl atlas label file JHU-tracts.xml
JHUtracts_region_labels = {
        0: 'Background',
        1: 'Anterior thalamic radiation L',
        2: 'Anterior thalamic radiation R',
        3: 'Corticospinal tract L',
        4: 'Corticospinal tract R',
        5: 'Cingulum (cingulate gyrus) L',
        6: 'Cingulum (cingulate gyrus) R',
        7: 'Cingulum (hippocampus) L',
        8: 'Cingulum (hippocampus) R',
        9: 'Forceps major',
        10: 'Forceps minor',
        11: 'Inferior fronto-occipital fasciculus L',
        12: 'Inferior fronto-occipital fasciculus R',
        13: 'Inferior longitudinal fasciculus L',
        14: 'Inferior longitudinal fasciculus R',
        15: 'Superior longitudinal fasciculus L',
        16: 'Superior longitudinal fasciculus R',
        17: 'Uncinate fasciculus L',
        18: 'Uncinate fasciculus R',
        19: 'Superior longitudinal fasciculus (temporal part) L',
        20: 'Superior longitudinal fasciculus (temporal part) R',
        }
