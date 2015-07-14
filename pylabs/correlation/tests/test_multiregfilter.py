from unittest import TestCase
from pylabs.utils import MockShell


class MultiRegfilterTests(TestCase):

    def setUp(self):
        self.shell = MockShell()

    def test_runs_filter_on_each_image(self):
        from pylabs.correlation.regfilt import multiregfilt
        imgs = ['one.img','two.img']
        multiregfilt(imgs, 'x.mat', shell=self.shell)
        self.shell.assert_ran_command_matching(
            'regfilt *-i one.img* -d x.mat*')
        self.shell.assert_ran_command_matching(
            'regfilt *-i two.img* -d x.mat*')

    def test_names_output_appropriately(self):
        from pylabs.correlation.regfilt import multiregfilt
        imgs = ['one.img']
        multiregfilt(imgs, 'xyz.mat', shell=self.shell)
        self.shell.assert_ran_command_matching(
            'regfilt *-o one_filt_xyz.img')

    def test_returns_output_images(self):
        from pylabs.correlation.regfilt import multiregfilt
        imgs = ['one.img','two.img']
        output = multiregfilt(imgs, 'xyz.mat', shell=self.shell)
        self.assertEqual(output, ['one_filt_xyz.img','two_filt_xyz.img'])

    def test_outdir_formatting_matfile_path_and_filenames_multiple_dots(self):
        from pylabs.correlation.regfilt import multiregfilt
        imgs = ['one.img.x','two.img.x']
        output = multiregfilt(imgs, 'matfiles/xyz.mat', shell=self.shell)
        self.assertEqual(output, ['one_filt_xyz.img.x','two_filt_xyz.img.x'])


