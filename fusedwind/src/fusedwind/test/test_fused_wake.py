# Unit test of FUSED_Wake
import unittest
from fused_wake.wake import *
from fused_wake.io import *
from fused_wake.windturbine import *
from fused_wake.lib import *
from fused_wake.gcl import *
from fused_wake.noj import *
import ipdb
import numpy as np
from numpy.linalg.linalg import norm
from openmdao.lib.casehandlers.api import CSVCaseRecorder
from openmdao.main.api import set_as_top
from random import random
import pylab as plt

# Some handy case generators ---------------------------------------------------------------


def generate_a_valid_wt():
    wt_desc = GenericWindTurbineDesc()
    wt_desc.hub_height = random()*200
    wt_desc.rotor_diameter = wt_desc.hub_height*2.0 * (1 - random())
    return wt_desc


def generate_ws_positions():
    wt_desc = generate_a_valid_wt()
    xy = [random()*1000, random()*1000]
    # Compute the ws_positions
    ws_pos = GaussWSPosition()
    ws_pos.wt_desc = wt_desc
    ws_pos.wt_xy = xy
    ws_pos.N = 6
    ws_pos.execute()
    return ws_pos.ws_positions

# UnitTest classes -----------------------------------------------------------------------


# class WakeDBTest(unittest.TestCase):

    def testWakeDB(self):
        wake_db = WakeDB()
        wake_db.wake_rec = 'wake_rec'
        cases = []
        ni = int(random()*10)+1
        nj = int(random()*10)+1
        for i in range(ni):
            for j in range(nj):
                cases.append(Case(outputs=[(wake_db.wake_rec+'.i', i),
                                           (wake_db.wake_rec+'.j', j),
                                           (wake_db.wake_rec+'.ws_array', [i, j])]))
        wake_db.cases = ListCaseIterator(cases)
        wake_db.i = int(np.floor(random()*nj))
        wake_db.execute()
        for c in wake_db.wakes:
            self.assertEqual(c[1], wake_db.i)


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

    def testGaussWSPosition(self):
        # print "Testing GaussWSPosition ----------------------------------------------"
        ws_pos = GaussWSPosition()
        ws_pos.wind_direction = random()*360.0
        # Test default N value
        self.generic_ws_pos_test(ws_pos)

        # Test acceptable N values
        for N in range(4, 7):
            ws_pos.N = N
            self.generic_ws_pos_test(ws_pos)

        # Test some innacceptable values ------------------------------------------
        for N in [1, 2, 3, 7, 8, 9, 10]:
            ws_pos.N = N
            self.assertRaises(Exception, self.generic_ws_pos_test, ws_pos)

        # Test the wind_direction orientation .------------------------------------
        ws_pos = GaussWSPosition()
        ws_pos.wt_desc = generate_a_valid_wt()
        ws_pos.wt_xy = [random()*1000, random()*1000]
        ws_pos.N = 6

        # North
        ws_pos.wind_direction = 0.0
        ws_pos.execute()
        # The points should be aligned in the x direction, so they should have a constant y
        self.assertAlmostEqual(norm(ws_pos.ws_positions[:, 1]-ws_pos.wt_xy[1]), 0.0)

        # South
        ws_pos.wind_direction = 180.0
        ws_pos.execute()
        # The points should be aligned in the x direction, so they should have a constant y
        self.assertAlmostEqual(norm(ws_pos.ws_positions[:, 1]-ws_pos.wt_xy[1]), 0.0)

        # West
        ws_pos.wind_direction = 270.0
        ws_pos.execute()
        # The points should be aligned in the x direction, so they should have a constant y
        self.assertAlmostEqual(norm(ws_pos.ws_positions[:, 0]-ws_pos.wt_xy[0]), 0.0)

        # East
        ws_pos.wind_direction = 90.0
        ws_pos.execute()
        # The points should be aligned in the x direction, so they should have a constant y
        self.assertAlmostEqual(norm(ws_pos.ws_positions[:, 0]-ws_pos.wt_xy[0]), 0.0)

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


