import unittest
from fusedwind.plant_flow.vt import GenericWindTurbineVT, GenericWindTurbinePowerCurveVT, \
    ExtendedWindTurbinePowerCurveVT, WeibullWindRoseVT, GenericWindRoseVT, GenericWindFarmTurbineLayout
from fusedwind.plant_flow.comp import WeibullWindRose
from fusedwind.fused_helper import init_container
from fusedwind.plant_flow.generate_fake_vt import *

from random import random
from numpy import array, vstack, linspace, pi, floor
import numpy as np
from numpy import ndarray, array, loadtxt, log, zeros, cos, arccos, sin, nonzero, argsort, NaN, mean, ones, vstack, linspace, exp, arctan, arange
from numpy import pi, sqrt, dot, diff
from numpy.testing import assert_array_almost_equal, assert_almost_equal


class test_GenericWindTurbineVT(unittest.TestCase):

    def test_init(self):
        gwt = GenericWindTurbineVT()


class test_GenericWindTurbinePowerCurveVT(unittest.TestCase):

    def test_init(self):
        gwtpc = GenericWindTurbinePowerCurveVT()

    def test_random(self):
        wt = generate_random_GenericWindTurbinePowerCurveVT()
        wt.test_consistency()


class test_ExtendedWindTurbinePowerCurveVT(unittest.TestCase):

    def test_init(self):
        ewtpc = ExtendedWindTurbinePowerCurveVT()


class test_GenericWindRoseVT(unittest.TestCase):

    def test_init(self):
        gwr = GenericWindRoseVT()
        init_container(gwr, **wr_example)

    def test_random(self):
        gwr = GenericWindRoseVT()


class test_GenericWindFarmTurbineLayout(unittest.TestCase):

    def test_init(self):
        gwf = GenericWindFarmTurbineLayout()

    def test_random(self):
        gwf = generate_random_wt_layout()


class test_WeibullWindRoseVT(unittest.TestCase):

    def random_fill_up(self, wwr):
        wwr.wind_directions = np.linspace(
            0., 360, np.random.randint(360))[:-1].tolist()
        wwr.k = [random() * 3 for w in wwr.wind_directions]
        wwr.A = [random() * 25 for w in wwr.wind_directions]
        normalise = lambda l: (array(l) / sum(l)).tolist()
        wwr.frequency = normalise([random() for w in wwr.wind_directions])

    def test_to_weibull_array(self):
        wwr = WeibullWindRoseVT()
        self.random_fill_up(wwr)
        arr = wwr.to_weibull_array()
        assert_array_almost_equal(arr[:, 0], wwr.wind_directions)
        assert_array_almost_equal(arr[:, 1], wwr.frequency)
        assert_array_almost_equal(arr[:, 2], wwr.A)
        assert_array_almost_equal(arr[:, 3], wwr.k)
        assert_almost_equal(arr[:, 1].sum(), 1.0)

    def test_df(self):
        wwr = WeibullWindRoseVT()
        self.random_fill_up(wwr)
        df = wwr.df()
        self.assertEqual(
            df.columns.tolist(), ['wind_direction', 'frequency', 'A', 'k'])

    # def test_to_wind_rose(self):
    #    from test_comp import wr_inputs, wr_result
    #    wwr = WeibullWindRoseVT()
    #    wwr.wind_directions = wr_inputs['wind_rose_array'][:,0]
    #    wwr.frequency = wr_inputs['wind_rose_array'][:,1]
    #    wwr.A = wr_inputs['wind_rose_array'][:,2]
    #    wwr.k = wr_inputs['wind_rose_array'][:,3]
    #    wr = wwr.to_wind_rose(wind_directions=wr_inputs['wind_directions'],
    #                          wind_speeds=wr_inputs['wind_speeds'])
    #    assert_array_almost_equal(wr.frequency_array, wr_result['frequency_array'])


if __name__ == '__main__':
    unittest.main()
