
import unittest

#FUSED-Wake imports
from fusedwind.plant_flow.wake.wake import *
from fusedwind.plant_flow.wake.accumulation import *
# from fused_wake.io import *
#from fused_wake.windturbine import *

#FUSED-Wind imports
from fusedwind.plant_flow.vt import GenericWindTurbineVT, GenericWindTurbinePowerCurveVT
from fusedwind.plant_flow.comp import WindTurbinePowerCurve, GenericWSPosition, HubCenterWSPosition, GenericWakeSum, GenericHubWindSpeed, GenericFlowModel, GenericWakeModel

#FUSED-Wake.test imports
from test_lib import generate_a_valid_wt, generate_ws_positions, generate_neutral_inflow, generate_v80



#OpenMDAO imports
from openmdao.lib.casehandlers.api import CSVCaseRecorder
from openmdao.main.api import set_as_top

#Other imports
import ipdb
import numpy as np
from numpy.linalg.linalg import norm
from random import random
import matplotlib.pyplot as plt

#
# class fused_wakeTestCase(unittest.TestCase):
#
#     def setUp(self):
#         pass
#
#     def tearDown(self):
#         pass
#
#     # add some tests here...
#
#     #def test_fused_wake(self):
#         #pass



# UnitTest classes -----------------------------------------------------------------------

class WakeDistTest(unittest.TestCase):

    def testWakeDist(self):
        wake_dist = WTStreamwiseSorting()

        # Horizontal row-------------------------------
        wake_dist.wt_positions = np.array([np.arange(10), np.zeros([10])]).T
        wake_dist.wind_direction = 270.0
        wake_dist.execute()

        # print wake_dist.wind_direction, wake_dist.ordered_indices
        self.assertEqual(norm(np.array(np.arange(10)) - np.array(wake_dist.ordered_indices)), 0.0)

        wake_dist.wind_direction = 90.0
        wake_dist.execute()
        # print wake_dist.wind_direction, wake_dist.ordered_indices
        self.assertEqual(norm(np.arange(9, -1, -1) - np.array(wake_dist.ordered_indices)), 0.0)

        # Vertical row -------------------------------
        wake_dist.wt_positions = np.array([zeros([10]), np.arange(10)]).T
        wake_dist.wind_direction = 0.0
        wake_dist.execute()
        # print wake_dist.wind_direction, wake_dist.ordered_indices
        self.assertEqual(norm(np.arange(9, -1, -1) - np.array(wake_dist.ordered_indices)), 0.0)

        wake_dist.wind_direction = 360.0
        wake_dist.execute()
        # print wake_dist.wind_direction, wake_dist.ordered_indices
        self.assertEqual(norm(np.arange(9, -1, -1) - np.array(wake_dist.ordered_indices)), 0.0)

        wake_dist.wind_direction = 180.0
        wake_dist.execute()
        # print wake_dist.wind_direction, wake_dist.ordered_indices
        self.assertEqual(norm(np.array(np.arange(10)) - np.array(wake_dist.ordered_indices)), 0.0)

        # Diagonal row -------------------------------
        wake_dist.wt_positions = np.array([np.arange(10), np.arange(10)]).T
        wake_dist.wind_direction = 225.0
        wake_dist.execute()
        # print wake_dist.wind_direction, wake_dist.ordered_indices
        self.assertEqual(norm(np.array(np.arange(10)) - np.array(wake_dist.ordered_indices)), 0.0)

        wake_dist.wind_direction = 45.0
        wake_dist.execute()
        # print wake_dist.wind_direction, wake_dist.ordered_indices
        self.assertEqual(norm(np.arange(9, -1, -1) - np.array(wake_dist.ordered_indices)), 0.0)


class WSPos(unittest.TestCase):

    """
    Test the ws_pos modules
    """
    def testHubCenterWSPosition(self):
        # print "Testing HubCenterWS -------------------------------------------------"
        ws_pos = HubCenterWSPosition()
        self.generic_ws_pos_test(ws_pos)

    def generic_ws_pos_test(self, ws_pos):
        wt_desc = generate_a_valid_wt()
        ws_pos.wt_xy = [random()*1000, random()*1000]
        # print "inputs: x,y,H,R:", wt_desc.xpos, wt_desc.ypos, wt_desc.hub_height, wt_desc.rotor_diameter
        ws_pos.wt_desc = wt_desc
        ws_pos.execute()
        # print "ws_positions:"
        # print ws_pos.ws_positions
        for i in range(ws_pos.ws_positions.shape[0]):
            # Check that the x, y values are not outside the wt rotor
            self.assertTrue(sqrt((ws_pos.ws_positions[i, 0] - ws_pos.wt_xy[0])**2.0 + (
                ws_pos.ws_positions[i, 1] - ws_pos.wt_xy[1])**2.0) <= wt_desc.rotor_diameter/2.0)
            # Check that the z values are not outside the wt rotor
            self.assertTrue(abs(ws_pos.ws_positions[i, 2] - wt_desc.hub_height) <= wt_desc.rotor_diameter/2.0)
            # Check that the z value is not under the ground
            self.assertTrue(ws_pos.ws_positions[i, 2] > 0.0)



