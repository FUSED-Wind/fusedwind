
from openmdao.main.api import VariableTree
from openmdao.lib.datatypes.api import Int, Float, Array, List, Str, Enum, Bool, VarTree, Slot


class BeamGeometryVT(VariableTree):

    critical_dim = Float(units='m', desc='blade_length')
    s = Array(desc='Main axis accumulated curve length')
    main_axis = Array(desc='Main axis of beam')
    rot_x = Array(desc='x-rotation of stations')
    rot_y = Array(desc='y-rotation of stations')
    rot_z = Array(desc='z-rotation of stations')

    def _compute_s(self):
        """
        compute s based on main_axis coordinates
        """
        pass


class BladeGeometryVT(BeamGeometryVT):

    chord = Array(units=None, desc='Chord length at each section')
    rthick = Array(units=None, desc='Relative thickness at each section, t/c')
    p_le = Array(units=None, desc='Normalized distance from LE to pitch axis')


class TowerVT(BeamGeometryVT):

    radius = Array(desc='Tower radius as function of s')


# too aeroelastic code specific?!
class ConcentratedMass(VariableTree):

    s = Float(desc='Non-dimens the inertia is attached')
    offset = Array(desc='x, y, z offset relative to node')
    moment_of_inertia = Array(desc='Ixx, Iyy, Izz moments of inertia')
    mass = Float(desc='Concentrated mass', units='kg')


class MassProperties(VariableTree):
    """mass and mass moments of inertia of a component"""

    mass = Float(units='kg', desc='mass of object')
    Ixx = Float(units='kg*m**2', desc='mass moment of inertia about x-axis') # todo: arrary or not?
    Iyy = Float(units='kg*m**2', desc='mass moment of inertia about y-axis')
    Izz = Float(units='kg*m**2', desc='mass moment of inertia about z-axis')
    Ixy = Float(units='kg*m**2', desc='mass x-y product of inertia')
    Ixz = Float(units='kg*m**2', desc='mass x-z product of inertia')
    Iyz = Float(units='kg*m**2', desc='mass y-z product of inertia')


class BeamStructureVT(VariableTree):

    s = Array(desc='Running curve length of beam', units='m')
    dm = Array(desc='Mass per unit length', units='kg/m')
    x_cg = Array(desc='x-distance from blade axis to center of mass', units='m')
    y_cg = Array(desc='y-distance from blade axis to center of mass', units='m')
    ri_x = Array(desc='radius of gyration relative to elastic center.', units='m')
    ri_y = Array(desc='radius of gyration relative to elastic center', units='m')
    x_sh = Array(desc='x-distance from blade axis to shear center', units='m')
    y_sh = Array(desc='y-distance from blade axis to shear center', units='m')
    E = Array(desc='modulus of elasticity', units='N/m**2')
    G = Array(desc='shear modulus of elasticity', units='N/m**2')
    I_x = Array(desc='area moment of inertia with respect to principal bending xe axis', units='m**4')
    I_y = Array(desc='area moment of inertia with respect to principal bending ye axis', units='m**4')
    J = Array(desc='torsional stiffness constant with respect to ze axis at the shear center', units='m**4/rad')
    k_x = Array(desc='shear factor for force in principal bending xe direction', units=None)
    k_y = Array(desc='shear factor for force in principal bending ye direction', units=None)
    A = Array(desc='cross sectional area', units='m**2')
    pitch = Array(desc='structural pitch relative to main axis.', units='deg')
    x_e = Array(desc='x-distance from main axis to center of elasticity', units='m')
    y_e = Array(desc='y-distance from main axis to center of elasticity', units='m')


