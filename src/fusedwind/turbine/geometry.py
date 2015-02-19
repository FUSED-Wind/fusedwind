
import numpy as np
from scipy.interpolate import pchip, Akima1DInterpolator
from scipy.linalg import norm
from openmdao.main.api import Component, Assembly
from openmdao.lib.datatypes.api import Instance, Array, VarTree, Enum, Int, List, Str, Float, Bool

from fusedwind.lib.distfunc import distfunc
from fusedwind.lib.cubicspline import NaturalCubicSpline
from fusedwind.lib.geom_tools import RotMat, dotXC, calculate_length, curvature
from fusedwind.lib.bezier import BezierCurve
from fusedwind.turbine.geometry_vt import Curve, BladePlanformVT, BladeSurfaceVT, BlendAirfoilShapes
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
            array with y-coordinates of spline control points

        returns
        ---------
        ynew: array
            resampled points
        """

        spl = pchip(Cx, C)
        return spl(x)


class BezierSpline(SplineBase):

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
        self.B = BezierCurve()
        self.B.CPs = np.array([xp, yp]).T
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
            array with y-coordinates of spline control points

        returns
        ---------
        ynew: array
            resampled points
        """
        self.B.CPs = np.array([Cx, C]).T
        self.B.update()
        spl = NaturalCubicSpline(self.B.points[:, 0], self.B.points[:, 1])
        return spl(x)


spline_dict = {'pchip': pchipSpline,
               'bezier': BezierSpline}


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


    def __init__(self, nC=8):
        super(SplineComponentBase, self).__init__()

        self.init_called = False
        self.nC = nC
        # the spline engine derived from SplineBase (set by parent class)
        self.spline = None

        self.add('C', Array(np.zeros(nC), size=(nC,),
                                          dtype=float,
                                          iotype='in', 
                                          desc='spline control points of cross-sectional curve fraction'
                                               'ending point of region'))

        self.set_spline(self.spline_type)

    def set_spline(self, spline_type):

        self.spline = spline_dict[spline_type]()
        self.spline_type = spline_type

    def initialize(self):
        """

        """
        self.set_spline(self.spline_type)
        self.C = self.spline(self.Cx, self.xinit, self.Pinit)

    def execute(self):
        """
        Default behaviour is to copy the input array

        derived classes need to overwrite this class with specific splines
        """

        if not self.init_called:
            self.initialize()

        self.P = self.spline(self.x, self.Cx, self.C)


@base
class FFDSplineComponentBase(Component):
    """
    FUSED-Wind base class for splines
    """

    spline_type = Enum('pchip', ('pchip', 'bezier', 'bspline','akima','cubic'),
                        iotype='in', desc='spline type used')
    base_spline_type = Enum('pchip', ('pchip', 'bezier', 'bspline','akima','cubic'),
                        iotype='in', desc='spline type used')
    nC = Int(iotype='in')
    Cx = Array(iotype='in', desc='Spanwise distribution of control points [0:1]')
    x = Array(iotype='in', desc='Spanwise discretization')
    xinit = Array(np.linspace(0,1,10), iotype='in', desc='Initial spanwise distribution')
    Pinit = Array(np.zeros(10), iotype='in', desc='Initial curve as function of span')

    P = Array(iotype='out', desc='Output curve')
    dPds = Array(iotype='out', desc='Curvature')

    def __init__(self, nC=8):
        super(FFDSplineComponentBase, self).__init__()

        self.init_called = False
        self.nC = nC
        # the spline engine derived from SplineBase (set by parent class)
        self.spline = None

        self.add('C', Array(np.zeros(nC), size=(nC,),
                                          dtype=float,
                                          iotype='in', 
                                          desc='spline control points of cross-sectional curve fraction'
                                               'ending point of region'))

        self.set_spline(self.spline_type)

    def set_spline(self, spline_type):

        self.spline = spline_dict[spline_type]()
        self.spline_type = spline_type

    def initialize(self):
        """

        """

        self.base_spline = spline_dict[self.base_spline_type]()
        self.set_spline(self.spline_type)
        self.Pbase = self.base_spline(self.x, self.xinit, self.Pinit)
        self.spline.initialize(self.x, self.Cx, self.C)

    def execute(self):
        """
        Default behaviour is to copy the input array

        derived classes need to overwrite this class with specific splines
        """

        if not self.init_called:
            self.initialize()

        self.P = self.Pbase + self.spline(self.x, self.Cx, self.C)
        self.dPds = curvature(np.array([self.x, self.P]).T)


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

        self.pfOut.blade_length = self.pfIn.blade_length
        self.pfIn._compute_s()
        for name in self.pfIn.list_vars():
            var = getattr(self.pfIn, name)
            if not isinstance(var, np.ndarray): continue
            tck = pchip(self.pfIn.s, var)
            newvar = tck(self.x) 
            setattr(self.pfOut, name, newvar)
        self.pfOut._compute_s()

