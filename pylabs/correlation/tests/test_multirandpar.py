from unittest import TestCase
from pylabs.utils import MockShell
from mock import patch, call
import fnmatch



class MultiRandParTests(TestCase):

    def setUp(self):
        self.shell = MockShell()
        self.niprov = None

    def multirandpar(self, *args, **kwargs):
        from pylabs.correlation.randpar import multirandpar
        with patch('pylabs.correlation.randpar.niprov') as self.niprov:
            multirandpar(*args, shell=self.shell, **kwargs)

    def assert_recorded_command_matching(self, needle):
        self.assertIn(call(needle), self.niprov.record.call_args_list)

    def test_runs_randpar_on_each_image_with_separate_output_dir(self):
        imgs = ['one.img','two.img']
        self.multirandpar(imgs, ['x.mat'], 'd.con')
        self.assert_recorded_command_matching(
            'randomize_parallel *-i one.img*')
        self.assert_recorded_command_matching(
            'randomize_parallel *-i two.img*')

    def test_uses_separate_output_dir_per_image(self):
        imgs = ['one.img','two.img']
        self.multirandpar(imgs, ['x.mat'], 'd.con')
        self.assert_recorded_command_matching(
            'randomize_parallel *-i one.img *-o randpar_50_one/*')

    def test_creates_dirs(self):
        imgs = ['one.img','two.img']
        self.multirandpar(imgs, ['x.mat','y.mat'], 'd.con')
        self.assert_recorded_command_matching(
            'mkdir -p randpar_50_one/x')
        self.assert_recorded_command_matching(
            'mkdir -p randpar_50_two/y')

    def test_output_path_reflects_files_and_options(self):
        imgs = ['/dir_sth/else/one_foo.img']
        mats = ['/matfiles/abc_bar.mat']
        self.multirandpar(imgs, mats, 'mydesign.con', niterations=77)
        self.assert_recorded_command_matching(
            'randomize_parallel * -o /dir_sth/else/randpar_77_one_foo/abc_bar*')

    def test_runs_for_each_image_and_variable_combination(self):
        imgs = ['one.img','two.img']
        mats = ['a.mat','b.mat']
        self.multirandpar(imgs, mats, 'd.con')
        self.assert_recorded_command_matching(
            'randomize_parallel *-i one.img *-d a.mat*')
        self.assert_recorded_command_matching(
            'randomize_parallel *-i one.img *-d b.mat*')
        self.assert_recorded_command_matching(
            'randomize_parallel *-i two.img *-d a.mat*')
        self.assert_recorded_command_matching(
            'randomize_parallel *-i two.img *-d b.mat*')

    def test_specifies_number_of_iterations(self):
        imgs = ['one.img']
        mats = ['a.mat']
        self.multirandpar(imgs, mats, 'd.con', niterations=99)
        self.assert_recorded_command_matching(
            'randomize_parallel * -n 99*')

    def test_Looks_for_maskfile_based_on_image_prefix(self):
        imgs = ['/dir_sth/typeA_bla.img','/dir_sth/typeB_bla.img']
        self.multirandpar(imgs, ['a.mat'], 'd.con')
        self.assert_recorded_command_matching(
            'randomize_parallel* -m /dir_sth/typeA_mask *')
        self.assert_recorded_command_matching(
            'randomize_parallel* -m /dir_sth/typeB_mask *')



