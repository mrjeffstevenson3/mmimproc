from unittest import TestCase
from mock import patch, call, Mock, MagicMock


class AtlasReportTests(TestCase):

    def setUp(self):
        self.niprov = None
        self.opts = Mock()
        self.bins = Mock()
        self.bins.randpar = 'randparbin'
        self.context = Mock()
        self.context.return_value = MagicMock()

    def multirandpar(self, *args, **kwargs):
        from pylabs.correlation.randpar import multirandpar
        with patch('pylabs.correlation.randpar.niprov') as self.niprov:
            return multirandpar(*args, shell=self.shell, opts=self.opts, 
                binaries=self.bins, context=self.context,  **kwargs)

    def test_Raises_error_if_atlas_image_different_size(self):
        self.img.shape = (1,2,3)
        self.atlasimg.shape = (3,2,1)
        with self.assertRaises():
            self.report('','')

    def test_Counts_number_of_superthreshold_voxels_per_region(self):
        self.fail()