class Inflow(unittest.TestCase):

    def testHomogeneousInflowGenerator(self):
        ws_positions = generate_ws_positions()
        # Generate the inflow
        inflow = HomogeneousInflowGenerator()
        inflow.wind_speed = random()*40
        inflow.ws_positions = ws_positions
        inflow.execute()
        # print inflow.ws_array
        # Test that the generated ws_array if of the correct shape and size
        self.assertEqual(inflow.ws_array.shape[0], ws_positions.shape[0])
        # Test that the generated ws_array have the correct value
        for i in range(inflow.ws_array.shape[0]):
            self.assertEqual(inflow.ws_array[i], inflow.wind_speed)

    def testNeutralLogLawInflowGenerator(self):
        # print "Testing NeutralLogLawInflowGenerator -------------------------------------------------"
        ws_positions = generate_ws_positions()
        # Generate the inflow
        inflow = NeutralLogLawInflowGenerator()
        inflow.z_0 = random()
        inflow.z_ref = random()*100
        inflow.wind_speed = random()*40
        inflow.ws_positions = ws_positions
        inflow.execute()
        # print "inputs z_0, z_ref, ws: ", inflow.z_0, inflow.z_ref, inflow.wind_speed
        # print inflow.ws_array
        # Test that the generated ws_array if of the correct shape and size
        self.assertEqual(inflow.ws_array.shape[0], ws_positions.shape[0])
        # Test that the generated ws_array have the correct value
        ustar = inflow.wind_speed * inflow.KAPPA / np.log(inflow.z_ref/inflow.z_0)
        for i in range(inflow.ws_array.shape[0]):
            val = ustar / inflow.KAPPA * np.log(ws_positions[i, 2]/inflow.z_0)
            self.assertAlmostEqual(inflow.ws_array[i], val)


class testWakeSum(unittest.TestCase):

    def testQuadraticWakeSum(self):
        # ws_pos = generate_ws_positions()
        # SUM of ones / N wake
        n = np.int(np.random.rand()*100) + 1
        nwake = np.int(np.random.rand()*100) + 1
        inflow_ws = np.random.rand(n)*40
        wake_ws = []
        for i in range(nwake):
            # wake_ws.append((1-np.sqrt(1.0/(nwake))) * inflow_ws)
            wake_ws.append((np.sqrt(1.0/(nwake))) * inflow_ws)
        # for i in range(n):
        #     wake_ws[i,:] = wake_ws[i,:] * inflow_ws[i]
        wsum = QuadraticWakeSum()
        wsum.ws_array_inflow = inflow_ws
        wsum.wakes = wake_ws
        wsum.execute()
        # print n, inflow_ws, wake_ws, wsum.ws_array
        for i in range(n):
            self.assertAlmostEqual(wsum.ws_array[i], 0.00)

    def testLinearWakeSum(self):
        # ws_pos = generate_ws_positions()
        # SUM of ones / N wake
        n = np.int(np.random.rand()*100) + 1
        nwake = np.int(np.random.rand()*100) + 1
        inflow_ws = np.random.rand(n)*40
        # wake_ws = (1-1.0/(nwake)) * ones([n, nwake])
        wake_ws = []
        for i in range(nwake):
            wake_ws.append((1.0/(nwake)) * inflow_ws)
            # wake_ws.append((1-1.0/(nwake)) * inflow_ws)
        wsum = LinearWakeSum()
        wsum.ws_array_inflow = inflow_ws
        wsum.wakes = wake_ws
        wsum.execute()
        # print n, inflow_ws, wake_ws, wsum.ws_array
        for i in range(n):
            self.assertAlmostEqual(wsum.ws_array[i], 0.00)


class testWTModel(unittest.TestCase):

    def testWTCurve(self):
        # Test if the model return the same as the power curve
        wt_desc = generate_v80()

        # Test that the curve does not give values that are higher / lower in between each control points
        # -> TODO
        wt_model = WindTurbinePowerCurve()
        wt_model.wt_desc = wt_desc
        for i in range(wt_desc.power_curve.shape[0]):
            ws = wt_desc.power_curve[i, 0]
            wt_model.hub_wind_speed = ws
            wt_model.execute()
            # print wt_model.hub_wind_speed, wt_model.power, wt_model.thrust, wt_model.a, wt_model.c_t
            self.assertAlmostEqual(wt_model.power, wt_desc.power_curve[i, 1])



if __name__ == "__main__":
    unittest.main()
