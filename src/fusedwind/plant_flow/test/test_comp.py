import unittest
from unittest import TestCase
from numpy.testing import assert_equal
from fusedwind.plant_flow.comp import *
from fusedwind.fused_helper import *
from fusedwind.plant_flow.vt import GenericWindTurbineVT, GenericWindTurbinePowerCurveVT
from fusedwind.plant_flow.generate_fake_vt import generate_random_GenericWindTurbinePowerCurveVT, \
    generate_random_wt_positions, generate_random_GenericWindRoseVT, generate_random_wt_layout, \
    generate_a_valid_wt
import numpy as np
from random import random, randint
from numpy import array, vstack, linspace

wr_inputs = {
    'wind_directions': [0., 30., 60., 90., 120., 150., 180., 210., 240., 270., 300., 330.],
    'wind_speeds': [4., 5., 6., 7., 8., 9., 10., 11., 12., 13., 14., 15., 16., 17., 18., 19., 20., 21., 22., 23., 24.,
                    25.],
    'wind_rose_array': array(
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

wr_result = {
    'wind_directions': [0., 30., 60., 90., 120., 150., 180., 210., 240., 270., 300., 330.],
    'wind_speeds': [4., 5., 6., 7., 8., 9., 10., 11., 12., 13., 14., 15., 16., 17., 18., 19., 20., 21., 22., 23., 24.,
                    25.],
    'frequency_array': array(
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
          8.53960207e-05, 4.70346524e-05, 2.48592270e-05, 7.39661364e-06]])}

def generate_random_inflow(opt=randint(0,2)):
    if  opt == 0:
        in_log = LogLawInflowGenerator()
        in_log.wind_speed = 50.*random()
        in_log.z_ref = 150.*random()
        in_log.ws_positions = array([[0.,0.,50.],[0.,0.,100.],[0.,0.,1000.]])
        in_log.z_0 = 0.5*random()
        L = 12000.*(random()-0.5)*2.
        in_log.L = NaN*((L>0)&(L<12000)) + L*((L<0)|(L>12000))
        in_log.stab_term = 0
        in_log.run()
        return in_log

    elif opt == 1:
        in_log = LogLawInflowGenerator()
        in_log.wind_speed = 50.*random()
        in_log.z_ref = 150.*random()
        in_log.ws_positions = array([[0.,0.,50.],[0.,0.,100.],[0.,0.,1000.]])
        in_log.z_0 = 0.5*random()
        L = 20000.*(random()-0.5)*2.
        in_log.L = NaN*((L>=0)&(L<20000)) + L*((L<0)|(L>20000))
        in_log.stab_term = 1
        in_log.run()
        return in_log

    elif opt == 2:
        in_pl = PowerLawInflowGenerator()
        in_pl.wind_speed = 50.*random()
        in_pl.z_ref = 150.*random()
        in_pl.ws_positions = array([[0.,0.,50.],[0.,0.,100.],[0.,0.,1000.]])
        in_pl.shear_coef = 0.5*(random()-0.5)
        in_pl.run()
        return in_pl

class TestWindFarm(GenericWindFarm):
    def execute(self):
        self.wt_power = [random() * wt_desc.power_rating for wt_desc in self.wt_layout.wt_list]
        self.wt_thrust = [pow_ / (random() * self.wind_speed) for pow_ in self.wt_power]
        self.power = sum(self.wt_power)
        self.thrust = sum(self.wt_thrust)


class test_GenericWindFarm(unittest.TestCase):
    def fill_up(self, gwf):
        """Fill up a generic windfarm with random inputs"""
        gwf.wind_speed = random() * 25.0
        gwf.wind_direction = random() * 360.0
        gwf.wt_layout = generate_random_wt_layout()

    def test_init(self):
        gwf = GenericWindFarm()
        self.fill_up(gwf)

    def test_execution(self):
        """Test the execution of a generic wind farm"""
        gwf = TestWindFarm()
        self.fill_up(gwf)
        gwf.run()


class test_WeibullWindRose(unittest.TestCase):
    def test_init(self):
        c = WeibullWindRose()
        init_container(c, **wr_inputs)

    def test_run(self):
        c = WeibullWindRose()
        init_container(c, **wr_inputs)
        c.run()
        # Testing that the output wind_rose is equal to the wr_result dictionary
        for k, v in wr_result.iteritems():
            np.testing.assert_array_almost_equal(getattr(c.wind_rose, k), v)

    def test_random(self):
        wind_rose = generate_random_GenericWindRoseVT()


class test_GenericWSPosition(unittest.TestCase):
    def test_init(self):
        c = GenericWSPosition()

class test_HubCenterWSPosition(unittest.TestCase):
    def test_init(self):
        c = HubCenterWSPosition()

    def test_execute(self):
        HC = HubCenterWSPosition()
        HC.wt_desc = generate_a_valid_wt()
        HC.run()

