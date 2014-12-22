
import numpy as np
import unittest
import pkg_resources
import os

from fusedwind.turbine.airfoil_vt import AirfoilShape, BlendAirfoilShapes

PATH = pkg_resources.resource_filename('fusedwind', 'test')

afs = []
for f in [os.path.join(PATH, 'data/ffaw3241.dat'),
          os.path.join(PATH, 'data/ffaw3301.dat'),
          os.path.join(PATH, 'data/ffaw3360.dat')]:

    afs.append(np.loadtxt(f))

aff_data = np.array([[  1.00000000e+00,  -3.60000000e-03],
       [  8.91572619e-01,   5.27395639e-03],
       [  7.77423691e-01,  -5.63034185e-03],
       [  6.62060653e-01,  -3.57195934e-02],
       [  5.46011920e-01,  -7.36722578e-02],
       [  4.26820676e-01,  -1.03965506e-01],
       [  3.05429399e-01,  -1.15716194e-01],
       [  1.86766408e-01,  -1.05356084e-01],
       [  7.76571314e-02,  -7.05894544e-02],
       [ -1.76360545e-05,  -2.69735983e-04],
       [  6.72921710e-02,   7.55502436e-02],
       [  1.66387156e-01,   1.11409058e-01],
       [  2.71187348e-01,   1.24714465e-01],
       [  3.76920503e-01,   1.22141036e-01],
       [  4.82004142e-01,   1.09602483e-01],
       [  5.86248455e-01,   9.12808023e-02],
       [  6.89851996e-01,   6.97282693e-02],
       [  7.93174769e-01,   4.70976031e-02],
       [  8.96527245e-01,   2.49669917e-02],
       [  1.00000000e+00,   3.91000000e-03]])

p_data = np.array([[  1.00000000e+00,  -1.16953764e-02],
       [  8.87236469e-01,  -2.43220527e-03],
       [  7.69652278e-01,  -2.58962829e-02],
       [  6.52527314e-01,  -6.95431800e-02],
       [  5.33491596e-01,  -1.16882160e-01],
       [  4.09510980e-01,  -1.52729873e-01],
       [  2.82285727e-01,  -1.65930763e-01],
       [  1.58682293e-01,  -1.49500142e-01],
       [  5.22818120e-02,  -9.56835708e-02],
       [ -1.09395361e-05,   1.06203334e-03],
       [  4.70521397e-02,   9.68137906e-02],
       [  1.41912132e-01,   1.50030576e-01],
       [  2.49963976e-01,   1.67388750e-01],
       [  3.59490124e-01,   1.63070578e-01],
       [  4.67906997e-01,   1.46820994e-01],
       [  5.75128009e-01,   1.23910154e-01],
       [  6.81586349e-01,   9.75192652e-02],
       [  7.87647823e-01,   6.92958844e-02],
       [  8.93686777e-01,   4.06047565e-02],
       [  1.00000000e+00,   1.24853187e-02]])

c_data = np.array([[  1.00000000e+00,  -1.13962899e-02],
       [  8.87421314e-01,  -2.18259509e-03],
       [  7.69941667e-01,  -2.52208064e-02],
       [  6.52884522e-01,  -6.85657982e-02],
       [  5.34003229e-01,  -1.15844787e-01],
       [  4.10197405e-01,  -1.51671732e-01],
       [  2.83167061e-01,  -1.64999563e-01],
       [  1.59730787e-01,  -1.48751610e-01],
       [  5.32813154e-02,  -9.52509018e-02],
       [ -1.15398580e-05,   9.24981927e-04],
       [  4.83047177e-02,   9.57543977e-02],
       [  1.43563914e-01,   1.47857563e-01],
       [  2.51413382e-01,   1.64814442e-01],
       [  3.60660460e-01,   1.60548027e-01],
       [  4.68830105e-01,   1.44591988e-01],
       [  5.75839270e-01,   1.22076055e-01],
       [  6.82102557e-01,   9.60890997e-02],
       [  7.87968900e-01,   6.82035368e-02],
       [  8.93823167e-01,   3.98242792e-02],
       [  1.00000000e+00,   1.21248369e-02]])

a_data = np.array([[  1.00000000e+00,  -1.14026379e-02],
       [  8.87426906e-01,  -2.20092151e-03],
       [  7.69936384e-01,  -2.52624344e-02],
       [  6.52878831e-01,  -6.86862746e-02],
       [  5.34011185e-01,  -1.16067874e-01],
       [  4.10200742e-01,  -1.51959314e-01],
       [  2.83158326e-01,  -1.65345013e-01],
       [  1.59712662e-01,  -1.49076714e-01],
       [  5.32837425e-02,  -9.54335343e-02],
       [ -1.16876614e-05,   8.86668536e-04],
       [  4.84878050e-02,   9.56682171e-02],
       [  1.43845737e-01,   1.47600216e-01],
       [  2.51665447e-01,   1.64457074e-01],
       [  3.60858469e-01,   1.60182288e-01],
       [  4.68979814e-01,   1.44287219e-01],
       [  5.75949905e-01,   1.21859370e-01],
       [  6.82179354e-01,   9.59583413e-02],
       [  7.88009952e-01,   6.81189360e-02],
       [  8.93832667e-01,   3.97603572e-02],
       [  1.00000000e+00,   1.21156693e-02]])

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
        af.computeLETE()
        aff = af.redistribute_even(20)

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
