# test_fused_plant_asym
from random import random
import unittest

from fusedwind.plant_flow.asym import *
from test_comp import TestWindFarm
from test_vt import generate_random_GenericWindRoseVT
from fusedwind.plant_flow.generate_fake_vt import generate_random_wt_layout
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
        aep.add('wf', TestWindFarm())
        #aep.run()
        #generate_inputs_AEPWindRose(aep)
        wr = generate_random_GenericWindRoseVT()
        aep.wind_rose = wr.frequency_array
        aep.wind_speeds = wr.wind_speeds
        aep.wind_directions = wr.wind_directions
        #aep.create_passthrough('wf.wt_layout')
        aep.wf.wt_layout = generate_random_wt_layout(nwt=50)
        aep.run()
        #print aep.net_aep, aep.gross_aep, aep.capacity_factor, aep.array_aep
        assert aep.net_aep > 0.0, 'net_aep hasn\'t been set properlyy: %f'%(aep.net_aep)
        # TODO: set make the gross_aep work properly
        #assert aep.gross_aep > 0.0, 'gross_aep hasn\'t been set properly: %f'%(aep.gross_aep)
        #assert aep.gross_aep < aep.net_aep, 'gross_aep or net_aep haven\'t been set properly: gross=%f, net=%f'%(aep.gross_aep, aep.net_aep)
        #assert aep.capacity_factor > 0.0 and aep.capacity_factor < 1.0, 'capacity factor is unrealistic: %f'%(aep.capacity_factor)

        #import ipdb; ipdb.set_trace()

class MyTestWindFarm(GenericWindFarm):
    def execute(self):
        self.wt_power = [random() * wt_desc.power_rating for wt_desc in self.wt_layout.wt_list()]
        self.wt_thrust = [pow_ / (random() * self.wind_speed) for pow_ in self.wt_power]
        self.power = sum(self.wt_power)
        self.thrust = sum(self.wt_thrust)

class test_AEPMultipleWindRoses(unittest.TestCase):
    def test_init(self):
        aep = AEPMultipleWindRoses()

    def test_configure(self):
        aep = AEPMultipleWindRoses()
        aep.configure()

    def test_execute(self):
        cG = AEPMultipleWindRoses()
        cG.add('wf', MyTestWindFarm())
        cG.configure()
        cG.connect('wt_layout', 'wf.wt_layout')
        cG.wind_speeds = np.linspace(4., 25., 10).tolist()
        cG.wind_directions = np.linspace(0., 360., 36)[:-1].tolist()
        nwt = 5
        cG.wt_layout = generate_random_wt_layout(nwt=nwt)
        cG.run()
        print cG.net_aep
        print cG.wt_aep

if __name__ == '__main__':
    unittest.main()

