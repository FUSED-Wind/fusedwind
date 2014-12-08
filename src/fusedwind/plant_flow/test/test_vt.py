import unittest
from unittest import TestCase
from fusedwind.plant_flow.vt import GenericWindTurbineVT, GenericWindTurbinePowerCurveVT, \
    ExtendedWindTurbinePowerCurveVT, WeibullWindRoseVT, GenericWindRoseVT, GenericWindFarmTurbineLayout, WTPC, \
    weibull2freq_array
from fusedwind.plant_flow.comp import WeibullWindRose
from fusedwind.fused_helper import init_container
from fusedwind.plant_flow.generate_fake_vt import *

from random import random
from numpy import array, vstack, linspace, pi, floor
import numpy as np
from numpy import ndarray, array, loadtxt, log, zeros, cos, arccos, sin, nonzero, argsort, NaN, mean, ones, vstack, \
    linspace, exp, arctan, arange
from numpy import pi, sqrt, dot, diff
from numpy.testing import assert_array_almost_equal, assert_almost_equal


wr_inputs = {
        'wind_directions': [0., 30., 60., 90., 120., 150., 180., 210., 240., 270., 300., 330.],
        'wind_speeds': [4., 5., 6., 7., 8., 9., 10., 11., 12., 13., 14., 15., 16., 17., 18., 19., 20., 21., 22., 23., 24.,
                        25.],
        'weibull_array': array(
            [[0.00000000e+00, 3.59550200e-02, 9.22421500e+00, 2.38867200e+00],
             [3.00000000e+01, 3.94968400e-02, 9.88496400e+00, 2.44726600e+00],
             [6.00000000e+01, 5.19472500e-02, 9.67463200e+00, 2.43164100e+00],
             [9.00000000e+01, 7.01142500e-02, 1.00520300e+01, 2.60351600e+00],
             [1.20000000e+02, 8.36171100e-02, 1.01233300e+01, 2.75585900e+00],
             [1.50000000e+02, 6.43188100e-02, 9.64359200e+00, 2.59179700e+00],
             [1.80000000e+02, 8.63938000e-02, 9.63384700e+00, 2.58007800e+00],
             [2.10000000e+02, 1.17646400e-01, 1.05676900e+01, 2.54492200e+00],
             [2.40000000e+02, 1.51493800e-01, 1.14521200e+01, 2.46679700e+00],
             [2.70000000e+02, 1.47303000e-01, 1.17420100e+01, 2.60351600e+00],
             [3.00000000e+02, 1.00075900e-01, 1.16922200e+01, 2.62304700e+00],
             [3.30000000e+02, 5.16379700e-02, 1.01387300e+01, 2.32226600e+00]])}