class HubWS(unittest.TestCase):

    def testGaussHubWS(self):
        # print "Testing GaussHubWS -------------------------------------------------"
        wt_desc = generate_a_valid_wt()

        # Compute the ws_positions
        ws_pos = GaussWSPosition()
        ws_pos.wt_desc = wt_desc
        ws_pos.wt_xy = [random()*1000, random()*1000]
        ws_pos.execute()

        # Generate the inflow the homogeneous inflow generator
        inflow = HomogeneousInflowGenerator()
        inflow.wind_speed = random()*40
        inflow.ws_positions = ws_pos.ws_positions
        inflow.execute()
        # print inflow.ws_array

        # Now compute the hub wind speed
        hub_ws = GaussHubWS()
        hub_ws.wt_desc = wt_desc
        hub_ws.ws_positions = ws_pos.ws_positions
        hub_ws.ws_array = inflow.ws_array
        hub_ws.execute()

        # print "hub ws:", hub_ws.hub_wind_speed
        # Test that the hub_wind speed is within a margin of eps
        eps = 1E-8
        self.assertTrue(abs(hub_ws.hub_wind_speed - inflow.wind_speed) < eps)

        # Generate the inflow using the Neutral log law generator
        inflow = NeutralLogLawInflowGenerator()
        inflow.z_0 = random()
        inflow.z_ref = random()*100
        inflow.wind_speed = random()*40
        inflow.ws_positions = ws_pos.ws_positions
        inflow.execute()
        # print "inputs z_0, z_ref, ws: ", inflow.z_0, inflow.z_ref, inflow.wind_speed
        # print inflow.ws_array
        hub_ws.ws_array = inflow.ws_array
        hub_ws.execute()
        # print "hub ws:", hub_ws.hub_wind_speed, inflow.wind_speed, inflow.ws_array.mean(), abs(hub_ws.hub_wind_speed - inflow.ws_array.mean())/inflow.ws_array.mean()
        # Test that the hub_wind speed is within a margin of eps
        eps = 0.05
        self.assertTrue(abs(hub_ws.hub_wind_speed - inflow.ws_array.mean())/inflow.ws_array.mean() < eps)


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
    V80 = {'rotor_diameter': 80.0,
           'hub_height': 70.0,
           'power_curve': array([[4.00000000e+00, 6.66000000e+04, ],
                                [5.00000000e+00, 1.54000000e+05],
                                [6.00000000e+00, 2.82000000e+05],
                                [7.00000000e+00, 4.60000000e+05],
                                [8.00000000e+00, 6.96000000e+05],
                                [9.00000000e+00, 9.96000000e+05],
                                [1.00000000e+01, 1.34100000e+06],
                                [1.10000000e+01, 1.66100000e+06],
                                [1.20000000e+01, 1.86600000e+06],
                                [1.30000000e+01, 1.95800000e+06],
                                [1.40000000e+01, 1.98800000e+06],
                                [1.50000000e+01, 1.99700000e+06],
                                [1.60000000e+01, 1.99900000e+06],
                                [1.70000000e+01, 2.00000000e+06],
                                [1.80000000e+01, 2.00000000e+06],
                                [1.90000000e+01, 2.00000000e+06],
                                [2.00000000e+01, 2.00000000e+06],
                                [2.10000000e+01, 2.00000000e+06],
                                [2.20000000e+01, 2.00000000e+06],
                                [2.30000000e+01, 2.00000000e+06],
                                [2.40000000e+01, 2.00000000e+06],
                                [2.50000000e+01, 2.00000000e+06]]),
           'c_t_curve': array([[4.00000000e+00, 8.18000000e-01],
                               [5.00000000e+00, 8.06000000e-01],
                               [6.00000000e+00, 8.04000000e-01],
                               [7.00000000e+00, 8.05000000e-01],
                               [8.00000000e+00, 8.06000000e-01],
                               [9.00000000e+00, 8.07000000e-01],
                               [1.00000000e+01, 7.93000000e-01],
                               [1.10000000e+01, 7.39000000e-01],
                               [1.20000000e+01, 7.09000000e-01],
                               [1.30000000e+01, 4.09000000e-01],
                               [1.40000000e+01, 3.14000000e-01],
                               [1.50000000e+01, 2.49000000e-01],
                               [1.60000000e+01, 2.02000000e-01],
                               [1.70000000e+01, 1.67000000e-01],
                               [1.80000000e+01, 1.40000000e-01],
                               [1.90000000e+01, 1.19000000e-01],
                               [2.00000000e+01, 1.02000000e-01],
                               [2.10000000e+01, 8.80000000e-02],
                               [2.20000000e+01, 7.70000000e-02],
                               [2.30000000e+01, 6.70000000e-02],
                               [2.40000000e+01, 6.00000000e-02],
                               [2.50000000e+01, 5.30000000e-02]])}

    def testWTCurve(self):
        # Test if the model return the same as the power curve
        wt_desc = GenericWindTurbineDesc()
        wt_desc.rotor_diameter = self.V80['rotor_diameter']
        wt_desc.hub_height = self.V80['hub_height']
        wt_desc.c_t_curve = self.V80['c_t_curve']
        wt_desc.power_curve = self.V80['power_curve']

        # Test that the curve does not give values that are higher / lower in between each control points
        # -> TODO
        wt_model = WindTurbinePowerCurve()
        wt_model.wt_desc = wt_desc
        for i in range(self.V80['power_curve'].shape[0]):
            ws = self.V80['power_curve'][i, 0]
            wt_model.hub_wind_speed = ws
            wt_model.execute()
            # print wt_model.hub_wind_speed, wt_model.power, wt_model.thrust, wt_model.a, wt_model.c_t
            self.assertAlmostEqual(wt_model.power, self.V80['power_curve'][i, 1])


