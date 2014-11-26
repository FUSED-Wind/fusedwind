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

class test_AEPMultipleWindRoses(unittest.TestCase):
    def test_init(self):
        aep = AEPMultipleWindRoses()

    def test_configure(self):
        aep = AEPMultipleWindRoses()
        aep.configure()



if __name__ == '__main__':
    unittest.main()
