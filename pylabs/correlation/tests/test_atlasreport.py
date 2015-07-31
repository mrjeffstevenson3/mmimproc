from unittest import TestCase
from mock import patch, call, Mock, MagicMock
import numpy
from numpy.testing import assert_array_equal


class AtlasReportTests(TestCase):

    def setUp(self):
        self.niprov = None
        self.nibabel = None
        self.opts = Mock()
        self.bins = Mock()
        self.table = MockTable()
        self.img = Mock()
        self.img.shape = (1,1,0)
        self.img.get_data.return_value = self.array3d([])
        self.img2 = Mock()
        self.img2.shape = (1,1,0)
        self.img2.get_data.return_value = self.array3d([])
        self.inputImages = [self.img]
        self.atlasimg = Mock()
        self.atlasimg.shape = (1,1,0)
        self.atlasimg.get_data.return_value = []

    def atlasreport(self, *args, **kwargs):
        from pylabs.correlation.atlas import report
        with patch('pylabs.correlation.randpar.niprov') as self.niprov:
            with patch('pylabs.correlation.atlas.nibabel') as self.nibabel:
                self.nibabel.load.side_effect = (lambda f: 
                    self.atlasimg if 'atlas' in f else self.inputImages.pop(0))
                return report(*args, table=self.table, **kwargs)

    def test_Raises_error_if_atlas_image_different_size(self):
        self.img.shape = (1,2,3)
        self.atlasimg.shape = (3,2,1)
        with self.assertRaisesRegexp(ValueError, 'dimensions'):
            self.atlasreport(['stats.img'],'atlas.img')

    def test_Counts_number_of_superthreshold_voxels_per_region(self):
        self.img.get_data.return_value = self.array3d(
            [.3, .4, .5, .96, .6, .97, .998])
        self.atlasimg.get_data.return_value = self.array3d(
            [ 1,  1,  3,   3,  2,   2,  2])
        self.atlasreport(['stats'],'atlas')
        assert_array_equal(self.table.data, numpy.array([[0], [2], [1]]))

    def test_Threshold_can_be_adapted(self):
        self.img.get_data.return_value = self.array3d(
            [.3, .4, .5, .96, .6, .97, .998])
        self.atlasimg.get_data.return_value = self.array3d(
            [ 1,  1,  3,   3,  2,   2,  2])
        self.atlasreport(['stats'],'atlas',threshold=.98)
        assert_array_equal(self.table.data, numpy.array([[0], [1], [0]]))

    def test_If_given_regionnames_passes_them_to_table(self):
        self.atlasreport(['stats'],'atlas')
        assert not self.table.setRowHeadersCalled
        self.inputImages = [self.img] #reset 
        self.atlasreport(['stats'],'atlas',regionnames=['a','b','c'])
        self.assertEqual(self.table.rowHeaders, ['a','b','c'])

    def test_Publishes_table_after_setting_attributes(self):
        self.atlasreport(['stats'],'atlas',regionnames=['a'])
        self.assertEqual(self.table.calls, 
            ['setData', 'setRowHeaders', 'setColumnHeaders', 'publish'])

    def test_Takes_multiple_images_and_makes_them_into_cols(self):
        self.inputImages = [self.img, self.img2]
        self.img.get_data.return_value = self.array3d(
            [.3, .4, .5, .96, .6, .97])
        self.img2.get_data.return_value = self.array3d(
            [.96, .97, .5, .67, .99, .2])
        self.atlasimg.get_data.return_value = self.array3d(
            [ 1,  1,  2,   2,  3,   3])
        self.atlasreport(['s1','s2'], 'atlas', regionnames=['a'])
        assert_array_equal(self.table.data, numpy.array([[0, 2], [1, 0], [1, 1]]))

    def test_Can_sepcify_name_segment_to_use_as_column_header(self):
        self.inputImages = [self.img, self.img2]
        self.atlasreport(['a_b_c','d_e_f'], 'atlas', relevantImageFilenameSegment=1)
        self.assertEqual(self.table.colHeaders, ['b','e'])
   
    def array3d(self, vector):
        return numpy.array([[vector]])

class MockTable(object):

    def __init__(self):
        self.setDataCalled = False
        self.setRowHeadersCalled = False
        self.calls = []
        self.colHeaders = None
        self.rowHeaders = None

    def setData(self, data):
        self.data = data
        self.setDataCalled = True
        self.calls.append('setData')

    def setRowHeaders(self, headers):
        self.rowHeaders = headers
        self.setRowHeadersCalled = True
        self.calls.append('setRowHeaders')

    def setColumnHeaders(self, headers):
        self.colHeaders = headers
        self.calls.append('setColumnHeaders')

    def publish(self):
        self.calls.append('publish')