class testWakeModel(unittest.TestCase):
    tests = {'GCL': {'test1': {'z_0': 1.0000e-04,
                               'TI': 0.07,
                               'U0': 8.0,
                               'c_t': 0.80597,
                               'xpos': 423974,
                               'ypos': 6151447,
                               'hub_height': 70.0,
                               'rotor_diameter': 80.0,
                               'wind_direction': 270.0,
                               'points': 'unittest_ref_files/GCL/points1.txt',
                               'u': 'unittest_ref_files/GCL/points_u1.txt'},
                     'test2': {'z_0': 1.0000e-04,
                               'TI': 0.07,
                               'U0': 8.0,
                               'c_t': 0.80597,
                               'xpos': 423974,
                               'ypos': 6151447,
                               'hub_height': 70.0,
                               'rotor_diameter': 80.0,
                               'wind_direction': 270.0,
                               'points': 'unittest_ref_files/GCL/points2.txt',
                               'u': 'unittest_ref_files/GCL/points_u2.txt'}},
             'NOJ': {'test1': {'z_0': 1.0000e-04,
                               'TI': 0.07,
                               'U0': 8.0,
                               'c_t': 0.8060,
                               'xpos': 423974,
                               'ypos': 6151447,
                               'hub_height': 70.0,
                               'rotor_diameter': 80.0,
                               'wind_direction': 270.0,
                               'points': 'unittest_ref_files/NOJ/points1.txt',
                               'u': 'unittest_ref_files/NOJ/points_u1.txt'},
                     'test2': {'z_0': 1.0000e-04,
                               'TI': 0.07,
                               'U0': 8.0,
                               'c_t': 0.8060,
                               'xpos': 423974,
                               'ypos': 6151447,
                               'hub_height': 70.0,
                               'rotor_diameter': 80.0,
                               'wind_direction': 270.0,
                               'points': 'unittest_ref_files/NOJ/points2.txt',
                               'u': 'unittest_ref_files/NOJ/points_u2.txt'}}}

    def testNOJ(self):
        plt.close(1)
        plt.figure(1)
        i = 0        
        for k, v in self.tests['NOJ'].iteritems():
            # print 'Test: ', k
            wt_desc = GenericWindTurbineDesc()
            xy = [v['xpos'], v['ypos']]
            wt_desc.hub_height = v['hub_height']
            wt_desc.rotor_diameter = v['rotor_diameter']

            ws_positions = loadtxt(v['points'], delimiter=',')
            matlab_results = loadtxt(v['u'], delimiter=',')

            # Make the inflow using the log law
            inflow = NeutralLogLawInflowGenerator()
            inflow.z_0 = v['z_0']
            inflow.wind_speed = v['U0']
            inflow.z_ref = v['hub_height']
            inflow.ws_positions = ws_positions
            inflow.execute()

            wake = NOJWakeModel()
            wake.c_t = v['c_t']
            wake.wind_direction = v['wind_direction']
            wake.ws_array_inflow = inflow.ws_array
            wake.ws_positions = ws_positions
            wake.wt_desc = wt_desc
            wake.wt_xy = xy
            wake.execute()
            # print wake.ws_array_inflow, wake.ws_array, matlab_results, np.linalg.linalg.norm(wake.ws_array - matlab_results)
            eps = 1.0E-5

            plt.subplot(len(self.tests['NOJ']),1,i); i+=1
            plt.plot(wake.ws_array, label='python')
            plt.plot(matlab_results, label='matlab')
            plt.title('NOJ: ' + k)
            plt.legend()


            # ipdb.set_trace()
            self.assertTrue(norm(wake.ws_array - matlab_results) < eps)
            # ipdb.set_trace()

        plt.savefig('noj_single_wake.pdf')

    def testGCL(self):
        plt.close(1)
        plt.figure(1)
        i = 0
        for k, v in self.tests['GCL'].iteritems():
            # print 'Test: ', k
            wt_desc = GenericWindTurbineDesc()
            xy = [v['xpos'], v['ypos']]
            wt_desc.hub_height = v['hub_height']
            wt_desc.rotor_diameter = v['rotor_diameter']

            ws_positions = loadtxt(v['points'], delimiter=',')
            matlab_results = loadtxt(v['u'], delimiter=',')

            # Make the inflow using the log law
            inflow1 = NeutralLogLawInflowGenerator()
            inflow1.z_0 = v['z_0']
            inflow1.wind_speed = v['U0']
            inflow1.z_ref = v['hub_height']
            inflow1.ws_positions = ws_positions
            inflow1.execute()

            # Compute the ws_positions
            ws_pos = GaussWSPosition()
            ws_pos.wt_desc = wt_desc
            ws_pos.wt_xy = xy
            ws_pos.execute()

            # Make the inflow using the log law
            inflow2 = NeutralLogLawInflowGenerator()
            inflow2.z_0 = v['z_0']
            inflow2.wind_speed = v['U0']
            inflow2.z_ref = v['hub_height']
            inflow2.ws_positions = ws_pos.ws_positions
            inflow2.execute()

            # Now compute the hub wind speed
            hub_ws = GaussHubWS()
            hub_ws.wt_desc = wt_desc
            hub_ws.ws_positions = ws_pos.ws_positions
            hub_ws.ws_array = inflow2.ws_array
            hub_ws.execute()

            wake = GCLWakeModel()
            wake.c_t = v['c_t']
            wake.TI = v['TI']
            wake.wind_direction = v['wind_direction']
            wake.hub_wind_speed = hub_ws.hub_wind_speed
            wake.ws_array_inflow = inflow1.ws_array
            wake.ws_positions = ws_positions
            wake.wt_desc = wt_desc
            wake.wt_xy = xy

            wake.execute()
            # print wake.ws_array_inflow, wake.ws_array, matlab_results, np.linalg.linalg.norm(wake.ws_array - matlab_results)
            eps = 1.0E-2
            self.assertTrue(np.linalg.linalg.norm(wake.ws_array - matlab_results) < eps)

            plt.subplot(len(self.tests['GCL']),1,i); i+=1
            plt.plot(wake.ws_array, label='python')
            plt.plot(matlab_results, label='matlab')
            plt.title('GCL: ' + k)
            plt.legend()

        plt.savefig('gcl_single_wake.pdf')


