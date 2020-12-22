from pathlib import *
import nibabel as nib
import numpy as np
import xml.etree.ElementTree as ET
from mmimproc.utils import *
from mmimproc.correlation.atlas import mori_region_labels
from scipy.ndimage.measurements import center_of_mass as com


# useful xml print command:
# print(ET.tostring(root, encoding="ISO-8859-1", method='xml').decode('UTF-8'), end='\n')

def indent(elem, level=0):
    i = "\n" + level*"  "
    j = "\n" + (level-1)*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for subelem in elem:
            indent(subelem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = j
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = j
    return elem


def makefslatlas(atlas_fname, xmlout_fname, labelmap=mori_region_labels):
    # test if file exists
    if atlas_fname == 'mori':
        atlas_fname = moriMNIatlas
    atlas_img = nib.load(atlas_fname)
    atlas_data = np.asanyarray(atlas_img.dataobj).astype(np.int64)
    # test if dict
    lm = labelmap
    root = ET.Element('atlas', attrib={'version': '1.0'})
    h0 = ET.SubElement(root, 'header', {})
    h1 = ET.SubElement(h0, 'name', {})
    h1.text = 'Mori Whole Brain Label Atlas'
    h2 = ET.SubElement(h0, 'type', {})
    h2.text = 'Label'
    h3 = ET.SubElement(h0, 'images', {})
    h31 = ET.SubElement(h3, 'imagefile', {})
    h31.text = '/' + atlas_fname.name
    h32 = ET.SubElement(h3, 'summaryimagefile', {})
    h32.text = '/' + atlas_fname.name

    d0 = ET.SubElement(root, 'data', {})
    d1 = ET.SubElement(d0, 'label', {'index': "0", 'x': "0", 'y': "0", 'z': "0"})
    d1.text = 'Unclassified'
    for i in np.unique(atlas_data)[1:]:
        # todo: Question: can i make roi dtype to bool_, i region = True, com, then i region = False, restart loop?
        roi = np.zeros(atlas_data.shape).copy()
        roi[atlas_data == i] = True
        com_coord = tuple(map(lambda x: isinstance(x, float) and int(round(x, 0)) or x, com(roi)))
        dx = ET.SubElement(d0, 'label', {'index': str(i), 'x': str(com_coord[0]), 'y': str(com_coord[1]), 'z': str(com_coord[2])})
        dx.text = lm[i]
        print(i, "   ", com_coord)

    tree = ET.ElementTree(indent(root))

    with open(xmlout_fname, 'wb') as xf:
        tree.write(xf, encoding="ISO-8859-1", method='xml')
    return

def fsllutfromslicer(slicerlut_fname, fsl_lut_fname):
    lutdf = pd.read_csv(slicerlut_fname, sep='\s+', index_col=0,
                        names=['index', 'label name', 'red', 'green', 'blue', 'opacity'],
                        dtype={'index': str, 'label name': str, 'red': np.int32, 'green': np.int32, 'blue': np.int32,
                               'opacity': np.int32})
    lutdf['red_perc'] = lutdf['red'] / 255
    lutdf['green_perc'] = lutdf['green'] / 255
    lutdf['blue_perc'] = lutdf['blue'] / 255
    fsl_cols = ['index', 'red_perc', 'green_perc', 'blue_perc', 'label name']
    lutdf.reset_index(inplace=True)
    lutdf['index'] = lutdf['index'].astype(str)
    # todo: need to right pad index or left pad red_perc for 1-9 two spaces and 10-99 one space
    lutdf.to_csv(fsl_lut_fname, header=False, index=False, columns=fsl_cols, sep=' ', float_format='%.5f')
    return

