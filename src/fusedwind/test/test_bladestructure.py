
import numpy as np
import unittest
import glob
import os

from openmdao.main.api import Assembly

from fusedwind.turbine.blade_structure import BladeStructureReader, BladeStructureWriter, BladeStructureCSBuilder
from fusedwind.turbine.structure_vt import BladeStructureVT3D



class BladeStructureSetup(Assembly):

    def configure(self):

        # configure simple structure with only a single TE panel, spar caps and a single LE region
        st = BladeStructureVT3D()


        # define matrials
        triax = st.add_material('triax')
        triax.E1 = 21.79e9
        triax.E2 = 14.67e9
        triax.E3 = 14.67e9
        triax.nu12 = 0.478
        triax.nu13 = 0.478
        triax.nu23 = 0.478
        triax.G12 = 9.413e9
        triax.G13 = 4.539e9
        triax.G23 = 4.539e9
        triax.rho = 1845

        biax = st.add_material('biax')
        biax.E1 = 13.92e9
        biax.E2 = 13.92e9
        biax.E3 = 13.92e9
        biax.nu12 = 0.533
        biax.nu13 = 0.533
        biax.nu23 = 0.533
        biax.G12 = 11.5e9
        biax.G13 = 4.539e9
        biax.G23 = 4.539e9
        biax.rho = 1845

        uniax = st.add_material('uniax')
        uniax.E1 = 41.63e9
        uniax.E2 = 14.93e9
        uniax.E3 = 14.93e9
        uniax.nu12 = 0.241
        uniax.nu13 = 0.241
        uniax.nu23 = 0.241
        uniax.G12 = 5.047e9
        uniax.G13 = 5.047e9
        uniax.G23 = 5.047e9
        uniax.rho = 1915.5

        core = st.add_material('core')
        core.E1 = 50e6
        core.E2 = 50e6
        core.E3 = 50e6
        core.nu12 = 0.5
        core.nu13 = 0.013
        core.nu23 = 0.013
        core.G12 = 16.67e6
        core.G13 = 150e6
        core.G23 = 150e6
        core.rho = 110

        # spanwise distribution of thickness points
        st.x = [0, 0.25, 0.6, 1.]

        st.configure_regions(5)

        st.DP00 = np.ones(4) * -1.
        st.DP05 = np.ones(4) * 1.
        st.DP01 = np.ones(4) * -0.5 
        st.DP04 = np.ones(4) * 0.5 
        st.DP02 = np.ones(4) * -0.35 
        st.DP03 = np.ones(4) * 0.35

        # add materials to regions
        l = st.region00.add_layer('triax')
        l.thickness = np.array([0.008, 0.003, 0.002, 0.001])
        l.angle = np.zeros(4)
        l = st.region00.add_layer('uniax')
        l.thickness = np.array([0.008, 0.000, 0.000, 0.000])
        l.angle = np.zeros(4)
        l = st.region00.add_layer('core')
        l.thickness = np.array([0.00, 0.07, 0.06, 0.000])
        l.angle = np.zeros(4)
        l = st.region00.add_layer('uniax')
        l.thickness = np.array([0.008, 0.000, 0.000, 0.000])
        l.angle = np.zeros(4)
        l = st.region00.add_layer('triax')
        l.thickness = np.array([0.008, 0.003, 0.002, 0.001])
        l.angle = np.zeros(4)
        st.region04 = st.region00.copy()

        l = st.region01.add_layer('triax')
        l.thickness = np.array([0.008, 0.000, 0.000, 0.000])
        l.angle = np.zeros(4)
        l = st.region01.add_layer('uniax')
        l.thickness = np.array([0.008, 0.04, 0.04, 0.002])
        l.angle = np.zeros(4)
        l = st.region01.add_layer('uniax')
        l.thickness = np.array([0.008, 0.04, 0.04, 0.002])
        l.angle = np.zeros(4)
        l = st.region01.add_layer('triax')
        l.thickness = np.array([0.008, 0.000, 0.000, 0.000])
        l.angle = np.zeros(4)
        st.region03 = st.region01.copy()

        l = st.region02.add_layer('triax')
        l.thickness = np.array([0.008, 0.003, 0.0015, 0.0011])
        l.angle = np.zeros(4)
        l = st.region02.add_layer('uniax')
        l.thickness = np.array([0.008, 0.001, 0.0007, 0.00])
        l.angle = np.zeros(4)
        l = st.region00.add_layer('core')
        l.thickness = np.array([0.00, 0.035, 0.02, 0.000])
        l.angle = np.zeros(4)
        l = st.region02.add_layer('uniax')
        l.thickness = np.array([0.008, 0.001, 0.0007, 0.00])
        l.angle = np.zeros(4)
        l = st.region02.add_layer('triax')
        l.thickness = np.array([0.008, 0.003, 0.0015, 0.0011])
        l.angle = np.zeros(4)

        st.configure_webs(2, [[2, 3], [1, 4]])
        l = st.web00.add_layer('biax')
        l.thickness = np.array([0.0025, 0.0045, 0.004, 0.001])
        l.angle = np.zeros(4)
        l = st.web00.add_layer('core')
        l.thickness = np.array([0.065, 0.05, 0.02, 0.005])
        l.angle = np.zeros(4)
        l = st.web00.add_layer('biax')
        l.thickness = np.array([0.0025, 0.0045, 0.004, 0.001])
        l.angle = np.zeros(4)
        st.web01 = st.web00.copy()

        self.stbase = st

        self.add('writer', BladeStructureWriter())
        self.add('reader', BladeStructureReader())
        self.driver.workflow.add(['writer', 'reader'])

        self.writer.st3d = self.stbase
        self.writer.filebase = 'testST'
        self.reader.filebase = 'testST_1'


class BladeSurfaceTestCase(unittest.TestCase):

    def setUp(self):

        self.top = BladeStructureSetup()
        self.top.run()

    def tearDown(self):

        files = glob.glob('testST*')
        for name in files:
            os.remove(name)

    def test_readwrite_consistency(self):

        for rname in self.top.stbase.regions:
            r1 = getattr(self.top.stbase, rname)
            r2 = getattr(self.top.reader.st3d, rname)
            for lname in r1.layers:
                l1 = getattr(r1, lname)
                l2 = getattr(r2, lname)
                # print l2.thickness, l1.thickness
                self.assertEqual(np.testing.assert_almost_equal(l2.thickness, l1.thickness, decimal=5), None)


if __name__ == '__main__':

    # top = BladeStructureSetup()
    # top.run()

    unittest.main()
