from unittest import TestCase
from mock import patch, call, Mock, MagicMock


class AtlasLabelsTests(TestCase):

    def setUp(self):
        pass

    def test_finds_labelsfile(self):
        from mmimproc.correlation.atlas import atlaslabels
        os = Mock()
        atlaslabels('bla.img', filesys=os)
        os.readlines.assert_called_with('data/atlaslabels/bla.img.txt')

    def test_finds_labelsfile(self):
        from mmimproc.correlation.atlas import atlaslabels
        os = Mock()
        labels = atlaslabels('bla.img', filesys=os)
        self.assertEqual(labels, os.readlines())