class test_GaussLegendreQuadratureWSPosition(unittest.TestCase):
    def test_init(self):
        c = GaussLegendreQuadratureWSPosition()

    def test_execute(self):
        GLQ = GaussLegendreQuadratureWSPosition()
        GLQ.wt_desc = generate_a_valid_wt()
        GLQ.degree = randint(2,15)
        GLQ.run()

class test_GenericHubWindSpeed(unittest.TestCase):
    def test_init(self):
        c = GenericHubWindSpeed()

class test_AreaAveragedWindSpeed(unittest.TestCase):
    def test_init(self):
        c = AreaAveragedWindSpeed()
    def test_execute(self):
        GLQ = GaussLegendreQuadratureWSPosition()
        GLQ.wt_desc = generate_a_valid_wt()
        GLQ.degree = randint(2,15)
        GLQ.run()

        inflow = generate_random_inflow()
        inflow.ws_positions = GLQ.ws_positions
        inflow.run()

        AvgWS = AreaAveragedWindSpeed()
        AvgWS.ws_array = inflow.ws_array
        AvgWS.weights = GLQ.weights
        AvgWS.run()

class test_ThrustEquivalentWindSpeed(unittest.TestCase):
    def test_init(self):
        c = ThrustEquivalentWindSpeed()
    def test_execute(self):
        GLQ = GaussLegendreQuadratureWSPosition()
        GLQ.wt_desc = generate_a_valid_wt()
        GLQ.degree = randint(2,15)
        GLQ.run()

        inflow = generate_random_inflow()
        inflow.ws_positions = GLQ.ws_positions
        inflow.run()

        eqT_WS = ThrustEquivalentWindSpeed()
        eqT_WS.ws_array = inflow.ws_array
        eqT_WS.weights  = GLQ.weights
        eqT_WS.run()

class test_PowerEquivalentWindSpeed(unittest.TestCase):
    def test_init(self):
        c = PowerEquivalentWindSpeed()
    def test_execute(self):
        GLQ = GaussLegendreQuadratureWSPosition()
        GLQ.wt_desc = generate_a_valid_wt()
        GLQ.degree = randint(2,15)
        GLQ.run()

        inflow = generate_random_inflow()
        inflow.ws_positions = GLQ.ws_positions
        inflow.run()

        eqP_WS = PowerEquivalentWindSpeed()
        eqP_WS.ws_array = inflow.ws_array
        eqP_WS.weights  = GLQ.weights
        eqP_WS.run()


class test_GenericWakeSum(unittest.TestCase):
    def test_init(self):
        c = GenericWakeSum()

class test_LinearWakeSum(unittest.TestCase):
    def test_init(self):
        c = LinearWakeSum()

class test_QuadraticWakeSum(unittest.TestCase):
    def test_init(self):
        c = QuadraticWakeSum()

class test_ARLWakeSum(unittest.TestCase):
    def test_init(self):
        c = ARLWakeSum()

class test_MaxWakeSum(unittest.TestCase):
    def test_init(self):
        c = MaxWakeSum()


class test_GenericFlowModel(unittest.TestCase):
    def test_init(self):
        c = GenericFlowModel()


class test_GenericInflowGenerator(unittest.TestCase):
    def test_init(self):
        c = GenericInflowGenerator()


class test_PowerLawInflowGenerator(unittest.TestCase):
    def test_init(self):
        c = GenericInflowGenerator()

    def test_execute(self):
        in_pl = PowerLawInflowGenerator()
        in_pl.wind_speed = 10.
        in_pl.z_ref = 100.
        in_pl.ws_positions = array([[0.,0.,0.],[0.,0.,100.],[0.,0.,1000.]])
        in_pl.shear_coef = 0.1
        in_pl.run()
        np.testing.assert_array_almost_equal(in_pl.ws_array,array([0.,10.,10.**1.1]))

        in_pl2 = PowerLawInflowGenerator()
        in_pl2.wind_speed = 50.*random()
        in_pl2.z_ref = 200.*random()
        in_pl2.ws_positions = array([[0.,0.,0.],[0.,0.,100.*random()],[0.,0.,1000.*random()]])
        in_pl2.shear_coef = 0.5*(random() - 0.5)
        in_pl2.run()


