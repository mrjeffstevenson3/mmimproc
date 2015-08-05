from unittest import TestCase
from mock import patch, call, Mock, MagicMock
import numpy


class FileSelectionTests(TestCase):


    def test_Select_files_with_voxels_over_threshold(self):
        from pylabs.utils.selection import select
        myfiles = ['0nobla','1yesbar', '2barno','3fooyes']
        withCriteria = lambda f: 'yes' in f
        out = select(myfiles, withCriteria)
        self.assertEqual(out, ['1yesbar','3fooyes'])
        

    def test_Select_file_with_voxels_over_threshold(self):
        from pylabs.utils.selection import withVoxelsOverThresholdOf
        img = Mock()
        img.get_data.return_value = numpy.array([.5, -1, .96, .97])
        with patch('pylabs.utils.selection.nibabel') as self.nibabel:
            self.nibabel.load.return_value = img
            self.assertFalse(withVoxelsOverThresholdOf(.99)('afile'))
            self.assertTrue(withVoxelsOverThresholdOf(.95)('afile'))
