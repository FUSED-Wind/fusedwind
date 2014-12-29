
import pkg_resources
import os
import numpy as np
import unittest

from fusedwind.turbine.geometry import LoftedBladeSurface
from fusedwind.turbine.geometry import read_blade_planform, redistribute_blade_planform

PATH = pkg_resources.resource_filename('fusedwind', 'test')


def configure_blade():

    pf = read_blade_planform(os.path.join(PATH, 'data/DTU_10MW_RWT_blade_axis_prebend.dat'))
    pf = redistribute_blade_planform(pf, np.linspace(0, 1, 5))

    b = LoftedBladeSurface()
    b.pfIn = pf
    b.chord_ni = 40

    for f in [os.path.join(PATH, 'data/ffaw3241.dat'),
              os.path.join(PATH, 'data/ffaw3301.dat'),
              os.path.join(PATH, 'data/ffaw3360.dat'),
              os.path.join(PATH, 'data/ffaw3480.dat'),
              os.path.join(PATH, 'data/cylinder.dat')]:

        b.base_airfoils.append(np.loadtxt(f))

    b.blend_var = np.array([0.241, 0.301, 0.36, 0.48, 1.])
    return b

class LoftedBladeSurfaceTest(unittest.TestCase):

    def test_build(self):
        b = configure_blade()
        b.execute()
        d = np.loadtxt(os.path.join(PATH, 'data/blade_test_data.dat')).reshape(40, 5, 3)
        self.assertEqual(np.testing.assert_array_almost_equal(b.surfout.surface, d, decimal=6), None)

if __name__ == '__main__':

    unittest.main()