class test_LogLawInflowGenerator(unittest.TestCase):
    def test_init(self):
        c = LogLawInflowGenerator()

    def test_execute(self):
        in_log = LogLawInflowGenerator()
        in_log.wind_speed = 10.
        in_log.z_ref = 100.
        in_log.ws_positions = array([[0.,0.,50.],[0.,0.,100.],[0.,0.,1000.]])
        in_log.z_0 = 0.0002
        in_log.L = NaN
        in_log.run()
        np.testing.assert_array_almost_equal(in_log.ws_array,array([9.47178175,10.,11.75470304]))


        in_log2 = LogLawInflowGenerator()
        in_log2.wind_speed = 10.
        in_log2.z_ref = 100.
        in_log2.ws_positions = array([[0.,0.,50.],[0.,0.,100.],[0.,0.,1000.]])
        in_log2.z_0 = 0.0002
        in_log2.L = 20000
        in_log2.stab_term = 0
        in_log2.run()
        np.testing.assert_array_almost_equal(in_log2.ws_array,array([9.46378784,10.,11.91245339]))

        in_log2 = LogLawInflowGenerator()
        in_log2.wind_speed = 10.
        in_log2.z_ref = 100.
        in_log2.ws_positions = array([[0.,0.,50.],[0.,0.,100.],[0.,0.,1000.]])
        in_log2.z_0 = 0.0002
        in_log2.L = -1000
        in_log2.stab_term = 0
        in_log2.run()
        np.testing.assert_array_almost_equal(in_log2.ws_array,array([9.56011479,10.,11.06759567]))

        in_log3 = LogLawInflowGenerator()
        in_log3.wind_speed = 10.
        in_log3.z_ref = 100.
        in_log3.ws_positions = array([[0.,0.,50.],[0.,0.,100.],[0.,0.,1000.]])
        in_log3.z_0 = 0.0002
        in_log3.L = 20000
        in_log3.stab_term = 1
        in_log3.run()
        np.testing.assert_array_almost_equal(in_log3.ws_array,array([9.46361807,10.,11.91580365]))

        in_log3 = LogLawInflowGenerator()
        in_log3.wind_speed = 10.
        in_log3.z_ref = 100.
        in_log3.ws_positions = array([[0.,0.,50.],[0.,0.,100.],[0.,0.,1000.]])
        in_log3.z_0 = 0.0002
        in_log3.L = -1000
        in_log3.stab_term = 1
        in_log3.run()
        np.testing.assert_array_almost_equal(in_log3.ws_array,array([9.57125298,10.,11.02583296]))


class test_GenericWakeModel(unittest.TestCase):
    def test_init(self):
        c = GenericWakeModel()


class test_GenericWindTurbine(unittest.TestCase):
    def test_init(self):
        c = GenericWindTurbine()


class test_WindTurbinePowerCurve(unittest.TestCase):
    def test_init(self):
        c = WindTurbinePowerCurve()
        c.wt_desc = generate_random_GenericWindTurbinePowerCurveVT()
        for ws, power in c.wt_desc.power_curve:
            np.testing.assert_almost_equal(c(hub_wind_speed=ws).power, power)


class test_GenericWindRoseCaseGenerator(unittest.TestCase):
    def test_init(self):
        c = GenericWindRoseCaseGenerator()


class TestBaseAEPAggregator(TestCase):
    pass


class TestWeibullWindRose(TestCase):
    def test_execute(self):
        pass


class TestMultipleWindRosesCaseGenerator(unittest.TestCase):
    def test_execute(self):
        # Preparing inputs
        cG = MultipleWindRosesCaseGenerator()
        cG.wind_speeds = np.linspace(4., 25., 22).tolist()
        cG.wind_directions = np.linspace(0., 360., 36)[:-1].tolist()
        nwt = 5
        cG.wt_layout = generate_random_wt_layout(nwt=nwt)
        cG.run()
        nwd, nws = len(cG.wind_directions), len(cG.wind_speeds)
        self.assertEqual(len(cG.all_wind_speeds), nws * nwd)
        self.assertEqual(len(cG.all_wind_directions), nws * nwd)
        self.assertEqual(len(cG.all_frequencies), nws * nwd)
        self.assertEqual(len(cG.all_frequencies[0]), nwt)


class TestPostProcessMultipleWindRoses(unittest.TestCase):
    def test_execute(self):
        cG = MultipleWindRosesCaseGenerator()
        cG.wind_speeds = np.linspace(4., 25., 22).tolist()
        cG.wind_directions = np.linspace(0., 360., 36)[:-1].tolist()
        nwt = 5
        cG.wt_layout = generate_random_wt_layout(nwt=nwt)
        cG.run()

        cP = PostProcessMultipleWindRoses()
        cP.wind_directions = cG.wind_directions
        cP.wind_speeds = cG.wind_speeds
        cP.frequencies = cG.all_frequencies
        cP.powers = [[random()*2.E6 for iwt in range(nwt)] for i in cG.all_wind_speeds]
        cP.run()
        assert_equal(cP.array_aep.shape, [len(cP.wind_directions), len(cP.wind_speeds)])



if __name__ == '__main__':
    unittest.main()

