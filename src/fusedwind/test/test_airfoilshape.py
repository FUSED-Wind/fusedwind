
import numpy as np
import unittest
import pkg_resources
import os

from fusedwind.turbine.geometry_vt import AirfoilShape, BlendAirfoilShapes

PATH = pkg_resources.resource_filename('fusedwind', 'test')

afs = []
for f in [os.path.join(PATH, 'data/ffaw3241.dat'),
          os.path.join(PATH, 'data/ffaw3301.dat'),
          os.path.join(PATH, 'data/ffaw3360.dat')]:

    afs.append(np.loadtxt(f))

aff_data = np.array([[  1.00000000e+00,  -3.60000000e-03],
       [  8.82890388e-01,   5.16190373e-03],
       [  7.54879899e-01,  -1.02155093e-02],
       [  6.22717224e-01,  -4.85702866e-02],
       [  4.86884116e-01,  -9.06708656e-02],
       [  3.46784860e-01,  -1.14105344e-01],
       [  2.09447054e-01,  -1.09207576e-01],
       [  8.55441271e-02,  -7.42218292e-02],
       [ -1.76360545e-05,  -2.69735983e-04],
       [  6.86792155e-02,   7.63001512e-02],
       [  1.62811412e-01,   1.10589726e-01],
       [  2.57098876e-01,   1.23983175e-01],
       [  3.48788779e-01,   1.24033193e-01],
       [  4.37988578e-01,   1.15763237e-01],
       [  5.25868053e-01,   1.02439764e-01],
       [  6.13898120e-01,   8.57628051e-02],
       [  7.03637013e-01,   6.67334277e-02],
       [  7.96758075e-01,   4.63146919e-02],
       [  8.94984030e-01,   2.52891775e-02],
       [  1.00000000e+00,   3.91000000e-03]])


p_data = np.array([[  1.00000000e+00,  -1.16953764e-02],
       [  8.83277263e-01,  -2.76462512e-03],
       [  7.64868577e-01,  -2.73031395e-02],
       [  6.49036798e-01,  -7.05450707e-02],
       [  5.32533789e-01,  -1.16583705e-01],
       [  4.11774921e-01,  -1.51975791e-01],
       [  2.87458560e-01,  -1.66129904e-01],
       [  1.65014862e-01,  -1.51594279e-01],
       [  5.65516372e-02,  -9.91079110e-02],
       [ -1.11331235e-05,   1.03149773e-03],
       [  4.84651017e-02,   9.87140832e-02],
       [  1.45244888e-01,   1.50849519e-01],
       [  2.53093828e-01,   1.67613257e-01],
       [  3.60871166e-01,   1.63143939e-01],
       [  4.66857419e-01,   1.47226388e-01],
       [  5.71670501e-01,   1.24864985e-01],
       [  6.76391046e-01,   9.89367294e-02],
       [  7.82030029e-01,   7.08394639e-02],
       [  8.89586210e-01,   4.17077780e-02],
       [  1.00000000e+00,   1.24853187e-02]])


c_data = np.array([[ 1.        , -0.01139629],
       [ 0.88371343, -0.00249959],
       [ 0.76644217, -0.02645545],
       [ 0.65226009, -0.06909875],
       [ 0.53782542, -0.11485668],
       [ 0.41922934, -0.15039667],
       [ 0.29656273, -0.16558905],
       [ 0.17465017, -0.15311583],
       [ 0.06396195, -0.10450251],
       [-0.00632498, -0.00611201],
       [ 0.04293787,  0.09545881],
       [ 0.14098825,  0.14839051],
       [ 0.24952501,  0.16505946],
       [ 0.3580272 ,  0.16082924],
       [ 0.46479889,  0.14525026],
       [ 0.57037858,  0.12324697],
       [ 0.67574992,  0.09764828],
       [ 0.78183316,  0.06980775],
       [ 0.88959624,  0.04093352],
       [ 1.        ,  0.01212484]])


a_data = np.array([[ 1.        , -0.01140264],
       [ 0.88386472, -0.00251559],
       [ 0.76697958, -0.02638764],
       [ 0.65335516, -0.06886211],
       [ 0.5396208 , -0.11456806],
       [ 0.42175785, -0.15036095],
       [ 0.29965217, -0.16613346],
       [ 0.17792287, -0.154439  ],
       [ 0.06648337, -0.10691944],
       [-0.00845325, -0.00852234],
       [ 0.04028011,  0.09433847],
       [ 0.13862165,  0.14777227],
       [ 0.24751554,  0.16472644],
       [ 0.35641456,  0.16065528],
       [ 0.46358976,  0.14516738],
       [ 0.56955233,  0.1232147 ],
       [ 0.6752597 ,  0.09763791],
       [ 0.7816034 ,  0.06978124],
       [ 0.88953312,  0.04088409],
       [ 1.        ,  0.01211567]])


def pchip_interpolator():

    b = BlendAirfoilShapes()
    b.airfoil_list = afs
    b.ni = 20
    b.blend_var = [0.241, 0.301, 0.36]
    b.spline = 'pchip'
    b.initialize()
    return b

def cubic_interpolator():
    b = BlendAirfoilShapes()
    b.airfoil_list = afs
    b.ni = 20
    b.blend_var = [0.241, 0.301, 0.36]
    b.spline = 'cubic'
    b.initialize()
    return b

def akima_interpolator():

    b = BlendAirfoilShapes()
    b.airfoil_list = afs
    b.ni = 20
    b.blend_var = [0.241, 0.301, 0.36]
    b.spline = 'akima'
    b.initialize()
    return b


class BlendAirfoilTest(unittest.TestCase):

    def test_airfoilshape(self):

        af = AirfoilShape(afs[0])
        aff = af.redistribute(20, even=True)

        self.assertEqual(np.testing.assert_array_almost_equal(af.LE, np.array([ -1.76360545e-05,  -2.69735983e-04]), decimal=6), None)
        self.assertAlmostEqual(af.sLE, 0.49899432317189191, places=6)
        self.assertEqual(np.testing.assert_array_almost_equal(aff.points, aff_data, decimal=6), None)

    def test_pchip(self):

        b = pchip_interpolator()
        p = b(.33)
        self.assertEqual(np.testing.assert_array_almost_equal(p, p_data, decimal=6), None)

    def test_cubic(self):

        b = cubic_interpolator()
        p = b(.33)
        self.assertEqual(np.testing.assert_array_almost_equal(p, c_data, decimal=6), None)

    def test_akima(self):

        b = akima_interpolator()
        p = b(.33)
        self.assertEqual(np.testing.assert_array_almost_equal(p, a_data, decimal=6), None)


if __name__ == '__main__':

    unittest.main()
