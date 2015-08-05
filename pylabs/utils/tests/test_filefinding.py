from unittest import TestCase
from mock import patch, call, Mock, MagicMock


class FilefinderTests(TestCase):

    def test_corep_from_randpar_base_result(self):
        from pylabs.utils.files import deconstructRandparFiles
        f1 =('randpar_n500_WM_mod_merg_s4_c4b21s15d_'
                'SOPT41totalcorrectmax3_tfce_corrp_tstat2.nii.gz')
        f2 =('randpar_n500_GM_foo_mod_merg_s4_c4b93s15d_'
                'Blablascore_tfce_corrp_tstat2.nii.gz')
        outimgs, outmats = deconstructRandparFiles([f1, f2])
        self.assertEqual(outimgs, ['WM_mod_merg_s4.nii.gz',
                                    'GM_foo_mod_merg_s4.nii.gz'])
        self.assertEqual(outmats, ['c4b21s15d_SOPT41totalcorrectmax3.mat',
                                    'c4b93s15d_Blablascore.mat'])

