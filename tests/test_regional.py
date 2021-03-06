from unittest import TestCase
from mock import patch, call, Mock, MagicMock
import numpy
from numpy.testing import assert_array_equal, assert_array_almost_equal


class RegionalTests(TestCase):

    def setUp(self):
        self.niprov = None
        self.nibabel = None
        self.opts = Mock()
        self.bins = Mock()
        self.img = Mock()
        self.img.shape = (1,1,0)
        self.img.get_data.return_value = self.array3d([])
        self.atlasimg = Mock()
        self.atlasimg.shape = (1,1,0)
        self.atlasimg.get_data.return_value = self.array3d([])

    def statsByRegion(self, *args, **kwargs):
        from mmimproc.regional import statsByRegion
        with patch('mmimproc.regional.nibabel') as self.nibabel:
            self.nibabel.load.side_effect = (lambda f: 
                self.atlasimg if 'atlas' in f else self.img)
            return statsByRegion(*args, **kwargs)

    def test_Raises_error_if_atlas_image_different_size(self):
        self.img.get_data.return_value = self.array3d(
            [[.3, .4],[ .5, .6], [.6, .7]])
        self.atlasimg.get_data.return_value = self.array3d(
            [[ 1,  1,  3],[3,  2,   2]])
        with self.assertRaisesRegexp(ValueError, 'dimensions'):
            self.statsByRegion(['stats.img'],'atlas.img')

    def test_If_two_volumes_assumes_complex_and_uses_first(self):
        self.img.shape = (3,2,1,2)
        self.atlasimg.shape = (3,2,1)
        self.img.get_data.return_value =  numpy.array([[[[3,30]],[[4,40]]],[[[3,30]],[[4,40]]]])
        self.atlasimg.get_data.return_value = numpy.array([[[0],[0]],[[0],[0]]])
        out = self.statsByRegion(['stats.img'],'atlas.img')
        assert_array_almost_equal(numpy.array([3.5]), out['average'])

    def test_Average(self):
        self.img.get_data.return_value = self.array3d(
            [.3, .4, .5, .6, .6, .7, .8])
        self.atlasimg.get_data.return_value = self.array3d(
            [ 1,  1,  3,   3,  2,   2,  2])
        out = self.statsByRegion(['stats.img'],'atlas.img')
        assert_array_almost_equal(numpy.array([0.35, 0.7, 0.55]), out['average'])

#    def test_Counts_number_of_superthreshold_voxels_per_region(self):
#        self.img.get_data.return_value = self.array3d(
#            [.3, .4, .5, .96, .6, .97, .998])
#        self.atlasimg.get_data.return_value = self.array3d(
#            [ 1,  1,  3,   3,  2,   2,  2])
#        self.atlasreport(['stats'],'atlas')
#        assert_array_equal(self.table.data, numpy.array([[0], [2], [1]]))

#    def test_Threshold_can_be_adapted(self):
#        self.img.get_data.return_value = self.array3d(
#            [.3, .4, .5, .96, .6, .97, .998])
#        self.atlasimg.get_data.return_value = self.array3d(
#            [ 1,  1,  3,   3,  2,   2,  2])
#        self.atlasreport(['stats'],'atlas',threshold=.98)
#        assert_array_equal(self.table.data, numpy.array([[0], [1], [0]]))

#    def test_If_given_regionnames_passes_them_to_table(self):
#        self.atlasreport(['stats'],'atlas')
#        assert not self.table.setRowHeadersCalled
#        self.inputImages = [self.img] #reset 
#        self.atlasreport(['stats'],'atlas',regionnames=['a','b','c'])
#        self.assertEqual(self.table.rowHeaders, ['a','b','c'])

#    def test_Publishes_table_after_setting_attributes(self):
#        self.atlasreport(['stats'],'atlas',regionnames=['a'])
#        self.assertEqual(self.table.calls, 
#            ['setData', 'setRowHeaders', 'setColumnHeaders', 'publish'])

#    def test_Takes_multiple_images_and_makes_them_into_cols(self):
#        self.inputImages = [self.img, self.img2]
#        self.img.get_data.return_value = self.array3d(
#            [.3, .4, .5, .96, .6, .97])
#        self.img2.get_data.return_value = self.array3d(
#            [.96, .97, .5, .67, .99, .2])
#        self.atlasimg.get_data.return_value = self.array3d(
#            [ 1,  1,  2,   2,  3,   3])
#        self.atlasreport(['s1','s2'], 'atlas', regionnames=['a'])
#        assert_array_equal(self.table.data, numpy.array([[0, 2], [1, 0], [1, 1]]))

#    def test_Can_sepcify_name_segment_to_use_as_column_header(self):
#        self.inputImages = [self.img, self.img2]
#        self.atlasreport(['a_b_c','d_e_f'], 'atlas', relevantImageFilenameSegment=1)
#        self.assertEqual(self.table.colHeaders, ['b','e'])
   
    def array3d(self, vector):
        return numpy.array([[vector]])


