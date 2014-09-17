# test_fused_plant_asym
from random import random
import unittest

from fusedwind.plant_flow.asym import *
from test_comp import TestWindFarm
from test_vt import generate_random_GenericWindRoseVT
import numpy as np

def generate_inputs_AEPWindRose(aep):
    aep.wind_speeds = linspace(0., 30, np.random.randint(30)).tolist()
    aep.wind_directions = linspace(0., 360, np.random.randint(360))[:-1].tolist()



class test_AEPSingleWindRose(unittest.TestCase):
    def test_init(self):
        aep = AEPSingleWindRose()

    def test_configure(self):
        aep = AEPSingleWindRose()
        aep.configure()
               

    def test_run(self):
        aep = AEPSingleWindRose()
        generate_inputs_AEPWindRose(aep)
        aep.configure()
        aep.replace('wf', TestWindFarm())
        wr = generate_random_GenericWindRoseVT()
        aep.wind_rose = wr.frequency_array
        aep.wind_speeds = wr.wind_speeds
        aep.wind_directions = wr.wind_directions        
        #print hasattr(aep.wf, 'execute')
        aep.execute()



class test_AEPMultipleWindRoses(unittest.TestCase):
    def test_init(self):
        aep = AEPMultipleWindRoses()

    def test_configure(self):
        aep = AEPMultipleWindRoses()
        aep.configure()
               




# class test_WWHAEP(unittest.TestCase):
#     def test_init(self):
#         wwh = WWHAEP()

#     def test_HR(self):
#         wwh = WWHAEP()
#         wwh.wind_rose_type = 'single'
#         wwh.configure()

#     def test_HR(self):
#         wwh = WWHAEP()
#         wwh.filename = '/Users/pire/git/FUSED-Wind/fusedwind_examples/src/fusedwind_examples/plant_flow/wind_farms/horns_rev/hornsrev1_turbine_nodescription.wwh'
#         wwh.wind_rose_type = 'single'
#         wwh.configure()
#         wwh.wind_rose_driver.sequential=True
#         wwh.replace('wf', noj.NOJWindFarmWake())
#         wwh.wf.wake_model.k = 0.04
#         wwh.filename = filename
#         wwh.wind_directions = linspace(0.0, 360.0, 14)[:-1]
#         wwh.wind_speeds = linspace(4.0, 25.0, 3)
#         wwh.execute()



if __name__ == '__main__':
    unittest.main()