def redistribute_blade_planform(pfIn, x):

    pfOut = BladePlanformVT()
    pfOut.s = x.copy()

    for name in pfIn.list_vars():
        var = getattr(pfIn, name)
        if not isinstance(var, np.ndarray): continue
        tck = Akima1DInterpolator(pfIn.s, var)
        newvar = tck(x) 
        setattr(pfOut, name, newvar)

    return pfOut


def read_blade_planform(filename):

    data = np.loadtxt(filename)
    s = calculate_length(data[:, [0, 1, 2]])

    pf = BladePlanformVT()
    pf.blade_length = data[-1, 2]
    pf.s = s / s[-1]
    pf.smax = s[-1]
    pf.x = data[:, 0] / data[-1, 2]
    pf.y = data[:, 1] / data[-1, 2]
    pf.z = data[:, 2] / data[-1, 2]
    pf.rot_x = data[:, 3]
    pf.rot_y = data[:, 4]
    pf.rot_z = data[:, 5]
    pf.chord = data[:, 6] / data[-1, 2]
    pf.rthick = data[:, 7]
    pf.rthick /= pf.rthick.max()
    pf.athick = pf.rthick * pf.chord
    pf.p_le = data[:, 8]

    return pf


@base
class BladePlanformWriter(Component):

    filebase = Str('blade')
    pf = VarTree(BladePlanformVT(), iotype='in')

    def execute(self):

        name = self.filebase + self.itername + '.pfd'

        try:
            if '-fd' in self.itername or '-fd' in self.parent.itername:
               name = self.filebase + '.pfd'
        except:
            pass

        data = np.array([self.pf.x,
                         self.pf.y,
                         self.pf.z,
                         self.pf.rot_x,
                         self.pf.rot_y,
                         self.pf.rot_z,
                         self.pf.chord,
                         self.pf.rthick,
                         self.pf.p_le]).T
        fid = open(name, 'w')
        header = ['main_axis_x',  'main_axis_y', 'main_axis_z', 'rot_x', 'rot_y', 'rot_z', 'chord', 'rthick', 'p_le']

        exp_prec = 10             # exponential precesion
        col_width = exp_prec + 8  # column width required for exp precision
        header_full = '# ' + ''.join([(hh + ' [%i]').center(col_width + 2)%i for i, hh in enumerate(header)])+'\n'

        fid.write(header_full)
        np.savetxt(fid, data, fmt='%'+' %i.%ie' % (col_width, exp_prec))
        fid.close()

class ComputeDist(Component):
    """
    simple redistribution function that clusters cells towards one end
    """

    span_ni = Int(iotype='in')
    x = Array(iotype='out')

    def execute(self):

        self.x = distfunc([[0., -1, 1], [1., 0.2 * 1./self.span_ni, self.span_ni]])


class ScaleChord(Component):
    """
    component to replace
    connect(sname + '.P'+
        '*blade_length/blade_length_ref', 'pfOut.' + vname)
    """

    scaler = Float(iotype='in')
    cIn = Array(iotype='in')
    cOut = Array(iotype='out')

    def execute(self):

        self.cOut = self.scaler * self.cIn


