#__all__ = ['fused_wake']

import unittest

#FUSED-Wake imports
from fused_wake.wake import *
# from fused_wake.io import *
#from fused_wake.windturbine import *

#FUSED-Wind imports
from fusedwind.plant_flow.fused_plant_vt import GenericWindTurbineVT, GenericWindTurbinePowerCurveVT
from fusedwind.plant_flow.fused_plant_comp import WindTurbinePowerCurve, GenericWSPosition, HubCenterWSPosition, GenericWakeSum, GenericHubWindSpeed, GenericFlowModel, GenericWakeModel

#OpenMDAO imports
from openmdao.lib.casehandlers.api import CSVCaseRecorder
from openmdao.main.api import set_as_top

#Other imports
# import ipdb
import numpy as np
from numpy.linalg.linalg import norm
from random import random
import matplotlib.pyplot as plt


# Some handy case generators ---------------------------------------------------------------
def generate_a_valid_wt(D = 200*random()):
    wt_desc = GenericWindTurbineVT()
    wt_desc.rotor_diameter = D
    wt_desc.hub_height = D * (0.5 + random())
    return wt_desc


def generate_ws_positions(wt_desc = generate_a_valid_wt()):
    xy = [random()*1000, random()*1000]
    # Compute the ws_positions
    ws_positions = array([[xy[0], 
    					   xy[1] + cos(theta)*r, 
    					   sin(theta)*r + wt_desc.hub_height]
    					   for r in np.linspace(0.0, wt_desc.rotor_diameter/2.0, 10)
    					   for theta in np.linspace(0.0, 2.0*np.pi, 10)])
    return ws_positions

def generate_neutral_inflow(ws_positions, ws=random()*40, z_ref=random()*100):
    """ Generate a ramdom neutral inflow """
    inflow = NeutralLogLawInflowGenerator()
    inflow.z_0 = random()
    inflow.z_ref = z_ref
    inflow.wind_speed = ws
    inflow.ws_positions = ws_positions
    inflow.execute()
    return inflow.ws_array

def generate_v80():

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

    wt_desc = GenericWindTurbinePowerCurveVT()
    wt_desc.hub_height = V80['hub_height']
    wt_desc.rotor_diameter = V80['rotor_diameter']
    wt_desc.c_t_curve = V80['c_t_curve']
    wt_desc.power_curve = V80['power_curve']

    return wt_desc


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



class testHornsRev(unittest.TestCase):
    file_Positions = 'unittest_ref_files/HR_coordinates.dat'

    def HR_test(self, wfmp, file_power):

        ref_power = np.loadtxt(file_power)
        
        # Necessary for the parallelization
        wfm = set_as_top(wfmp)

        wt_desc = generate_v80()

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

        wfm.upstream_wake_driver.sequential = True

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



class test_AEP():#unittest.TestCase):
    file_Positions = 'unittest_ref_files/HR_coordinates.dat'

    def HR_test(self, wfm):
        aep = set_as_top(AEP())
        aep.configure()
        aep.replace('wf', wfm)

        wt_desc = generate_v80()
        aep.wt_list = [wt_desc]*80        
        aep.wf.z_0 = 1.0000e-04
        aep.wf.TI = 0.07
        aep.wf.z_ref = wt_desc.hub_height
        aep.wt_positions = np.loadtxt(self.file_Positions)
        aep.wf.configure()

        aep.wind_speeds = linspace(5.0, 24.0, 10)
        aep.wind_directions = linspace(0.0, 360.0, 2)
        n, m = aep.wind_speeds.shape[0], aep.wind_directions.shape[0]
        aep.wind_rose = ones([n, m]) / (n * m)
        # aep.wind_rose_driver.sequential = True
        # t = time.time()
        # aep.run()
        # print t-time.time(), aep.energies

        # In parallel
        aep.wind_rose_driver.sequential = False
        t = time.time()
        aep.run()
        print t-time.time(), aep.energies            

