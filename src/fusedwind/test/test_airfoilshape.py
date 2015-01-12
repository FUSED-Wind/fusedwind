
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
       [  8.82891133e-01,   5.16191894e-03],
       [  7.54882760e-01,  -1.02148786e-02],
       [  6.22723184e-01,  -4.85683055e-02],
       [  4.86894075e-01,  -9.06682888e-02],
       [  3.46799119e-01,  -1.14104354e-01],
       [  2.09464507e-01,  -1.09210166e-01],
       [  8.55622327e-02,  -7.42299140e-02],
       [ -1.76645007e-05,  -2.90461132e-04],
       [  6.86615314e-02,   7.62906539e-02],
       [  1.62793179e-01,   1.10585475e-01],
       [  2.57082165e-01,   1.23982133e-01],
       [  3.48774470e-01,   1.24033961e-01],
       [  4.37977008e-01,   1.15764699e-01],
       [  5.25859274e-01,   1.02441284e-01],
       [  6.13892002e-01,   8.57640502e-02],
       [  7.03633270e-01,   6.67342432e-02],
       [  7.96756265e-01,   4.63150870e-02],
       [  8.94983538e-01,   2.52892803e-02],
       [  1.00000000e+00,   3.91000000e-03]])



p_data = np.array([[  1.00000000e+00,  -1.16953764e-02],
       [  8.83275627e-01,  -2.76480783e-03],
       [  7.64862711e-01,  -2.73052190e-02],
       [  6.49024890e-01,  -7.05503400e-02],
       [  5.32513948e-01,  -1.16591119e-01],
       [  4.11745800e-01,  -1.51982078e-01],
       [  2.87420663e-01,  -1.66129714e-01],
       [  1.64971884e-01,  -1.51580058e-01],
       [  5.65155967e-02,  -9.90657344e-02],
       [ -1.11239421e-05,   1.08221321e-03],
       [  4.85063741e-02,   9.87507233e-02],
       [  1.45297226e-01,   1.50863949e-01],
       [  2.53141991e-01,   1.67614634e-01],
       [  3.60910700e-01,   1.63139932e-01],
       [  4.66887406e-01,   1.47221036e-01],
       [  5.71691245e-01,   1.24860368e-01],
       [  6.76403553e-01,   9.89336408e-02],
       [  7.82035935e-01,   7.08379240e-02],
       [  8.89587762e-01,   4.17073644e-02],
       [  1.00000000e+00,   1.24853187e-02]])



c_data = np.array([[ 1.        , -0.01139629],
       [ 0.88371204, -0.00249974],
       [ 0.76643717, -0.02645713],
       [ 0.65224993, -0.06910307],
       [ 0.53780849, -0.11486276],
       [ 0.41920451, -0.15040165],
       [ 0.29653053, -0.16558872],
       [ 0.1746138 , -0.15310526],
       [ 0.06393289, -0.10447345],
       [-0.00632334, -0.00607019],
       [ 0.0429663 ,  0.09548886],
       [ 0.14102463,  0.14840235],
       [ 0.24955845,  0.16506053],
       [ 0.35805466,  0.16082599],
       [ 0.4648198 ,  0.14524597],
       [ 0.57039318,  0.12324329],
       [ 0.67575886,  0.09764582],
       [ 0.78183747,  0.06980652],
       [ 0.88959741,  0.04093319],
       [ 1.        ,  0.01212484]])



a_data = np.array([[ 1.        , -0.01140264],
       [ 0.88386342, -0.00251572],
       [ 0.76697489, -0.0263892 ],
       [ 0.65334563, -0.06886615],
       [ 0.5396049 , -0.11457373],
       [ 0.42173456, -0.15036555],
       [ 0.299622  , -0.16613305],
       [ 0.17788886, -0.154429  ],
       [ 0.06645677, -0.10689201],
       [-0.00845107, -0.00848367],
       [ 0.04030683,  0.09436619],
       [ 0.13865561,  0.14778317],
       [ 0.24754673,  0.16472739],
       [ 0.35644016,  0.16065225],
       [ 0.46360925,  0.14516339],
       [ 0.56956594,  0.12321128],
       [ 0.67526803,  0.09763562],
       [ 0.78160742,  0.0697801 ],
       [ 0.88953421,  0.04088378],
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

        self.assertEqual(np.testing.assert_array_almost_equal(af.LE, np.array([ -1.76645007e-05,  -2.90461132e-04]), decimal=6), None)
        self.assertAlmostEqual(af.sLE, 0.49898457668804924, places=6)
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
