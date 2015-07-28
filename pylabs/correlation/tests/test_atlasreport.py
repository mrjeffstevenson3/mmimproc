from unittest import TestCase
from mock import patch, call, Mock, MagicMock
import numpy


class AtlasReportTests(TestCase):

    def setUp(self):
        self.niprov = None
        self.nibabel = None
        self.opts = Mock()
        self.bins = Mock()
        self.table = Mock()
        self.img = Mock()
        self.img.shape = (1,1,0)
        self.img.get_data.return_value = []
        self.atlasimg = Mock()
        self.atlasimg.shape = (1,1,0)
        self.atlasimg.get_data.return_value = []

    def atlasreport(self, *args, **kwargs):
        from pylabs.correlation.atlas import report
        with patch('pylabs.correlation.randpar.niprov') as self.niprov:
            with patch('pylabs.correlation.atlas.nibabel') as self.nibabel:
                self.nibabel.load.side_effect = (lambda f: 
                    self.atlasimg if 'atlas' in f else self.img)
                return report(*args, table=self.table, **kwargs)

    def test_Raises_error_if_atlas_image_different_size(self):
        self.img.shape = (1,2,3)
        self.atlasimg.shape = (3,2,1)
        with self.assertRaisesRegexp(ValueError, 'dimensions'):
            self.atlasreport('stats.img','atlas.img')

    def test_Counts_number_of_superthreshold_voxels_per_region(self):
        self.img.get_data.return_value = self.array3d(
            [.3, .4, .5, .96, .6, .97, .998])
        self.atlasimg.get_data.return_value = self.array3d(
            [ 1,  1,  3,   3,  2,   2,  2])
        self.atlasreport('stats','atlas')
        self.table.setData.assert_called_with([0, 2, 1])

    def array3d(self, vector):
        return numpy.array([[vector]])





