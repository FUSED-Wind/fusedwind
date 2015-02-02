
import pkg_resources
import os
import numpy as np
import unittest

from openmdao.main.api import Assembly

from fusedwind.turbine.configurations import configure_bladesurface
from fusedwind.turbine.geometry import read_blade_planform

PATH = pkg_resources.resource_filename('fusedwind', 'test')


def configure_blade():

    top = Assembly()

    configure_bladesurface(top, os.path.join(PATH, 'data/DTU_10MW_RWT_blade_axis_prebend.dat'), planform_nC=6)

    # load the planform file
    top.blade_length = 86.366
    top.span_ni = 5

    b = top.blade_surface

    # distribute 200 points evenly along the airfoil sections
    b.chord_ni = 40

    # load the airfoil shapes defining the blade
    for f in [os.path.join(PATH, 'data/ffaw3241.dat'),
              os.path.join(PATH, 'data/ffaw3301.dat'),
              os.path.join(PATH, 'data/ffaw3360.dat'),
              os.path.join(PATH, 'data/ffaw3480.dat') ,
              os.path.join(PATH, 'data/cylinder.dat')]:

        b.base_airfoils.append(np.loadtxt(f))

    b.blend_var = np.array([0.241, 0.301, 0.36, 0.48, 1.])

    return top

class LoftedBladeSurfaceTest(unittest.TestCase):

    def test_build(self):
        top = configure_blade()
        top.run()
        d = np.loadtxt(os.path.join(PATH, 'data/blade_test_data.dat')).reshape(40, 5, 3)
        self.assertEqual(np.testing.assert_array_almost_equal(top.blade_surface.surfout.surface, d, decimal=6), None)

if __name__ == '__main__':

    unittest.main()
