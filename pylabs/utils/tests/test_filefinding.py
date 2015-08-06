import unittest
from unittest import TestCase
from mock import patch, call, Mock, MagicMock


class FilefinderTests(TestCase):

    def test_corep_from_randpar_base_result(self):
        from pylabs.utils.files import deconstructRandparFiles
        f1 =('randpar_n500_WM_mod_merg_s4_c4b21s15d_'
                'SOPT41totalcorrectmax3_tfce_corrp_tstat2.nii.gz')
        f2 =('randpar_n500_GM_foo_mod_merg_s4_c4b93s15d_'
                'Blablascore_tfce_corrp_tstat2.nii.gz')
        out = deconstructRandparFiles([f1, f2])
        self.assertEqual(out, {'WM_mod_merg_s4.nii.gz':
            ['c4b21s15d_SOPT41totalcorrectmax3.mat'],
            'GM_foo_mod_merg_s4.nii.gz':
            ['c4b93s15d_Blablascore.mat']})


    def test_Gets_rid_of_path(self):
        from pylabs.utils.files import deconstructRandparFiles
        f1 =('bla/d_i/randpar_n500_WM_mod_merg_s4_c4b21s15d_'
                'SOPT41totalcorrectmax3_tfce_corrp_tstat2.nii.gz')
        f2 =('/foo/b_a_r/randpar_n500_GM_foo_mod_merg_s4_c4b93s15d_'
                'Blablascore_tfce_corrp_tstat2.nii.gz')
        out = deconstructRandparFiles([f1, f2])
        self.assertEqual(out, {'WM_mod_merg_s4.nii.gz':
            ['c4b21s15d_SOPT41totalcorrectmax3.mat'],
            'GM_foo_mod_merg_s4.nii.gz':
            ['c4b93s15d_Blablascore.mat']})

    def test_Multiple_mats_listed_under_one_img_key(self):
        from pylabs.utils.files import deconstructRandparFiles
        f1 =('randpar_n500_WM_mod_merg_s4_c4b21s15d_'
                'SOPT41totalcorrectmax3_tfce_corrp_tstat2.nii.gz')
        f2 =('randpar_n500_WM_mod_merg_s4_c4b99s15d_'
                'blablascore_tfce_corrp_tstat2.nii.gz')
        out = deconstructRandparFiles([f1, f2])
        self.assertEqual(out, {'WM_mod_merg_s4.nii.gz':
            ['c4b21s15d_SOPT41totalcorrectmax3.mat',
            'c4b99s15d_blablascore.mat']})


    def test_If_dirs_specified_joins_them(self):
        from pylabs.utils.files import deconstructRandparFiles
        f1 =('randpar_n500_WM_mod_merg_s4_c4b21s15d_'
                'SOPT41totalcorrectmax3_tfce_corrp_tstat2.nii.gz')
        out = deconstructRandparFiles([f1], 
            matdir='/mat/bla', imgdir='/foo/img/')
        self.assertEqual(out, {'/foo/img/WM_mod_merg_s4.nii.gz':
            ['/mat/bla/c4b21s15d_SOPT41totalcorrectmax3.mat']})

if __name__ == '__main__':
    unittest.main()


