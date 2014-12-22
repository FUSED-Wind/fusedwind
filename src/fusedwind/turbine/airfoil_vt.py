
import copy
import numpy as np
from scipy.interpolate import pchip, Akima1DInterpolator
from scipy.optimize import minimize

from openmdao.main.api import VariableTree
from openmdao.main.datatypes.api import Str, Float, Array, List

from fusedwind.lib.cubicspline import NaturalCubicSpline
from fusedwind.turbine.geometry_vt import Curve


class AirfoilDataVT(VariableTree):
    """
    airfoil data at a specific Reynolds number over of range of angles of attack
    """

    desc = Str(desc='Description of data, i.e. airfoil name, flow conditions (clean/rough) etc')
    Re = Float(desc='Reynolds number')
    alpha = Array(units='deg', desc='angles of attack')
    cl = Array(desc='corresponding lift coefficients')
    cd = Array(desc='corresponding drag coefficients')
    cm = Array(desc='corresponding pitching moment coefficients')


class AirfoilDatasetVT(VariableTree):
    """
    List of AirfoilDataVT datasets

    The ``interpolator`` parameter can be used to characterize the list of data
    in terms of e.g. Reynolds number, relative thickness, TE flap angle, roughness ratio etc,
    and should have the same length as the number of polars.
    """

    desc = Str(desc='Description of dataset')
    interpolator = Array(desc='The interpolator could characterize e.g. TE flap angle, roughness ratio etc')
    polars = List(AirfoilDataVT, desc='List of AirfoilDataVT')


class AirfoilShape(Curve):

    def __init__(self, points):
        super(AirfoilShape, self).__init__(points)

        self.spline = []
        self.spline.append(NaturalCubicSpline(self.s, points[:, 0]))
        self.spline.append(NaturalCubicSpline(self.s, points[:, 1]))

    def computeLETE(self):

        res = minimize(self.spline[0], (0.5), method='SLSQP')
        self.sLE = res['x'][0]
        xLE = res['fun']
        yLE = self.spline[1](self.sLE)
        self.LE = np.array([xLE, yLE])
        self.TE = np.array([np.average(self.points[[0, -1], 0]),
                            np.average(self.points[[0, -1], 1])])

    def redistribute_even(self, ni=400):

        from fusedwind.lib.distfunc import distfunc

        dist = [[0, 1./np.float(ni), 1], [self.sLE, 1./np.float(ni), ni/2], [1, 1./np.float(ni), ni]]
        s = distfunc(dist)

        points = np.zeros((ni, 2))
        for i in range(2):
            points[:, i] = self.spline[i](s)
        return AirfoilShape(points)


class BlendAirfoilShapes(object):
    """
    Blend input airfoil shape family based on a user defined scalar.

    The blended airfoil shape is interpolated using a cubic interpolator
    of the airfoil shapes.
    Three interpolators are implemented:
        - scipy.interpolate.pchip: has some unappealing characteristics at the bounds
        - fusedwind.lib.cubicspline: can overshoot significantly with large spacing in
          thickness
        - scipy.interpolate.Akima1DInterpolator: good compromise, overshoots less
          than a natural cubic spline

    The default spline is scipy.interpolate.Akima1DInterpolator.

    Parameters
    ------------
    ni: integer
        number of redistributed points on airfoils

    airfoil_list: list
        List of normalized airfoils with size ((ni, 2)).

    blend_var: list
        weight factors for each airfoil in the list, only relevant if tc is not specified.

    spline: string
        spline type, either ('pchip', 'cubic', 'akima')

    allow_extrapolation: bool
        the splines allow for limited extrapolation, set to True if you feel lucky
    """


    def __init__(self, **kwargs):

        self.airfoil_list = []
        self.ni = 600
        self.blend_var = None
        self.spline = 'pchip'
        self.allow_extrapolation = False

        for k,v in kwargs.iteritems():
            if hasattr(self,k):
                setattr(self,k,v)

    def initialize(self):

        if self.spline == 'pchip':
            self._spline = pchip
        elif self.spline == 'cubic':
            self._spline = NaturalCubicSpline
        elif self.spline == 'akima':
            self._spline = Akima1DInterpolator

        self.blend_var = np.asarray(self.blend_var)

        afs = []
        for af in self.airfoil_list:
            a = AirfoilShape(af)
            a.computeLETE()
            aa = a.redistribute_even(ni=self.ni)
            afs.append(aa.points)
        self.airfoil_list = afs

        self.nj = len(self.airfoil_list)
        self.nk = 3

        self.x = np.zeros([self.ni,self.nj,self.nk])
        for j, points in enumerate(self.airfoil_list):
            self.x[:,j,:2] = points[: , :2]
            self.x[:,j,2] = self.blend_var[j]

        self.f = [[],[]]
        for k in range(2):
            for i in range(self.ni):
                self.f[k].append(self._spline(self.x[0, :, 2], self.x[i, :, k]))


    def __call__(self, tc):
        """
        interpolate airfoil family at a given thickness

        Parameters
        ------------
        tc : float
            The relative thickness of the wanted airfoil.

        Returns
        ---------
        airfoil: array
            interpolated airfoil shape of size ((ni, 2))
        """

        # check for out of bounds
        if not self.allow_extrapolation:
            if tc < np.min(self.blend_var): tc = self.blend_var.min()
            if tc > np.max(self.blend_var): tc = self.blend_var.max()

        points = np.zeros((self.ni, 2))
        for k in range(2):
            for i in range(self.ni):
                points[i, k] = self.f[k][i](tc)

        return points
