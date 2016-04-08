#!/usr/bin/env python
"""
Jasper J.F. van den Bosch <jasperb@uw.edu>
"""
import unittest
from os.path import join, abspath

files = [
'PHANTOM_QT1_SLU_20151230.ExamCard',
'SR_ADULT_007.ExamCard',
]


class ExamCardTests(unittest.TestCase):

    def setUp(self):
        pass

    def test_Can_load_all_SPAR_files(self):
        from pylabs.io.examcard import load
        for fname in files:
            fpath = abspath(join('data/testdata/examcard',fname))
            img = load(fpath)

    def test_Loaded_examcard_file_exposes_exam_basic_properties(self):
        from pylabs.io.examcard import load
        fpath = abspath(join('data/testdata/examcard',files[0]))
        examDict = load(fpath)
        self.assertEqual(examDict['name'], 'PHANTOM_QT1_SLU_20151230')

    def test_Loaded_examcard_file_exposes_exam_names(self):
        from pylabs.io.examcard import load
        fpath = abspath(join('data/testdata/examcard',files[0]))
        examDict = load(fpath)
        scans = examDict['scans']
        self.assertEqual(19, len(scans))
        self.assertIn('CoilSurveyScan', [s['name'] for s in scans])

    def test_Finds_scanProcedures_with_different_prefixes(self):
        # a10:scanProcedure vs a12:scanProcedure
        from pylabs.io.examcard import load
        fpath = abspath(join('data/testdata/examcard',files[0]))
        examDict = load(fpath)
        self.assertEqual(len(examDict['scans']), 19)
        fpath = abspath(join('data/testdata/examcard',files[1]))
        examDict = load(fpath)
        self.assertEqual(len(examDict['scans']), 21)

    def test_Gets_number_of_parameter_values_right(self):
        from pylabs.io.examcard import load
        fpath = abspath(join('data/testdata/examcard',files[1]))
        examDict = load(fpath)
        targetScan = 'DTI6_b1_PA_TOPDN'
        scanDict = [s for s in examDict['scans'] if s['name']==targetScan][0]
        testParams = [('GEX_CONV_id',3),('EX_PROC_image_types',4)]
        for testParam, pLength in testParams:
            self.assertIn(testParam, scanDict['parameters'])
            self.assertEqual(len(scanDict['parameters'][testParam]), pLength)

    def test_Gets_datatype_of_parameter_values_right(self):
        from pylabs.io.examcard import load
        fpath = abspath(join('data/testdata/examcard',files[1]))
        examDict = load(fpath)
        targetScan = 'DTI6_b1_PA_TOPDN'
        scanDict = [s for s in examDict['scans'] if s['name']==targetScan][0]
        params = scanDict['parameters']
        self.assertIsInstance(params['EX_GEO_fov'], float)
        self.assertIsInstance(params['EX_ACQ_scan_resol'], int)
        self.assertIsInstance(params['IF_str_total_scan_time'], str)
        self.assertIsInstance(params['EX_PROC_image_types'][0], int) #"ENUM"

    def test_Gets_float_parameter_value_right(self):
        from pylabs.io.examcard import load
        fpath = abspath(join('data/testdata/examcard',files[1]))
        examDict = load(fpath)
        targetScan = 'DTI6_b1_PA_TOPDN'
        scanDict = [s for s in examDict['scans'] if s['name']==targetScan][0]
        params = scanDict['parameters']
        self.assertEquals(params['EX_GEO_fov'], 256.0)

    def test_Gets_int_parameter_value_right(self):
        from pylabs.io.examcard import load
        fpath = abspath(join('data/testdata/examcard',files[1]))
        examDict = load(fpath)
        targetScan = 'DTI6_b1_PA_TOPDN'
        scanDict = [s for s in examDict['scans'] if s['name']==targetScan][0]
        params = scanDict['parameters']
        self.assertEquals(params['IF_epi_factor'], 67)

if __name__ == '__main__':
    unittest.main()


