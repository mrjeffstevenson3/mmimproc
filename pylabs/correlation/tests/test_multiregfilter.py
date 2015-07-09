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
            'regfilt *-i one.img* -d x.mat')




# fsl_regfilt -i ${afile} -d gender.mat -f "1" -o filtered_gender_and_delta_${afile}









