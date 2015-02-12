
import numpy as np
import unittest

from openmdao.main.api import Assembly

from fusedwind.turbine.geometry_vt import BladePlanformVT
from fusedwind.turbine.geometry import RedistributedBladePlanform, SplinedBladePlanform



def configure_pf():

    pf = BladePlanformVT()
    pf.s = np.array([0, 0.08, 0.25, 0.5, 0.7, 0.98, 1.])
    pf.x = np.zeros(7)
    pf.y = np.zeros(7)
    pf.z = np.array([0, 0.08, 0.25, 0.5, 0.7, 0.98, 1.])
    pf.rot_x = np.zeros(7)
    pf.rot_y = np.zeros(7)
    pf.rot_z = np.array([-14.5       , -14.46339951,  -8.39059169,  -3.80326048, -0.3093841 ,   3.24525784,   3.428     ])
    pf.chord = np.array([ 0.06229303,  0.06274697,  0.07170661,  0.05870869,  0.0417073 , 0.01726638,  0.00694718])
    pf.rthick = np.array([ 1.        ,  0.90303866,  0.40834206,  0.26394705,  0.24103804, 0.241     ,  0.241     ])
    pf.athick = pf.chord * pf.rthick
    pf.p_le = np.array([ 0.5       ,  0.49662459,  0.38370686,  0.35000317,  0.35      , 0.35      ,  0.35      ])
    return pf

class RedistAsym(Assembly):

    def configure(self):
        self.add('pf', configure_pf())

        self.add('redist', RedistributedBladePlanform())
        self.driver.workflow.add('redist')
        self.redist.pfIn = self.pf
        self.redist.x = np.linspace(0, 1, 20)


class TestGeometry(unittest.TestCase):

    def test_splined_pf(self):

        chord = np.array([ 0.06229303,  0.06330014,  0.06994655,  0.07100946,  0.06652008,
        0.06069747,  0.05525125,  0.04915285,  0.04342934,  0.03876228,
        0.03505324,  0.0318812 ,  0.029023  ,  0.0263835 ,  0.02393461,
        0.02167727,  0.01962023,  0.01776974,  0.01273909,  0.00694718])

        top = SplinedBladePlanform()
        top.pfIn = configure_pf()
        top.span_ni = 20
        top.configure_splines()
        top.run()

        self.assertEqual(np.testing.assert_array_almost_equal(top.pfOut.chord, chord, decimal=6), None)
        
    def test_perturb_default(self):

        chord = np.array([ 0.06229303,  0.06330014,  0.06994655,  0.07126988,  0.08222149,
        0.07659311,  0.05673006,  0.04915285,  0.04342934,  0.03876228,
        0.03505324,  0.0318812 ,  0.029023  ,  0.0263835 ,  0.02393461,
        0.02167727,  0.01962023,  0.01776974,  0.01273909,  0.00694718])


        top = SplinedBladePlanform()
        top.pfIn = configure_pf()
        top.span_ni = 20
        top.configure_splines()
        top.run()

        top.chord_C[3] += 0.02
        top.run()

        self.assertEqual(np.testing.assert_array_almost_equal(top.pfOut.chord, chord, decimal=6), None)

    def test_perturb_bezier(self):

        chord = np.array([ 0.06229303,  0.06376952,  0.07223721,  0.07545525,  0.07224042,
        0.06643068,  0.06006542,  0.05267628,  0.04573023,  0.04012199,
        0.03578598,  0.03224209,  0.02918469,  0.02644862,  0.02395775,
        0.0216842 ,  0.01962139,  0.01776927,  0.01273863,  0.00694718])


        top = SplinedBladePlanform()
        top.pfIn = configure_pf()
        top.span_ni = 20
        top.configure_splines()
        top.chord.set_spline('bezier')
        top.run()

        top.chord_C[3] += 0.02
        top.run()

        self.assertEqual(np.testing.assert_array_almost_equal(top.pfOut.chord, chord, decimal=6), None)

    def test_pf_redist(self):

        top = RedistAsym()
        top.run()

if __name__ == '__main__':

    # top = PlanformSetup()
    # top.run()
    unittest.main()
