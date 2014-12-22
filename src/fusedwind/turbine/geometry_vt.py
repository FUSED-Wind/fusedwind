
import numpy as np

from openmdao.main.api import VariableTree
from openmdao.lib.datatypes.api import Float, Array, VarTree

from fusedwind.lib.geom_tools import calculate_length

class Curve(VariableTree):

    length = Float(desc='blade_length')
    s = Array(desc='Main axis accumulated curve length')
    points = Array(desc='coordinates of curve')

    def __init__(self, points):
        super(Curve, self).__init__()

        self.points = points

        self._compute_s()
        self._compute_dp()

    def _compute_s(self):
        """
        compute normalized curve length
        """
        s = calculate_length(self.points)
        self.length = s[-1]
        self.s = s/s[-1]

    def _compute_dp(self):
        """compute the unit direction vectors along the curve"""
 
        t1 = np.gradient(self.points[:,:])[0]
        self.dp = np.array([t1[i, :] / np.linalg.norm(t1[i, :]) for i in range(t1.shape[0])])


class BeamGeometryVT(VariableTree):

    s = Array(desc='x-coordinates of beam')
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


class BladePlanformVT(BeamGeometryVT):

    chord = Array(units=None, desc='Chord length at each section')
    rthick = Array(units=None, desc='Relative thickness at each section, t/c')
    p_le = Array(units=None, desc='Normalized distance from LE to pitch axis')


class TubularTowerGeometryVT(BeamGeometryVT):

    radius = Array(desc='Tower radius as function of s')


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