wr_result = array(
        [[1.44588988e-03, 3.35727582e-03, 3.81029809e-03, 4.02470558e-03, 3.98990151e-03, 3.73046644e-03,
          3.29906324e-03, 2.76423767e-03, 2.19642754e-03, 1.65575871e-03, 1.18426976e-03, 8.03545915e-04,
          5.17057409e-04, 3.15388270e-04, 1.82265836e-04, 9.97392412e-05, 5.16484433e-05, 2.52926787e-05,
          1.17053815e-05, 5.11599317e-06, 2.11020415e-06, 5.08752361e-07],
         [1.30490339e-03, 3.09884391e-03, 3.62718954e-03, 3.96056671e-03, 4.06990314e-03, 3.95614496e-03,
          3.64866956e-03, 3.19840948e-03, 2.66737868e-03, 2.11724064e-03, 1.59962624e-03, 1.15013583e-03,
          7.86692880e-04, 5.11652765e-04, 3.16234066e-04, 1.85620497e-04, 1.03401615e-04, 5.46258501e-05,
          2.73472412e-05, 1.29640581e-05, 5.81491675e-06, 1.50264971e-06],
         [1.77962417e-03, 4.19952053e-03, 4.87241564e-03, 5.26922670e-03, 5.35765892e-03, 5.14772140e-03,
          4.68765926e-03, 4.05270640e-03, 3.32955013e-03, 2.60048377e-03, 1.93096518e-03, 1.36289927e-03,
          9.14038683e-04, 5.82191700e-04, 3.51980669e-04, 2.01858052e-04, 1.09736471e-04, 5.65096359e-05,
          2.75447988e-05, 1.26991432e-05, 5.53343327e-06, 1.39586432e-06],
         [2.03574440e-03, 4.98929943e-03, 6.05198952e-03, 6.80997401e-03, 7.17340152e-03, 7.10897476e-03,
          6.64589168e-03, 5.86836208e-03, 4.89625745e-03, 3.85928948e-03, 2.87201235e-03, 2.01614762e-03,
          1.33368507e-03, 8.30343766e-04, 4.85929034e-04, 2.66934444e-04, 1.37448038e-04, 6.62437807e-05,
          2.98390332e-05, 1.25432885e-05, 4.91332268e-06, 1.12525886e-06],
         [2.15186806e-03, 5.43110528e-03, 6.80657106e-03, 7.86793420e-03, 8.46630869e-03, 8.52083209e-03,
          8.03827862e-03, 7.11211238e-03, 5.89954420e-03, 4.58318141e-03, 3.32962029e-03, 2.25796289e-03,
          1.42643914e-03, 8.37636776e-04, 4.56170072e-04, 2.29844137e-04, 1.06885088e-04, 4.57615873e-05,
          1.79926754e-05, 6.48041565e-06, 2.13264517e-06, 4.17265933e-07],
         [2.24784777e-03, 5.46088720e-03, 6.53473087e-03, 7.23314626e-03, 7.47069754e-03, 7.23396208e-03,
          6.58303613e-03, 5.63593453e-03, 4.54016275e-03, 3.44009748e-03, 2.44976880e-03, 1.63787627e-03,
          1.02684668e-03, 6.02850400e-04, 3.30951610e-04, 1.69634591e-04, 8.10558227e-05, 3.60483982e-05,
          1.48978462e-05, 5.71209909e-06, 2.02861392e-06, 4.27007926e-07],
         [2.84919811e-03, 6.90561292e-03, 8.24189952e-03, 9.10295837e-03, 9.38562803e-03, 9.07665485e-03,
          8.25355050e-03, 7.06455491e-03, 5.69322871e-03, 4.31834242e-03, 3.08069972e-03, 2.06505246e-03,
          1.29914820e-03, 7.66078219e-04, 4.22840120e-04, 2.18143544e-04, 1.05033331e-04, 4.71273715e-05,
          1.96750146e-05, 7.63101473e-06, 2.74537834e-06, 5.84660929e-07],
         [3.15103170e-03, 7.69357254e-03, 9.33336956e-03, 1.05666829e-02, 1.12688451e-02, 1.13813576e-02,
          1.09204112e-02, 9.97189992e-03, 8.67355879e-03, 7.18843635e-03, 5.67618809e-03, 4.26887875e-03,
          3.05612657e-03, 2.08130177e-03, 1.34730899e-03, 8.28320491e-04, 4.83210345e-04, 2.67221613e-04,
          1.39953406e-04, 6.93493727e-05, 3.24798328e-05, 8.68186021e-06],
         [3.38534246e-03, 8.22612132e-03, 9.98196140e-03, 1.13899884e-02, 1.23378363e-02, 1.27597240e-02,
          1.26435937e-02, 1.20308435e-02, 1.10083382e-02, 9.69411732e-03, 8.21957641e-03, 6.71153300e-03,
          5.27736822e-03, 3.99546450e-03, 2.91176859e-03, 2.04191583e-03, 1.37732536e-03, 8.93223652e-04,
          5.56674970e-04, 3.33229170e-04, 1.91495304e-04, 6.08835103e-05],
         [2.87303824e-03, 7.17906769e-03, 8.99864707e-03, 1.05685790e-02, 1.17476848e-02, 1.24323246e-02,
          1.25706437e-02, 1.21697691e-02, 1.12938057e-02, 1.00525910e-02, 8.58338998e-03, 7.02938634e-03,
          5.51945197e-03, 4.15307210e-03, 2.99270142e-03, 2.06379390e-03, 1.36094123e-03, 8.57478070e-04,
          5.15753711e-04, 2.95876874e-04, 1.61746247e-04, 4.91779082e-05],
         [2.02163959e-03, 5.06769635e-03, 6.37296122e-03, 7.50260428e-03, 8.35231542e-03, 8.84484216e-03,
          8.94099994e-03, 8.64540798e-03, 8.00521430e-03, 7.10171159e-03, 6.03649545e-03, 4.91515685e-03,
          3.83200463e-03, 2.85882995e-03, 2.03944379e-03, 1.39010175e-03, 9.04514324e-04, 5.61332477e-04,
          3.31930481e-04, 1.86840603e-04, 1.00013602e-04, 2.98627202e-05],
         [1.76963956e-03, 4.12232356e-03, 4.73613444e-03, 5.11273708e-03, 5.23107828e-03, 5.09941651e-03,
          4.75207060e-03, 4.24236873e-03, 3.63329069e-03, 2.98774782e-03, 2.36035193e-03, 1.79197095e-03,
          1.30756674e-03, 9.17018472e-04, 6.18067439e-04, 4.00285013e-04, 2.49050823e-04, 1.48827861e-04,
          8.53960207e-05, 4.70346524e-05, 2.48592270e-05, 7.39661364e-06]])


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
        gwr = GenericWindRoseVT(**wr_inputs)
        assert_almost_equal(gwr.frequency_array, wr_result)

    def test_init_default(self):
        gwr = GenericWindRoseVT(weibull_array=wr_inputs['weibull_array'])
        assert_almost_equal(gwr.wind_speeds, array([  4.,   5.,   6.,   7.,   8.,   9.,  10.,  11.,  12.,  13.,  14.,
                    15.,  16.,  17.,  18.,  19.,  20.,  21.,  22.,  23.,  24.,  25.]))
        assert_almost_equal(gwr.wind_directions, gwr.weibull_array[:,0])

    def test_change_resolution(self):
        gwr = GenericWindRoseVT(**wr_inputs)
        nws = int(random()*25)
        nwd = int(random()*360)
        new_wind_directions = np.linspace(0., 360., nwd)
        new_wind_speeds = np.linspace(4., 25., nws)
        gwr.change_resolution(wind_directions=new_wind_directions, wind_speeds=new_wind_speeds)
        assert_almost_equal(gwr.frequency_array.shape, [nwd, nws])
        assert_almost_equal(gwr.wind_directions, new_wind_directions)
        assert_almost_equal(gwr.wind_speeds, new_wind_speeds)