class ComputeAthick(Component):
    """
    component to replace connection:
    connect('chord.P*rthick.P', 'pfOut.athick')
    """
    
    chord = Array(iotype='in')
    rthick = Array(iotype='in')
    athick = Array(iotype='out')

    def execute(self):

        self.athick = self.chord * self.rthick


class ComputeSmax(Component):

    x = Array(iotype='in')
    y = Array(iotype='in')
    z = Array(iotype='in')
    smax = Float(iotype='in')

    def execute(self):

        s = calculate_length(np.array([self.x,
                                       self.y,
                                       self.z]).T)
        self.smax = s[-1]


@implement_base(ModifyBladePlanformBase)
class SplinedBladePlanform(Assembly):

    x_dist = Array(iotype='in', desc='spanwise resolution of blade')
    nC = Int(8, iotype='in', desc='Number of spline control points along span')
    Cx = Array(iotype='in', desc='spanwise distribution of spline control points')

    blade_length = Float(1., iotype='in')
    blade_length_ref = Float(iotype='in')

    span_ni = Int(50, iotype='in')

    pfIn = VarTree(BladePlanformVT(), iotype='in')
    pfOut = VarTree(BladePlanformVT(), iotype='out')

    def __init__(self):
        super(SplinedBladePlanform, self).__init__()
        
        self.blade_length_ref = 0.

    def _pre_execute(self):
        super(SplinedBladePlanform, self)._pre_execute()

        # set reference length first time this comp is executed
        if self.blade_length_ref == 0.:
            self.blade_length_ref = self.blade_length

    def configure_splines(self, spline_type='pchip'):


        if hasattr(self, 'chord_C'):
            return
        if self.Cx.shape[0] == 0:
            self.Cx = np.linspace(0, 1, self.nC)
        else:
            self.nC = self.Cx.shape[0]


        self.connect('blade_length', 'pfOut.blade_length')

        self.add('compute_x', ComputeDist())
        self.driver.workflow.add('compute_x')
        self.connect('span_ni', 'compute_x.span_ni')

        for vname in self.pfIn.list_vars():
            if vname in ['athick', 'blade_length']:
                continue

            cIn = self.get('pfIn.' + vname)
            cOut = self.get('pfOut.' + vname)
            sname = vname.replace('.','_')

            if vname == 's':
                self.connect('compute_x.x', 'pfOut.s')
            else:
                spl = self.add(sname, FFDSplineComponentBase(self.nC))
                self.driver.workflow.add(sname)
                # spl.log_level = logging.DEBUG
                spl.set_spline(spline_type)
                self.connect('compute_x.x', sname + '.x')
                self.connect('Cx', sname + '.Cx')
                spl.xinit = self.get('pfIn.s')
                spl.Pinit = cIn
                if vname == 'chord':
                    self.add('scaleC', ScaleChord())
                    self.driver.workflow.add('scaleC')
                    self.connect('chord.P', 'scaleC.cIn')
                    self.connect('blade_length/blade_length_ref', 'scaleC.scaler')
                    self.connect('scaleC.cOut', 'pfOut.chord')
                    # self.connect(sname + '.P'+
                    #     '*blade_length/blade_length_ref', 'pfOut.' + vname)
                else:
                    self.connect(sname + '.P', 'pfOut.' + vname)
                self.create_passthrough(sname + '.C', alias=sname + '_C')
                self.create_passthrough(sname + '.dPds', alias=sname + '_dPds')

        self.add('athick', ComputeAthick())
        self.driver.workflow.add('athick')
        self.connect('chord.P', 'athick.chord')
        self.connect('rthick.P', 'athick.rthick')
        self.connect('athick.athick', 'pfOut.athick')
        self.add('smax', ComputeSmax())
        self.driver.workflow.add('smax')
        self.connect('x.P', 'smax.x')
        self.connect('y.P', 'smax.y')
        self.connect('z.P', 'smax.z')
        self.connect('smax.smax', 'pfOut.smax')

@base
class LoftedBladeSurfaceBase(Component):

    surfout = VarTree(BladeSurfaceVT(), iotype='out')
    surfnorot = VarTree(BladeSurfaceVT(), iotype='out')


