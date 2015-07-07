from unittest import TestCase
from pylabs.utils import MockShell
from pylabs.correlation.randpar import multirandpar


class MultiRandParTests(TestCase):

    def setUp(self):
        self.shell = MockShell()

    def test_runs_randpar_on_each_image_with_separate_output_dir(self):
        imgs = ['one.img','two.img']
        multirandpar(imgs, ['x.mat'], 'd.con', shell=self.shell)
        self.shell.assert_ran_command_matching(
            'randomize_parallel *-i one.img*')
        self.shell.assert_ran_command_matching(
            'randomize_parallel *-i two.img*')

    def test_uses_separate_output_dir_per_image(self):
        imgs = ['one.img','two.img']
        multirandpar(imgs, ['x.mat'], 'd.con', shell=self.shell)
        self.shell.assert_ran_command_matching(
            'randomize_parallel *-i one.img *-o randpar_one*/*')

    def test_runs_for_each_image_and_variable_combination(self):
        imgs = ['one.img','two.img']
        mats = ['a.mat','b.mat']
        multirandpar(imgs, mats, 'd.con', shell=self.shell)
        self.shell.assert_ran_command_matching(
            'randomize_parallel *-i one.img *-d a.mat*')
        self.shell.assert_ran_command_matching(
            'randomize_parallel *-i one.img *-d b.mat*')
        self.shell.assert_ran_command_matching(
            'randomize_parallel *-i two.img *-d a.mat*')
        self.shell.assert_ran_command_matching(
            'randomize_parallel *-i two.img *-d b.mat*')

    def test_specifies_number_of_iterations(self):
        imgs = ['one.img']
        mats = ['a.mat']
        multirandpar(imgs, mats, 'd.con', niterations=99, shell=self.shell)
        self.shell.assert_ran_command_matching(
            'randomize_parallel * -n 99*')

    def test_Looks_for_maskfile_based_on_image_prefix(self):
        imgs = ['typeA_bla.img','typeB_bla.img']
        multirandpar(imgs, ['a.mat'], 'd.con', shell=self.shell)
        self.shell.assert_ran_command_matching(
            'randomize_parallel *-i typeA_bla.img * -m typeA_mask *')
        self.shell.assert_ran_command_matching(
            'randomize_parallel *-i typeB_bla.img * -m typeB_mask *')






