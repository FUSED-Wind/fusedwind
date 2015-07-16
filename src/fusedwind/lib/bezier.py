
import numpy as np
from math import factorial

from openmdao.lib.datatypes.api import List, Bool, Array, Instance, Int, Float

from fusedwind.turbine.geometry_vt import Curve
from fusedwind.lib.distfunc import distfunc
from fusedwind.lib.geom_tools import calculate_length
from fusedwind.lib.cubicspline import NaturalCubicSpline


def _C(n, k):
    return factorial(n) / (factorial(k) * factorial(n - k))


class BezierCurve(Curve):
    """
    Computes a 2D/3D bezier curve
    """

    CPs = Array(desc='Array of control points')

    def add_control_point(self, p):

        C = list(self.CPs)
        C.append(list(p))
        self.CPs = np.asarray(C)

    def update(self):

        try:
            self.nd = self.CPs.shape[1]
        except:
            raise RuntimeError('CPs needs to an array of shape (m, n)')

        if self.ni == 0:
            self.ni = 100

        points = self._compute(self.CPs)
        # self._s = calculate_length(points)
        # self._s /= self._s[-1] 
        self.initialize(points)

    # def _compute_dp(self):
    #     """
    #     computes the derivatives (tangent vectors) along a Bezier curve
    #     wrt ``t``.

    #     there is no trivial analytic function to compute derivatives wrt
    #     to a given space interval, so we just spline and redistribute
    #     see: http://pomax.github.io/bezierinfo/
    #     """
    #     C = np.zeros((self.CPs.shape[0] - 1, self.nd))
    #     nC = C.shape[0]
    #     for i in range(nC):
    #         C[i, :] = float(nC) * (self.CPs[i + 1] - self.CPs[i])

    #     dp = self._compute(C)

    def _compute(self, C):

        points = np.zeros((self.ni, self.nd))
        self.t = np.linspace(0., 1., self.ni)
        # control point iterator
        _n = xrange(C.shape[0])

        for i in range(self.ni):
            s = self.t[i]
            n = _n[-1]
            points[i, :] = 0.
            for j in range(self.nd):
                for m in _n:
                    # compute bernstein polynomial
                    b_i = _C(n, m) * s**m * (1 - s)**(n - m)
                    # multiply ith control point by ith bernstein polynomial
                    points[i, j] += C[m, j] * b_i

        return points
