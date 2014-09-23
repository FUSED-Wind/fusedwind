
import numpy as np
import unittest

from openmdao.main.api import Assembly

from fusedwind.turbine.geometry_vt import BladePlanformVT
from fusedwind.turbine.geometry import RedistributedBladePlanform

class PlanformSetup(Assembly):

    def configure(self):

        pf = BladePlanformVT()
        pf.x = np.zeros(7)
        pf.y = np.zeros(7)
        pf.z = np.array([0, 0.08, 0.25, 0.5, 0.7, 0.98, 1.])
        pf.rot_x = np.zeros(7)
        pf.rot_y = np.zeros(7)
        pf.rot_z = np.array([-14.5       , -14.46339951,  -8.39059169,  -3.80326048, -0.3093841 ,   3.24525784,   3.428     ])
        pf.chord = np.array([ 0.06229303,  0.06274697,  0.07170661,  0.05870869,  0.0417073 , 0.01726638,  0.00694718])
        pf.rthick = np.array([ 1.        ,  0.90303866,  0.40834206,  0.26394705,  0.24103804, 0.241     ,  0.241     ])
        pf.p_le = np.array([ 0.5       ,  0.49662459,  0.38370686,  0.35000317,  0.35      , 0.35      ,  0.35      ])

        self.add('pf', pf)

        self.add('redist', RedistributedBladePlanform())
        self.driver.workflow.add('redist')
        self.redist.pfIn = self.pf
        self.redist.x = np.linspace(0, 1, 20)


class TestGeometry(unittest.TestCase):

    def setUp(self):

        self.top = PlanformSetup()

    def test_pf_redist(self):

        self.top.run()

if __name__ == '__main__':

    # top = PlanformSetup()
    # top.run()
    unittest.main()
