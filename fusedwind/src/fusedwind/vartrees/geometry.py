
from openmdao.main.api import VariableTree
from openmdao.lib.datatypes.api import Array, List, Str


class AirfoilGeometry(VariableTree):

    airfoil_name = Str(desc='Name of airfoil')
    points = Array(desc='Array of points ')
    le = Array(desc='Leading edge location')


class BeamGeometry(VariableTree):

    s = Array(desc='Blade main axis accumulated curve length (n)')
    main_axis = Array(desc='Blade main axis (n,3)')
    rot_x = Array(desc='x-rotation angle (n)')
    rot_y = Array(desc='y-rotation angle (n)')
    rot_z = Array(desc='z-rotation angle (n)')


class BladeGeometry(BeamGeometry):

    chord = Array(desc='Blade chord (n)')
    rthick = Array(desc='Blade relative thickness (n)')
    athick = Array(desc='Blade absolute thickness (n)')
    p_le = Array(desc='normalized distance along chord line from leading edge to main axis (n)')


class BladeGeometry3D(BladeGeometry):

    base_profiles = List(Array, desc='Names of base profile shapes')


class BodyOfRevolution(BeamGeometry):

    contour = Array(desc='Contour curve normal to main axis (n,3)')