class test_GenericWindFarmTurbineLayout(unittest.TestCase):
    def test_init(self):
        gwf = GenericWindFarmTurbineLayout()

    def test_random(self):
        #gwf = generate_random_wt_layout(nwt=10)
        pass


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


class TestGenericWindFarmTurbineLayout(TestCase):
    def setUp(self):
        self.wtl = generate_random_wt_layout(nwt=10)

    def test_add_wt(self):
        name = 'new_WTPC'
        self.wtl.add_wt(generate_random_WTPC(name=name))
        self.assertTrue(name in self.wtl.wt_names)
        self.assertIsInstance(getattr(self.wtl, name), WTPC)

    def test_wt_list(self):
        self.assertEqual(self.wtl._wt_list('name'), self.wtl.wt_names)

    def test_wt_array(self):
        assert_almost_equal(self.wtl.wt_array('position').shape, [self.wtl.n_wt, 2])

    def test_n_wt(self):
        self.assertEqual(self.wtl.n_wt, self.wtl.wt_positions.shape[0])

    def test_wt_positions(self):
        assert_almost_equal(self.wtl.wt_array('position'), self.wtl.wt_positions)

    def test_wt_wind_roses(self):
        self.assertIsInstance(self.wtl.wt_wind_roses, list)

    def test_create_dict(self):
        dic = self.wtl.create_dict(0)
        # TODO:
        # - make sure that the dictionary is well formatted
        pass

    def test_df(self):
        df = self.wtl.df
        # TODO:
        # - figure out what to test
        pass

    def test_update_positions(self):
        new_position = generate_random_wt_positions(D=self.wtl.wt_array('rotor_diameter').max(), nwt=self.wtl.n_wt)
        self.wtl.wt_positions = new_position
        assert_almost_equal(new_position, self.wtl.wt_positions, err_msg='The new position has not been updated')


if __name__ == '__main__':
    unittest.main()



class TestWeibull2freq_array(TestCase):


    def test_func(self):
        c = weibull2freq_array(**wr_inputs)
        np.testing.assert_array_almost_equal(c, wr_result)