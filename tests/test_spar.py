import unittest
from mock import patch, call, Mock, MagicMock
from os.path import join
import numpy
from numpy.testing import assert_array_equal, assert_array_almost_equal

#Notes:
#Secsi has multiple slices
#Gaba has multiple dynamics (unsuppressed and suppressed)x160 measurements
#Glu and short TE glu are the simple ones.
#All have water reference and actual spectrums

files = [
'TADPOLE_998D_WIP_3SL_SECSI_TE16_SENSE_8_1_raw_act.SPAR',
'TADPOLE_998D_WIP_3SL_SECSI_TE16_SENSE_8_1_raw_ref.SPAR',
'TADPOLE_998D_WIP_GABAMM_TE80_7_2_raw_act.SPAR',
'TADPOLE_998D_WIP_GABAMM_TE80_7_2_raw_ref.SPAR',
'TADPOLE_998D_WIP_PRESS_TE30_GLU_5_2_raw_act.SPAR',
'TADPOLE_998D_WIP_PRESS_TE30_GLU_5_2_raw_ref.SPAR',
'TADPOLE_998D_WIP_PRESS_TE80_GLU_6_2_raw_act.SPAR',
'TADPOLE_998D_WIP_PRESS_TE80_GLU_6_2_raw_ref.SPAR',
]


class SparTests(unittest.TestCase):

    def setUp(self):
        pass

    def test_Can_load_all_SPAR_files(self):
        from pylabs.io.spar import load
        for fname in files:
            fpath = join('data/testdata/spar',fname)
            img = load(fpath)

    def test_Loaded_SPAR_file_exposes_header_info(self):
        from pylabs.io.spar import load
        fpath = join('data/testdata/spar',files[5])
        hdrDict = load(fpath)
        print(hdrDict.keys())
        self.assertEqual(hdrDict['scan_id'], 'PRESS_TE30_GLU')
        self.assertEqual(hdrDict['samples'], 2048)
        self.assertEqual(hdrDict['ap_off_center'], -26.76418495)

if __name__ == '__main__':
    unittest.main()


