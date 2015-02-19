
import numpy as np
from scipy.optimize import minimize
from scipy.interpolate import pchip, Akima1DInterpolator

from openmdao.main.api import VariableTree
from openmdao.lib.datatypes.api import Float, Array, VarTree, Int

from fusedwind.interface import base, implement_base
from fusedwind.lib.geom_tools import calculate_length, curvature
from fusedwind.lib.cubicspline import NaturalCubicSpline
from fusedwind.lib.distfunc import distfunc


@base
class Curve(VariableTree):

    length = Float(desc='Total curve length')
    s = Array(desc='Curve accumulated curve length')
    points = Array(desc='coordinates of curve')
    ni = Int(desc='Number of points')


    def __init__(self, points=None):
        super(Curve, self).__init__()

        if points is not None:
            self.initialize(points)

    def initialize(self, points):

            self.points = points
            self.ni = points.shape[0]

            self._compute_s()
            self._compute_dp()
            self._build_splines()

    def _compute_s(self):
        """
        compute normalized curve length
        """
        s = calculate_length(self.points)
        self.length = s[-1]
        self.ds = np.diff(s)
        self.s = s/s[-1]


    def _compute_dp(self):
        """compute the unit direction vectors along the curve"""
 
        t1 = np.gradient(self.points[:,:])[0]
        self.dp = np.array([t1[i, :] / np.linalg.norm(t1[i, :]) for i in range(t1.shape[0])])

    def _build_splines(self):

        self._splines = []

        for j in range(self.points.shape[1]):
            self._splines.append(NaturalCubicSpline(self.s, self.points[:, j]))

    def redistribute(self, dist=None, s=None):

        if dist is not None:
            self.s = distfunc(dist)
        else:
            self.s = s

        self.ni = self.s.shape[0]
        points = np.zeros((self.ni, self.points.shape[1]))
        for i in range(points.shape[1]):
            points[:, i] = self._splines[i](self.s)

        self.initialize(points)

@base
class AirfoilShape(Curve):
    """
    Base class for airfoil shapes.

    The class automatically computes the LE and TE
    and can redistribute the points smoothly along the surface.
    Points along the surface need to be defined starting at the
    TE pressure side ending at the TE suction side.
    """

    LE = Array(desc='Leading edge coordinates')
    TE = Array(desc='Trailing edge coordinates')
    sLE = Float(desc='Leading edge curve fraction')
    chord = Float(desc='chord length')

    def initialize(self, points):

        super(AirfoilShape, self).initialize(points)
        self.computeLETE()

    def computeLETE(self):
        """
        computes the leading and trailing edge of the airfoil.

        TE is computed as the mid-point between lower and upper TE points
        LE is computed as the point with maximum distance from the TE.
        """

        self.TE = np.array([np.average(self.points[[0, -1], 0]),
                            np.average(self.points[[0, -1], 1])])

        res = minimize(self._sdist, (0.5), method='SLSQP', bounds=[(0, 1)])
        self.sLE = res['x'][0]
        xLE = self._splines[0](self.sLE)
        yLE = self._splines[1](self.sLE)
        self.LE = np.array([xLE, yLE])
        self.curvLE = NaturalCubicSpline(self.s, curvature(self.points))(self.sLE)
        self.chord = np.linalg.norm(self.LE-self.TE)

    def _sdist(self, s):

        x = self._splines[0](s)
        y = self._splines[1](s)
        return -((x - self.TE[0])**2 + (y - self.TE[1])**2)**0.5

    def leading_edge_dist(self, ni):
        """ function that returns a suitable cell size based on airfoil LE curvature """

        min_ds1 = 1. / ni * 0.1
        max_ds1 = 1. / ni * 0.5

        ds1 = max((min_ds1 - max_ds1) / 30. * abs(self.curvLE) + max_ds1, min_ds1)

        return ds1

    def redistribute(self, ni, even=False, dist=None, dLE=False, dTE=-1.):
        """
        redistribute the points on the airfoil using fusedwind.lib.distfunc

        Parameters
        ----------
        ni : int
            total number of points on airfoil
        even : bool
            flag for getting an even distribution of points
        dist : list
            optional list of control points with the form
            [[s0, ds0, n0], [s1, ds1, n1], ... [s<n>, ds<n>, n<n>]]
            where\n
            s<n> is the normalized curve fraction at each control point,\n 
            ds<n> is the normalized cell size at each control point,\n
            n<n> is the cell count at each control point.
        dLE : bool
            optional flag for automatically calculating a suitable leading edge cell
            size based on the local curvature
        dTE : float
            optional trailing edge cell size. If set to -1 the cell size will increase
            from the LE to TE according to the tanh distribution function used
            in distfunc
        """

        if even:
            dist = [[0, 1./np.float(ni-1), 1], [self.sLE, 1./np.float(ni-1), int(ni*self.sLE)], [1, 1./np.float(ni-1), ni]]
        elif dLE:
            dist = [[0., dTE, 1], [self.sLE, self.leading_edge_dist(ni), ni / 2], [1., dTE, ni]]

        super(AirfoilShape, self).redistribute(dist)

        return self

    def s_to_11(self, s):
        """  
        Transform the s coordinates from AirfoilShape format:

        * s=0 at TE pressure side (lower surface)
        * s=1 at TE suction side (upper surface)

        to the s coordinates from the input definition:

        * s=0 at LE
        * s=1 at TE suction side (upper surface)
        * s=-1 at TE pressure side (lower surface)
        """

        if s > self.sLE:
            return (s-self.sLE) / (1.0-self.sLE)
        else:
            return -1.0 + s/self.sLE

    def s_to_01(self, s):
        """  
        Transform the s coordinates from the input definition:

        * s=0 at LE
        * s=1 at TE suction side (upper surface)
        * s=-1 at TE pressure side (lower surface)

        to the backend defintion compatible with AirfoilShape():

        * s=0 at TE pressure side (lower surface)
        * s=1 at TE suction side (upper surface)
        """
        if s >= 0.0: 
            return s*(1.0-self.sLE) + self.sLE
        else:
            return (1.0+s)*self.sLE

    def interp_s(self, s):
        """
        interpolate (x,y) at some curve fraction s
        """

        p = np.zeros(2)
        for i in range(2):
            p[i] = self._splines[i](s)

        return p


