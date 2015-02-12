
import numpy as np
import unittest

from fusedwind.lib.bezier import BezierCurve


points = np.array([[ 0.        ,  0.        ],
                   [ 0.02722146, -0.10096022],
                   [ 0.09974089, -0.17283951],
                   [ 0.20493827, -0.20740741],
                   [ 0.33165676, -0.20301783],
                   [ 0.47020271, -0.16460905],
                   [ 0.61234568, -0.1037037 ],
                   [ 0.7513184 , -0.03840878],
                   [ 0.8818168 ,  0.00658436],
                   [ 1.        ,  0.        ]])

def make_bezier():

    b = BezierCurve()
    b.ni = 10

    b.CPs = np.array([[0, 0., 0.4, 0.75, 1.],[0., -.25, -.4, .1, 0.]]).T
    b.update()
    return b


class TestBezier(unittest.TestCase):

    def test_bezier(self):

        b = make_bezier()

        self.assertEqual(np.testing.assert_array_almost_equal(b.points, points, decimal=6), None)

if __name__ == '__main__':

    unittest.main()
