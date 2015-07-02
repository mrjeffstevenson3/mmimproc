from unittest import TestCase
from pylabs.utils import MockShell
from pylabs.correlation.randpar import multirandpar


class MultiRandParTests(TestCase):

    def setUp(self):
        self.shell = MockShell()

    def test_runs_randpar_on_each_image(self):
        imgs = ['one.img','two.img']
        multirandpar(imgs, shell=self.shell)
        self.shell.assert_ran_command_matching('randomize_parallel *-i '+imgs[0])
        self.shell.assert_ran_command_matching('randomize_parallel *-i '+imgs[1])