class testHornsRev(unittest.TestCase):
    file_Positions = 'unittest_ref_files/HR_coordinates.dat'
    file_GCL_power = 'unittest_ref_files/GCL/HR_Power_270.txt'
    file_GCL_CT = 'unittest_ref_files/GCL/HR_CT_270.txt'
    file_GCL_U = 'unittest_ref_files/GCL/HR_U_270.txt'
    file_NOJ_power = 'unittest_ref_files/NOJ/HR_Power_270.txt'
    file_NOJ_CT = 'unittest_ref_files/NOJ/HR_CT_270.txt'
    file_NOJ_U = 'unittest_ref_files/NOJ/HR_U_270.txt'

    V80 = {'rotor_diameter': 80.0,
           'hub_height': 70.0,
           'power_curve': array([[4.00000000e+00, 6.66000000e+04, ],
                                [5.00000000e+00, 1.54000000e+05],
                                [6.00000000e+00, 2.82000000e+05],
                                [7.00000000e+00, 4.60000000e+05],
                                [8.00000000e+00, 6.96000000e+05],
                                [9.00000000e+00, 9.96000000e+05],
                                [1.00000000e+01, 1.34100000e+06],
                                [1.10000000e+01, 1.66100000e+06],
                                [1.20000000e+01, 1.86600000e+06],
                                [1.30000000e+01, 1.95800000e+06],
                                [1.40000000e+01, 1.98800000e+06],
                                [1.50000000e+01, 1.99700000e+06],
                                [1.60000000e+01, 1.99900000e+06],
                                [1.70000000e+01, 2.00000000e+06],
                                [1.80000000e+01, 2.00000000e+06],
                                [1.90000000e+01, 2.00000000e+06],
                                [2.00000000e+01, 2.00000000e+06],
                                [2.10000000e+01, 2.00000000e+06],
                                [2.20000000e+01, 2.00000000e+06],
                                [2.30000000e+01, 2.00000000e+06],
                                [2.40000000e+01, 2.00000000e+06],
                                [2.50000000e+01, 2.00000000e+06]]),
           'c_t_curve': array([[4.00000000e+00, 8.18000000e-01],
                               [5.00000000e+00, 8.06000000e-01],
                               [6.00000000e+00, 8.04000000e-01],
                               [7.00000000e+00, 8.05000000e-01],
                               [8.00000000e+00, 8.06000000e-01],
                               [9.00000000e+00, 8.07000000e-01],
                               [1.00000000e+01, 7.93000000e-01],
                               [1.10000000e+01, 7.39000000e-01],
                               [1.20000000e+01, 7.09000000e-01],
                               [1.30000000e+01, 4.09000000e-01],
                               [1.40000000e+01, 3.14000000e-01],
                               [1.50000000e+01, 2.49000000e-01],
                               [1.60000000e+01, 2.02000000e-01],
                               [1.70000000e+01, 1.67000000e-01],
                               [1.80000000e+01, 1.40000000e-01],
                               [1.90000000e+01, 1.19000000e-01],
                               [2.00000000e+01, 1.02000000e-01],
                               [2.10000000e+01, 8.80000000e-02],
                               [2.20000000e+01, 7.70000000e-02],
                               [2.30000000e+01, 6.70000000e-02],
                               [2.40000000e+01, 6.00000000e-02],
                               [2.50000000e+01, 5.30000000e-02]])}

    def testGCL(self):
        self.HR_test(GCLWindFarmWake(), self.file_GCL_power)

    # def testNOJ(self):
    #     noj = NOJWindFarmWake()
    #     self.HR_test(noj, self.file_NOJ_power)

    def testMozaicTile(self):
        self.HR_test(MozaicTileWindFarmWake(), self.file_NOJ_power)


    def HR_test(self, wfmp, file_power):

        ref_power = np.loadtxt(file_power)
        
        # Necessary for the parallelization
        wfm = set_as_top(wfmp)

        wt_desc = GenericWindTurbinePowerCurveDesc()
        wt_desc.hub_height = self.V80['hub_height']
        wt_desc.rotor_diameter = self.V80['rotor_diameter']
        wt_desc.c_t_curve = self.V80['c_t_curve']
        wt_desc.power_curve = self.V80['power_curve']

        # wfm.configure()
        # wfm.configure_single_inflow()
        wfm.wt_list = [wt_desc]*80

        wfm.wind_speed = 8.0
        wfm.wind_direction = 270.0
        wfm.z_0 = 1.0000e-04
        wfm.TI = 0.07
        wfm.z_ref = wt_desc.hub_height
        wfm.wt_positions = np.loadtxt(self.file_Positions)
        # wfm.wake_driver.recorders.append(CSVCaseRecorder(filename='debug.csv'))

        wfm.upstream_wake_driver.sequential = False

        # ipdb.set_trace()

        wfm.run()

        # ipdb.set_trace()
        diff_power = ref_power - wfm.wt_power
        # print (sum(wfm.wt_power)-sum(ref_power))/sum(ref_power), diff_power

        plt.close(1)
        plt.figure(1)
        indx = np.arange(len(wfm.wt_power))
        width = 0.35
        plt.bar(indx, wfm.wt_power, width, color='b', label='python')
        plt.bar(indx+width, ref_power, width, color='r', label='matlab')
        plt.legend()
        plt.savefig('HR_'+wfm.__class__.__name__+'.pdf')

        self.assertTrue(abs((sum(wfm.wt_power)-sum(ref_power))/sum(ref_power)) < 3E-3)


        ### Test in the single wind turbine configuration
        wfm.configure_single_turbine_type()
        wfm.wt_list = [wt_desc]
        wfm.run()        
        self.assertTrue(abs((sum(wfm.wt_power)-sum(ref_power))/sum(ref_power)) < 3E-3)


if __name__ == "__main__":
    unittest.main()
