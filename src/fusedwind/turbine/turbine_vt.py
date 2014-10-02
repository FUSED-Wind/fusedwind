# Input structure for FUSED_Wind turbine

import numpy as np
from openmdao.main.api import VariableTree
from openmdao.lib.datatypes.api import Int, Float, Array, List, Str, Enum, Bool, VarTree, Slot

from fusedwind.turbine.structure_vt import BeamStructureVT
from fusedwind.turbine.geometry_vt import BeamGeometryVT
from fusedwind.turbine.aero_vt import AirfoilDataset
from fusedwind.turbine.environment_vt import TurbineEnvironmentVT


# Support Classes for Overall Orientation of structural components relative to one another
class OrientationBase(VariableTree):

    inipos = Array(np.zeros(3), desc='Initial position in global coordinates')
    eulerang = List(Array(np.zeros(3)), desc='sequence of euler angle rotations, x->y->z')


class OrientationRelative(VariableTree):

    mbdy1_name = Str(desc='Main body name to which the body is attached')
    eulerang = List(Array(np.zeros(3)), desc='sequence of euler angle rotations, x->y->z')
    initial_speed = Float()
    rotation_dof = Array([0, 0, 0])


class Constraint(VariableTree):

    con_name = Str()
    con_type = Enum('free', ('fixed', 'fixed_to_body', 'free', 'prescribed_angle'), desc='Constraint type')
    body1 = Str(desc='Main body name to which the body is attached')
    DOF = Array(np.zeros(6), desc='Degrees of freedom')


class MainBody(VariableTree):

    body_name = Str('body')
    subsystem = Enum('Tower', ('Rotor', 'Nacelle', 'Tower', 'Foundation'))

    geom = VarTree(BeamGeometryVT(), desc='Geometry of body containing main axis and rotations')
    orientations = List()

    def initialize_geom(self, nb=10):
        """
        convenience method for initializing geometry

        could be moved to an __init__ method, but often the geometry is set directly
        from e.g. a file
        """

        self.geom.main_axis = np.zeros((nb, 3))
        self.geom.rot_x = np.zeros(nb)
        self.geom.rot_y = np.zeros(nb)
        self.geom.rot_z = np.zeros(nb)

    def add_orientation(self, orientation):

        if orientation == 'base':
            self.orientations.append(OrientationBase())
        elif orientation == 'relative':
            self.orientations.append(OrientationRelative())


class AeroelasticMainBody(MainBody):

    beam_structure = List(BeamStructureVT)
    n_elements = Int(1)
    damping_posdef = Array(np.zeros(6))
    concentrated_mass = List(Array())
    constraints = List()

    def add_constraint(self, con_type, con_name=None, body1=None, DOF=None):
        """
        add a constraint
        """

        con = Constraint()
        con.con_type = con_type
        if con_type == 'fixed_to_body':
            con.body1 = body1
        if con_type in ('free', 'prescribed_angle'):
            if con_name is None:
                raise RuntimeError('Contraint name not specified')
            con.DOF = DOF
            con.con_name = con_name
            con.body1 = body1

        self.constraints.append(con)


class MainBodies(VariableTree):
    """
    Empty placeholder vartree for main bodies
    """

    bodies = List(desc='')

    def add_body(self, name, body=None):

        if body is None:
            if 'blade' in name:
                body = BladeGeometryVT()
            else:
                body = BeamGeometryVT()

        self.add(name, VarTree(body))
        self.bodies.append(name)


class DrivetrainPerformanceVT(VariableTree):

    gear_ratio = Float(desc='Transmission gear ratio')
    gearbox_efficiency = Float(desc='efficiency of gearbox')
    generator_efficiency = Array(desc='2-D array of generator efficiency as a function of power/rated power') 
    hss_brake_torque = Float(desc='fully deployed hss-brake torque')
    drive_torsional_spring = Float(desc='drivetrain torsional spring') # ?FAST inputs - not sure to include here
    drive_torsional_damper = Float(desc='drivetrain torsional damper') # ?FAST inputs - not sure to include here
    nacelle_yaw_spring = Float(desc='nacelle-yaw spring constant') # ?FAST inputs - not sure to include here
    nacelle_yaw_damper = Float(desc='nacelle-yaw damper constant') # ?FAST inputs - not sure to include here
    max_torque = Float(desc='Maximum allowable generator torque')
    

class ControlsVT(VariableTree):
    """Base class for controllers"""

    "TBD controls VT"
    # Options in FAST include: yaw, pitch, variable-speed, mech brake, tip-brake, rotor-teeter, furling, partial-span pitch
    Vin = Float(units='m/s')
    Vout = Float(units='m/s')
    ratedPower = Float(units='W')


class FixedSpeedFixedPitch(ControlsVT):

    Omega = Float(units='rpm')
    pitch = Float(units='deg')

    varSpeed = Bool(False)
    varPitch = Bool(False)


class FixedSpeedVarPitch(ControlsVT):

    Omega = Float(units='rpm')

    varSpeed = Bool(False)
    varPitch = Bool(True)


class VarSpeedFixedPitch(ControlsVT):

    minOmega = Float(units='rpm')
    maxOmega = Float(units='rpm')
    pitch = Float(units='deg')

    varSpeed = Bool(True)
    varPitch = Bool(False)


class VarSpeedVarPitch(ControlsVT):

    minOmega = Float(units='rpm')
    maxOmega = Float(units='rpm')

    varSpeed = Bool(True)
    varPitch = Bool(True)

# More generic variables can probably be added here which are pretty much in common to
# all controllers...

#####################
# Overall turbine definition in multi-body formulation


class BasicTurbineVT(VariableTree):

    turbine_name = Str('FUSED-Wind turbine', desc='Wind turbine name')
    docs = Str(desc='Human readable description of wind turbine')

    nblades = Int(3, desc='number of blades')
    orientation = Str('upwind')
    rotor_diameter = Float(units='m', desc='Rotor Diameter')
    hub_height = Float(units='m', desc='Hub height')
    drivetrain_config = Enum(1, (1, 2, 3, 4, 'x'), desc='Drive train configuration')
    iec_class = Str(desc='Primary IEC classification of the turbine')

    controls = VarTree(ControlsVT(), desc='control specifications VT')


class AeroelasticTurbineVT(BasicTurbineVT):

    tilt_angle = Float(units='deg', desc='rotor tilt angle')
    cone_angle = Float(units='deg', desc='rotor cone angle')
    hub_radius = Float(units='m', desc='Hub radius')
    tower_height = Float(units='m', desc='Tower height')
    towertop_length = Float(units='m', desc='Nacelle Diameter')
    shaft_length = Float(units='m', desc='Shaft length')

    environment = VarTree(TurbineEnvironmentVT(), desc='Inflow conditions')
    airfoildata = VarTree(AirfoilDataset(), desc='Airfoil Aerodynamic characteristics')

    main_bodies = Slot(MainBodies(), desc='List of main bodies')

    drivetrain_performance = VarTree(DrivetrainPerformanceVT(), desc='drivetrain performance VT')