@implement_base(LoftedBladeSurfaceBase)
class LoftedBladeSurface(Component):

    pf = VarTree(BladePlanformVT(), iotype='in')
    base_airfoils = List(iotype='in')
    blend_var = Array(iotype='in')
    chord_ni = Int(300, iotype='in')
    span_ni = Int(300, iotype='in')

    interp_type = Enum('rthick', ('rthick', 's'), iotype='in')
    surface_spline = Str('akima', iotype='in', desc='Spline')

    rot_order = Array(np.array([2,1,0]),iotype='in',desc='rotation order of airfoil sections'
                                                         'default z,y,x (twist,sweep,dihedral)')

    surfout = VarTree(BladeSurfaceVT(), iotype='out')
    surfnorot = VarTree(BladeSurfaceVT(), iotype='out')

    def execute(self):

        self.interpolator = BlendAirfoilShapes()
        self.interpolator.ni = self.chord_ni
        self.interpolator.spline = self.surface_spline
        self.interpolator.blend_var = self.blend_var
        self.interpolator.airfoil_list = self.base_airfoils
        self.interpolator.initialize()

        self.span_ni = self.pf.s.shape[0]
        x = np.zeros((self.chord_ni, self.span_ni, 3))

        for i in range(self.span_ni):

            s = self.pf.s[i]
            pos_x = self.pf.x[i]
            pos_y = self.pf.y[i]
            pos_z = self.pf.z[i]
            chord = self.pf.chord[i]
            p_le = self.pf.p_le[i]

            # generate the blended airfoil shape
            if self.interp_type == 'rthick':
                rthick = self.pf.rthick[i]
                points = self.interpolator(rthick)
            else:
                points = self.interpolator(s)

            points *= chord
            points[:, 0] -= chord * p_le

            # x-coordinate needs to be inverted for clockwise rotating blades
            x[:, i, :] = (np.array([-points[:,0], points[:,1], x.shape[0] * [pos_z]]).T)

        # save blade without sweep and prebend
        x_norm = x.copy()

        # add translation and rotation
        x[:, :, 0] += self.pf.x
        x[:, :, 1] += self.pf.y
        x = self.rotate(x)

        self.surfnorot.surface = x_norm
        self.surfout.surface = x

    def rotate(self, x):
        """
        rotate blade sections accounting for twist and main axis orientation
        
        the blade will be built with a "sheared" layout, ie no rotation around y
        in the case of sweep.
        if the main axis includes a winglet, the blade sections will be
        rotated accordingly. ensure that an adequate point distribution is
        used in this case to avoid sections colliding in the winglet junction!
        """

        main_axis = Curve(points=np.array([self.pf.x, self.pf.y, self.pf.z]).T)

        rot_normals = np.zeros((3,3))
        x_rot = np.zeros(x.shape)

        for i in range(x.shape[1]):
            points = x[:, i, :]
            rot_center = main_axis.points[i]
            # rotation angles read from file
            angles = np.array([self.pf.rot_x[i],
                               self.pf.rot_y[i], 
                               self.pf.rot_z[i]]) * np.pi / 180.

            # compute rotation angles of main_axis
            t = main_axis.dp[i]
            rot = np.zeros(3)
            rot[0] = -np.arctan(t[1]/(t[2]+1.e-20))
            v = np.array([t[2], t[1]])
            vt = np.dot(v, v)**0.5
            rot[1] = (np.arcsin(t[0]/vt))
            angles[0] += rot[0]
            angles[1] += rot[1]

            # compute x-y-z normal vectors of rotation
            n_y = np.cross(t, [1,0,0])
            n_y = n_y/norm(n_y)
            rot_normals[0, :] = np.array([1,0,0])
            rot_normals[1, :] = n_y
            rot_normals[2, :] = t

            # compute final rotation matrix
            rotation_matrix = np.matrix([[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]])
            for n, ii in enumerate(self.rot_order):
                mat = np.matrix(RotMat(rot_normals[ii], angles[ii]))
                rotation_matrix = mat * rotation_matrix

            # apply rotation
            x_rot[:, i, :] = dotXC(rotation_matrix, points, rot_center)

        return x_rot
