from unittest import TestCase
from pylabs.utils import MockShell
from pylabs.correlation.randpar import multirandpar


class MultiRandParTests(TestCase):

    def setUp(self):
        self.shell = MockShell()

    def test_runs_randpar_on_each_image_with_separate_output_dir(self):
        imgs = ['one.img','two.img']
        multirandpar(imgs, shell=self.shell)
        self.shell.assert_ran_command_matching(
            'randomize_parallel *-i one.img*')
        self.shell.assert_ran_command_matching(
            'randomize_parallel *-i two.img*')

    def test_uses_separate_output_dir_per_image(self):
        imgs = ['one.img','two.img']
        multirandpar(imgs, shell=self.shell)
        self.shell.assert_ran_command_matching(
            'randomize_parallel *-i one.img *-o randpar_one*/*')

#one output dir per image





