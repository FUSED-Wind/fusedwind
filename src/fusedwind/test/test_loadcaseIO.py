
import glob
import os
import unittest
import numpy as np
from fusedwind.turbine.loadcaseIO import DTU10MWLoadCaseReader, LoadCaseInterpolator, LoadCaseWriter, LoadCaseReader



class TestLoadCaseIO(unittest.TestCase):

    def test_readwrite(self):
        r = LoadCaseReader()
        r.case_files = glob.glob('data/extreme_loads0*')
        r.execute()

        w = LoadCaseWriter()
        w.load_cases = r.load_cases
        w.file_base = 'test_lc'
        w.execute()

        rr = LoadCaseReader()
        rr.case_files = glob.glob('test_lc0*.dat')
        rr.execute()

        for i, case in enumerate(r.load_cases.cases):
            c0 = case._toarray()
            l1 = rr.load_cases.cases[i]
            c1 = l1._toarray()
            self.assertEqual(np.testing.assert_array_almost_equal(c0, c1, decimal=6), None)

    def tearDown(self):

        files = glob.glob('test_lc0*')
        print files
        for name in files:
            os.remove(name)

if __name__ == '__main__':

    unittest.main()
