from unittest import TestCase
from pylabs.utils import MockShell
from mock import patch, call, Mock, MagicMock
import fnmatch


class MultiRandParTests(TestCase):

    def setUp(self):
        self.shell = MockShell()
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
#, transient=True
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

    def test_runs_randpar_on_each_image_with_separate_output_dir(self):
        imgs = ['one.img','two.img']
        self.multirandpar(imgs, ['x.mat'], 'd.con')
        self.assert_recorded_command_matching(
            'randparbin *-i one.img*', transient=True, opts=self.opts)
        self.assert_recorded_command_matching(
            'randparbin *-i two.img*', transient=True, opts=self.opts)

    def test_uses_separate_output_dir_per_image(self):
        imgs = ['one.img','two.img']
        self.multirandpar(imgs, ['x.mat'], 'd.con')
        self.assert_recorded_command_matching(
            'randparbin *-i one.img *-o randpar_50_one/*', transient=True, opts=self.opts)

    def test_creates_dirs(self):
        imgs = ['one.img','two.img']
        self.multirandpar(imgs, ['x.mat','y.mat'], 'd.con')
        self.shell.assert_ran_command_matching(
            'mkdir -p randpar_50_one')
        self.shell.assert_ran_command_matching(
            'mkdir -p randpar_50_two')

    def test_output_path_reflects_files_and_options(self):
        imgs = ['/dir_sth/else/one_foo.img']
        mats = ['/matfiles/abc_bar.mat']
        self.multirandpar(imgs, mats, 'mydesign.con', niterations=77)
        self.assert_recorded_command_matching(
            'randparbin *'
            ' -o /dir_sth/else/randpar_77_one_foo/randpar_77_abc_bar_one_foo.img*', 
            transient=True, opts=self.opts)

    def test_runs_for_each_image_and_variable_combination(self):
        imgs = ['one.img','two.img']
        mats = ['a.mat','b.mat']
        self.multirandpar(imgs, mats, 'd.con')
        self.assert_recorded_command_matching(
            'randparbin *-i one.img *-d a.mat*', transient=True, opts=self.opts)
        self.assert_recorded_command_matching(
            'randparbin *-i one.img *-d b.mat*', transient=True, opts=self.opts)
        self.assert_recorded_command_matching(
            'randparbin *-i two.img *-d a.mat*', transient=True, opts=self.opts)
        self.assert_recorded_command_matching(
            'randparbin *-i two.img *-d b.mat*', transient=True, opts=self.opts)

    def test_specifies_number_of_iterations(self):
        imgs = ['one.img']
        mats = ['a.mat']
        self.multirandpar(imgs, mats, 'd.con', niterations=99)
        self.assert_recorded_command_matching(
            'randparbin * -n 99*', transient=True, opts=self.opts)

    def test_Looks_for_maskfile_based_on_image_prefix(self):
        imgs = ['/dir_sth/tA_bla.nii.gz','/dir_sth/tB_bla.img']
        self.multirandpar(imgs, ['a.mat'], 'd.con')
        self.assert_recorded_command_matching(
            'randparbin* -m /dir_sth/tA_mask.nii.gz *', transient=True, opts=self.opts)
        self.assert_recorded_command_matching(
            'randparbin* -m /dir_sth/tB_mask.img *', transient=True, opts=self.opts)

    def test_If_masks_dict_passed_uses_this(self):
        imgs = ['one.img','two.img']
        mymasks = {'one.img':'m1.img','two.img':'m2.img'}
        self.multirandpar(imgs, ['a.mat'], 'd.con', masks=mymasks)
        self.assert_recorded_command_matching(
            'randparbin*-i one.img *-m m1.img *', transient=True, opts=self.opts)
        self.assert_recorded_command_matching(
            'randparbin*-i two.img *-m m2.img *', transient=True, opts=self.opts)

    def test_returns_outfiles(self):
        imgs = ['one.img','two.img']
        out = self.multirandpar(imgs, ['x.mat','y.mat'], 'd.con')
        self.assertEqual(out,
            ['randpar_50_one/randpar_50_x_one.img',
                'randpar_50_one/randpar_50_y_one.img',
                'randpar_50_two/randpar_50_x_two.img',
                'randpar_50_two/randpar_50_y_two.img'])

    def test_Uses_binaries_object_to_pick_executable(self):
        self.bins.randpar = 'abracadabra'
        self.multirandpar(['bla.img'], ['a.mat'], 'd.con')
        self.assert_recorded_command_matching(
            'abracadabra *', transient=True, opts=self.opts)

    def test_Wraps_command_in_workingdir_context_manager(self):
        from pylabs.correlation.randpar import multirandpar
        workdir = '/foo/bar/bla'
        with patch('pylabs.correlation.randpar.niprov') as self.niprov:
            ctx = MockWorkingContext(self.niprov.record)
            self.context.return_value = ctx
            multirandpar(['bla.img'], ['a.mat'], 'd.con', workdir=workdir, 
                shell=self.shell, opts=self.opts, binaries=self.bins, 
                context=self.context)
        self.assertTrue(ctx.entered, 'Did not open context.')
        self.context.assert_called_with(workdir)

    def test_TFCE_flag_dependent_on_TBSS_flag(self):
        self.multirandpar(['one.img'], ['a.mat'], 'd.con')
        self.assert_recorded_command_matching(
            'randparbin * -T *', transient=True, opts=self.opts)
        self.multirandpar(['one.img'], ['a.mat'], 'd.con', tbss=True)
        self.assert_recorded_command_matching(
            'randparbin * --T2 *', transient=True, opts=self.opts)

class MockWorkingContext(object):

    def __init__(self, inner):
        self.encapsulated = inner
        self.entered = False

    def __enter__(self):
        self.entered = True
        assert not self.encapsulated.called, (
            "Inner object called before context activated")

    def __exit__(self,a ,b ,c):
        assert self.encapsulated.called, (
            "Inner object not called while context active")



