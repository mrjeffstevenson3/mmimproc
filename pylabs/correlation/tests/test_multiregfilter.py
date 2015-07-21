from unittest import TestCase
from pylabs.utils import MockShell
from mock import patch, call, Mock
import fnmatch


class MultiRegfilterTests(TestCase):

    def setUp(self):
        self.shell = MockShell()
        self.niprov = None
        self.opts = Mock()

    def multiregfilt(self, *args, **kwargs):
        import pylabs.correlation.regfilt
        with patch('pylabs.correlation.regfilt.niprov') as self.niprov:
            return pylabs.correlation.regfilt.multiregfilt(
                *args, shell=self.shell, opts=self.opts, **kwargs)

    def assert_recorded_command_matching(self, needle, **kwargs):
        allCalls = self.niprov.record.call_args_list
        for C in allCalls:
            if fnmatch.fnmatch(C[0][0], needle) and C[1] == kwargs:
                break
        else:
            strcalls = '\n'.join([str(c) for c in allCalls])
            msg = ('No matching recorded commands. Looking for:\n{0}\n'
                    'All calls:\n'+strcalls).format(call(needle, **kwargs))
            raise AssertionError(msg)

    def test_runs_filter_on_each_image(self):
        imgs = ['one.img','two.img']
        self.multiregfilt(imgs, 'x.mat')
        self.assert_recorded_command_matching(
            'fsl_regfilt *-i one.img* -d x.mat*', opts=self.opts)
        self.assert_recorded_command_matching(
            'fsl_regfilt *-i two.img* -d x.mat*', opts=self.opts)

    def test_names_output_appropriately(self):
        imgs = ['one.img']
        self.multiregfilt(imgs, 'xyz.mat')
        self.assert_recorded_command_matching(
            'fsl_regfilt *-o one_filt_xyz.img', opts=self.opts)

    def test_returns_output_images(self):
        from pylabs.correlation.regfilt import multiregfilt
        imgs = ['one.img','two.img']
        output = self.multiregfilt(imgs, 'xyz.mat')
        self.assertEqual(output, ['one_filt_xyz.img','two_filt_xyz.img'])

    def test_outdir_formatting_matfile_path_and_filenames_multiple_dots(self):
        from pylabs.correlation.regfilt import multiregfilt
        imgs = ['one.img.x','two.img.x']
        output = self.multiregfilt(imgs, 'matfiles/xyz.mat')
        self.assertEqual(output, ['one_filt_xyz.img.x','two_filt_xyz.img.x'])


