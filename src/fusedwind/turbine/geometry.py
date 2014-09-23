
import numpy as np
from scipy.interpolate import pchip

from openmdao.main.api import Component
from openmdao.lib.datatypes.api import Array, VarTree, Enum, Int

from fusedwind.turbine.geometry_vt import BladePlanformVT
from fusedwind.interface import base, implement_base


class SplineBase(object):
    """
    base for 1-D splines

    if the spline requires it, implement a fitting procedure in __init__

    place the main call to the spline in __call__ 
    """

    def initialize(self, Cx, xp, yp):

        pass

    def normdist(self, xp):
        """normalize x distribution"""

        return (xp - xp[0]) / (xp[-1] - xp[0])

    def __call__(self, x, Cx, C):
        """
        params:
        ----------
        x: array
            array with new x-distribution
        xp: array
            array with x-coordinates of spline control points
        yp: array
            array with y-coordinates of spline control points

        returns
        ---------
        ynew: array
            resampled points
        """

        raise NotImplementedError('A derived class of SplineBase needs to implement a __call__ method')


class pchipSpline(SplineBase):

    def initialize(self, x, xp, yp):
        """
        params:
        ----------
        x: array
            array with new x-distribution
        xp: array
            array with original x-distribution
        yp: array
            array with original y-distribution

        returns
        ---------
        ynew: array
            resampled points
        """

        return self.__call__(x, xp, yp)

    def __call__(self, x, Cx, C):
        """
        params:
        ----------
        x: array
            array with new x-distribution
        xp: array
            array with x-coordinates of spline control points
        yp: array
            array with y-coordinates of splinecontrol points

        returns
        ---------
        ynew: array
            resampled points
        """

        spl = pchip(Cx, C)
        return spl(x)


spline_dict = {'pchip': pchipSpline}


@base
class SplineComponentBase(Component):
    """
    FUSED-Wind base class for splines
    """

    spline_type = Enum('pchip', ('pchip', 'bezier', 'bspline','akima','cubic'),
                        iotype='in', desc='spline type used')

    nC = Int(iotype='in')
    Cx = Array(iotype='in', desc='Spanwise distribution of control points [0:1]')
    x = Array(iotype='in', desc='Spanwise discretization')
    xinit = Array(np.linspace(0,1,10), iotype='in', desc='Initial spanwise distribution')
    Pinit = Array(np.zeros(10), iotype='in', desc='Initial curve as function of span')

    P = Array(iotype='out', desc='Output curve')

    def set_spline(self, spline_type):

        self.spline = spline_dict[spline_type]()
        self.spline_type = spline_type

    def initialize(self):
        """

        """
        self.set_spline()
        self.C = self.spline(self.Cx, self.xinit, self.Pinit)

    def execute(self):
        """
        Default behaviour is to copy the input array

        derived classes need to overwrite this class with specific splines
        """

        self.P = self.spline(self.x, self.Cx, self.C)


@base
class ModifyBladePlanformBase(Component):
    """
    Base for classes that modify a blade planform object
    """

    pfIn = VarTree(BladePlanformVT(), iotype='in')
    pfOut = VarTree(BladePlanformVT(), iotype='out')


@implement_base(ModifyBladePlanformBase)
class RedistributedBladePlanform(Component):
    """
    Redistribute an existing planform onto a new distribution x
    """

    x = Array(iotype='in', desc='New spanwise discretization')

    pfIn = VarTree(BladePlanformVT(), iotype='in')
    pfOut = VarTree(BladePlanformVT(), iotype='out')

    def execute(self):

        self.pfOut.s = self.x.copy()
        self.pfIn._compute_s()
        for name in self.pfIn.list_vars():
            var = getattr(self.pfIn, name)
            if not isinstance(var, np.ndarray): continue
            tck = pchip(self.pfIn.s, var)
            newvar = tck(self.x) 
            setattr(self.pfOut, name, newvar)
