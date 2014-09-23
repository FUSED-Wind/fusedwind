# test_fused_plant_asym
from random import random
import unittest

from fusedwind.plant_flow.fused_plant_asym import *


class test_GenericWindFarm(unittest.TestCase):
    def test_init(self):
        gwf = GenericWindFarm()
        gwf.wind_speed = random()*25.0
        gwf.wind_direction = random()*360.0
        gwf.wt_layout = GenericWindFarmTurbineLayout()

    def test_interface(self):
        pass


class DoNothing(GenericWindFarm):
    def execute(self):
        pass

class test_AEPSingleWindRose(unittest.TestCase):
    def test_init(self):
        aep = AEPSingleWindRose()

    def test_configure(self):
        aep = AEPSingleWindRose()
        aep.configure()
               
    def test_run(self):
        aep = AEPSingleWindRose()
        aep.configure()
        aep.replace('wf', DoNothing())
        aep.run()


class test_AEPMultipleWindRoses(unittest.TestCase):
    def test_init(self):
        aep = AEPMultipleWindRoses()

    def test_configure(self):
        aep = AEPMultipleWindRoses()
        aep.configure()
               
    def test_run(self):
        aep = AEPMultipleWindRoses()
        aep.configure()
        aep.replace('wf', DoNothing())
        aep.run()



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