class BlendAirfoilShapes(object):
    """
    Blend input airfoil shape family based on a user defined scalar.

    The blended airfoil shape is interpolated using a cubic interpolator
    of the airfoil shapes.
    Three interpolators are implemented:\n
    ``scipy.interpolate.pchip``: has some unappealing characteristics at the bounds\n
    ``fusedwind.lib.cubicspline``: can overshoot significantly with large spacing in
    thickness\n
    ``scipy.interpolate.Akima1DInterpolator``: good compromise, overshoots less
    than a natural cubic spline\n

    The default spline is scipy.interpolate.Akima1DInterpolator.

    Parameters
    ----------
    ni: int
        number of redistributed points on airfoils

    airfoil_list: list
        List of normalized airfoils with size ((ni, 2)).

    blend_var: list
        weight factors for each airfoil in the list, only relevant if tc is not specified.

    spline: str
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
            aa = a.redistribute(ni=self.ni, even=True)
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
        ----------
        tc : float
            The relative thickness of the wanted airfoil.

        Returns
        -------
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



@base
class BeamGeometryVT(VariableTree):

    smax = Float(desc='Total accumulated length of beam')
    s = Array(desc='Curve fraction')
    x = Array(desc='x-coordinates of beam')
    y = Array(desc='y-coordinates of beam')
    z = Array(desc='z-coordinates of beam')
    rot_x = Array(desc='x-rotation of beam')
    rot_y = Array(desc='y-rotation of beam')
    rot_z = Array(desc='z-rotation of beam')

    def _compute_s(self):
        """
        compute normalized curve length
        """
        s = calculate_length(self._to_array())
        self.smax = s[-1]
        self.s = s/s[-1]

    def _to_array(self):

        return np.array([self.x, self.y, self.z]).T


@base
class BladePlanformVT(BeamGeometryVT):

    blade_length = Float(units='m', desc='Blade radial length')
    chord = Array(units=None, desc='Chord length at each section')
    rthick = Array(units=None, desc='Relative thickness at each section, t/c')
    athick = Array(units=None, desc='Relative thickness at each section, t/c')
    p_le = Array(units=None, desc='Normalized distance from LE to pitch axis')


@base
class TubularTowerGeometryVT(BeamGeometryVT):

    radius = Array(desc='Tower radius as function of s')


@base
class BladeSurfaceVT(VariableTree):
    """
    3D surface of a blade
    """

    surface = Array(desc='Surface of a blade described by a series of stacked cross sections'
                          'dimensions: (ni_chord, ni_span, 3)')

    def __init__(self):
        super(BladeSurfaceVT, self).__init__()

        self._prep_called = False

    def _compute_axis(self):
        """
        The blade axis is computed along the 3rd dimension of the blade
        """

        axis = np.zeros((self.surface.shape[1], 3))
        for j in range(self.surface.shape[1]):
            for nd in range(3):
                axis[j, nd] = np.mean(self.surface[:, j, nd])
        self.axis = Curve(axis)

        self._prep_called = True

    def interpolate_profile(self, ix):
        """
        interpolate the profile at position ix on the blade,
        relative to the running length of the blade
        """

        if not self._prep_called:
            self._compute_axis()

        ni = self.surface.shape[0]
        # linear interpolation of points
        prof = np.zeros((ni, 3))
        for i in range(self.surface.shape[0]):
            for iX in range(3):
                prof[i,iX]  = np.interp(ix, self.axis.s, self.surface[i,:,iX])

        return prof
