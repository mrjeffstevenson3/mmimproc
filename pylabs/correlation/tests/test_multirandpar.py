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
            'randomize_parallel *-i one.img *-o randpar_50_one/*')

    def test_creates_dirs(self):
        imgs = ['one.img','two.img']
        multirandpar(imgs, ['x.mat','y.mat'], 'd.con', shell=self.shell)
        self.shell.assert_ran_command_matching(
            'mkdir -p randpar_50_one/x')
        self.shell.assert_ran_command_matching(
            'mkdir -p randpar_50_two/y')

    def test_output_path_reflects_files_and_options(self):
        imgs = ['/dir_sth/else/one_foo.img']
        mats = ['/matfiles/abc_bar.mat']
        multirandpar(imgs, mats, 'mydesign.con', niterations=77, shell=self.shell)
        self.shell.assert_ran_command_matching(
            'randomize_parallel * -o /dir_sth/else/randpar_77_one_foo/abc_bar*')

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
        imgs = ['/dir_sth/typeA_bla.img','/dir_sth/typeB_bla.img']
        multirandpar(imgs, ['a.mat'], 'd.con', shell=self.shell)
        self.shell.assert_ran_command_matching(
            'randomize_parallel* -m /dir_sth/typeA_mask *')
        self.shell.assert_ran_command_matching(
            'randomize_parallel* -m /dir_sth/typeB_mask *')



