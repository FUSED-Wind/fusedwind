# Input structure for FUSED_Wind turbine
# extends vartrees.py from Frederik

import numpy as np
from openmdao.main.api import VariableTree
from openmdao.lib.datatypes.api import Int, Float, Array, List, Str, Enum, Bool, VarTree

#####################
# Aerodynamic Properties Variable Trees
class AirfoilPolar(VariableTree):
    """A single airfoil polar"""

    desc = Str()
    rthick = Float(desc='relative thickness associated with airfoil polar set')
    aoa = Array(desc='angle of attack indices')
    cl = Array(desc='associated coefficient of lift')
    cd = Array(desc='associated coefficient of drag')
    cm = Array(desc='associated coefficient of the pitching moment')

class AirfoilDataset(VariableTree):
    """A set of airfoil polars for a range of relative thicknesses"""

    np = Int(desc='number of airfoil polars in set')
    polars = List(HAWC2AirfoilPolar, desc='List of polars')

class RotorAeroVT(VariableTree):

    # geometry
    Rhub = Float(units='m', desc='hub radius')
    Rtip = Float(units='m', desc='tip radius')
    r = Array(units='m', desc='radial locations where blade is defined (should be increasing and not go all the way to hub or tip)')
    chord = Array(units='m', desc='chord length at each section')
    theta = Array(units='deg', desc='twist angle at each section (positive decreases angle of attack)')
    #c12_axis = Array(desc='Pitch axis of blade') # todo: variable location - used by Andrew's model and HAWC2 and indexed with radial stations
    af_set = VarTree(AirfoilDataSet, desc='names of airfoil file')

#####################
# Turbine Component Structure Variable Trees
# General class for Mass properties and Turbine Component
class MassProperties(VariableTree):
    """mass and mass moments of inertia of a component"""

    mass = Float(units='kg', desc='mass of object')
    Ixx = Float(units='kg*m**2', desc='mass moment of inertia about x-axis') # todo: arrary or not?
    Iyy = Float(units='kg*m**2', desc='mass moment of inertia about y-axis')
    Izz = Float(units='kg*m**2', desc='mass moment of inertia about z-axis')
    Ixy = Float(units='kg*m**2', desc='mass x-y product of inertia')
    Ixz = Float(units='kg*m**2', desc='mass x-z product of inertia')
    Iyz = Float(units='kg*m**2', desc='mass y-z product of inertia')

class TurbineComponent(VariableTree):
    """ Variable Tree Common to all Turbine Components """

    mp = VarTree(MassProperties(), desc = "mass and mass moments of intertia of a component")
    #? include other generic component properties?

# Specific Component and Subsystem Variable Trees
# Component class included for each main load-bearing component of the machine; inherit from turbine component above
# Subsystem aggregations (i.e. overall rotor mass, nacelle mass) handled at the turbine or external wrapper level
class BladeVT(TurbineComponent):

    length = Float(desc='blade length')
    root_chord = Float(desc='Blade root chord')
    max_chord = Float(desc='Blade maximum chord')
    tip_chord = Float(desc='Blade tip chord')
    subsystem = Enum('Rotor', ('Rotor', 'Nacelle', 'Tower', 'Foundation')

    #Distributed blade properties
    ### TBD - would like to see what Andrew and Frederik think

class HubVT(TurbineComponent):

    diameter = Float(desc='hub diameter')
    subsystem = Enum('Rotor', ('Rotor', 'Nacelle', 'Tower', 'Foundation')
 
# ? include pitch system as component or treat as additional rotor mass at c.m.

#class RotorVT(VariableTree): # kld - move to turbine, composite of individual components, up to wrapper to translate

    #hub_height = Float(desc='Hub height')
    #nblades = Int(desc='Number of blades')
    #tilt_angle = Float(desc='Tilt angle') 
    #cone_angle = Float(desc='Cone angle') 
    #diameter = Float(desc='Rotor diameter') 
    # mass = Float(desc='Total mass')
    # overhang = Float(desc='Rotor overhang')

class LowSpeedShaftVT(TurbineComponent):

    length = Float()
    subsystem = Enum('Nacelle', ('Rotor', 'Nacelle', 'Tower', 'Foundation')

class BearingVT(TurbineComponent):

    diameter = Float()
    subsystem = Enum('Nacelle', ('Rotor', 'Nacelle', 'Tower', 'Foundation')
    
class GearboxVT(TurbineComponent):

    height = Float()
    length = Float()
    subsystem = Enum('Nacelle', ('Rotor', 'Nacelle', 'Tower', 'Foundation')

# ? include high speed side or no?
class HighSpeedShaftVT(TurbineComponent):

    length = Float()
    subsystem = Enum('Nacelle', ('Rotor', 'Nacelle', 'Tower', 'Foundation')

class MechanicalBrakeVT(TurbineComponent):

    diameter = Float()
    subsystem = Enum('Nacelle', ('Rotor', 'Nacelle', 'Tower', 'Foundation')

class GeneratorVT(TurbineComponent):

    height = Float()
    diameter = Float()
    subsystem = Enum('Nacelle', ('Rotor', 'Nacelle', 'Tower', 'Foundation')

class BedplateVT(TurbineComponent):

    front_length = Float()
    rear_length = Float()
    subsystem = Enum('Nacelle', ('Rotor', 'Nacelle', 'Tower', 'Foundation')

class YawSystemVT(TurbineComponent):

    diameter = Float()
    subsystem = Enum('Nacelle', ('Rotor', 'Nacelle', 'Tower', 'Foundation')

#class NacelleVT(TurbineComponent): # kld - move to turbine, composite of individual components, up to wrapper to translate

    #diameter = Float() 

class TowerVT(TurbineComponent):

    height = Float(desc='Tower height')
    bottom_diameter = Float(desc='Tower bottom diameter')
    top_diameter = Float(desc='Tower bottom diameter')
    subsystem = Enum('Tower', ('Rotor', 'Nacelle', 'Tower', 'Foundation')

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
    body_type = Str('timoschenko')
    st_filename = Str()
    beam_structure = List(HAWC2BeamStructure)
    body_set = List([1, 1], desc='Index of beam structure set to use from st file')
    nbodies = Int(1)
    node_distribution = Str('c2_def')
    damping_posdef = Array(np.zeros(6))
    copy_main_body = Str()
    c12axis = Array(desc='C12 axis containing (x_c12, y_c12, z_c12, twist)')
    concentrated_mass = List(Array())
    body_set = Array([1, 1])
    orientations = List()
    constraints = List()

    def add_orientation(self, orientation):

        if orientation == 'base':
            self.orientations.append(OrientationBase())
        elif orientation == 'relative':
            self.orientations.append(OrientationRelative())

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

#####################
# Drivetrain and Controls Performance Variable Trees
class TransmissionPerformanceVT(VariableTree):

    gear_ratio = Float(desc='Transmission gear ratio')
    gearbox_efficiency = Float(desc='efficiency of gearbox')
    hss_brake_torque = Float(desc='fully deployed hss-brake torque')
    drive_torsional_spring = Float(desc='drivetrain torsional spring') # ?FAST inputs - not sure to include here
    drive_torsional_damper = Float(desc='drivetrain torsional damper') # ?FAST inputs - not sure to include here
    nacelle_yaw_spring = Float(desc='nacelle-yaw spring constant') # ?FAST inputs - not sure to include here
    nacelle_yaw_damper = Float(desc='nacelle-yaw damper constant') # ?FAST inputs - not sure to include here
    
class GeneratorPerformanceVT(VariableTree):

    power = Float(desc='Generator power')
    max_torque = Float(desc='Maximum allowable generator torque')
    generator_efficiency = Array(desc='2-D array of generator efficiency as a function of power/rated power') 
    
class ControlsVT(VariableTree):

    "TBD controls VT"
    # Options in FAST include: yaw, pitch, variable-speed, mech brake, tip-brake, rotor-teeter, furling, partial-span pitch

#####################
# Overall turbine definition in multi-body formulation
class TurbineVT(VariableTree):

    """ connects the set of components together using a HAWC2 multi-body approach """ 
    # aero properties
    rotor_aero = VarTree(RotorAeroVT(), desc='rotor aero properties VT')
    nacelle_cd = Float(desc='nacelle drag coefficient')
    tower_cd = Float(desc='tower drag coeffficient')
    
    # structure properties
    # TBD - discussion on what to include - should take approach of multi-body formulation and add bodies as relevant
    additional_rotor_mass = Float(desc='additional rotor mass from miscellaneous, non-load bearing components; treated as point mass at rotor c.m.')
    additional_nacelle_mass = Float(desc='additional nacelle mass from miscellaneous, non-load bearing components; treated as point mass at nacelle c.m.')
    additional_tower_mass = Float(desc='additional tower mass from miscellaneous, non-load bearing components; treated as point mass at tower c.m.')
    # ? include key aggregate properties of tilt, overhang, and coning?
    
    # drive and control properties   
    drivetrain_performance = VarTree(DrivetrainPerformanceVT(), desc='drivetrain performance VT')
    gen_perforamnce = VarTree(GeneratorPerformanceVT(), desc='generator performance VT')
    controls = VarTree(ControlsVT(), desc='control specifications VT')

    # support functions for configuration, something along these lines would be nice to include
    # would like to allow for the user to control configuration
    '''def configure_wt(self):
        
        if not self.from_file:
            self.configure_tower_body()
            self.configure_towertop_body()
            self.configure_shaft_body()
            self.configure_hub_bodies()
            self.configure_blade_bodies()

        self.add_tower_aerodrag()
        self.add_nacelle_aerodrag()

    def configure_tower_body(self):
        """convenience method for adding tower body with orientation and constraints"""

        b = self.get_main_body('tower')
        b.c12axis = np.zeros((10, 4))
        b.c12axis[:, 2] = np.linspace(0, -self.tower.height, 10)
        b.add_orientation('base')
        b.orientations[0].eulerang.append(np.array([0, 0, 0]))
        b.add_constraint('fixed')

        return b

    def configure_towertop_body(self):
        """convenience method for adding towertop body with orientation and constraints"""

        b = self.get_main_body('towertop')
        b.c12axis = np.zeros((2, 4))
        b.c12axis[-1, 2] = -self.nacelle.diameter / 2.
        b.add_orientation('relative')
        b.orientations[0].mbdy1_name = 'tower'
        b.orientations[0].eulerang.append(np.array([0, 0, 0]))
        b.add_constraint('fixed_to_body', body1='tower')

    def configure_shaft_body(self):
        """convenience method for adding shaft body with orientation and constraints"""

        b =self.get_main_body('shaft')
        b.c12axis = np.zeros((5, 4))
        b.c12axis[:, 2] = np.linspace(0, self.shaft.length, 5)
        b.add_orientation('relative')
        b.orientations[0].mbdy1_name = 'towertop'
        b.orientations[0].eulerang.append(np.array([90, 0, 0]))
        b.orientations[0].eulerang.append(np.array([self.rotor.tilt_angle, 0, 0]))
        b.orientations[0].initial_speed = 0.314 # ???
        b.orientations[0].rotation_dof = [0, 0, -1]
        b.add_constraint('free', body1='towertop', con_name='shaft_rot', DOF=np.array([0,0,0,0,0,-1]))

    def configure_hub_bodies(self):
        """convenience method for adding hub bodies with orientation and constraints"""

        b = self.get_main_body('hub1')
        b.c12axis = np.zeros((2, 4))
        b.c12axis[1, 2] = self.hub.diameter/2.
        b.nbodies = 1
        b.add_orientation('relative')
        b.orientations[0].mbdy1_name = 'shaft'
        b.orientations[0].eulerang.append(np.array([-90, 0, 0]))
        b.orientations[0].eulerang.append(np.array([0., 180., 0]))
        b.orientations[0].eulerang.append(np.array([self.rotor.cone_angle, 0, 0]))
        b.add_constraint('fixed_to_body', body1='shaft')

        for i in range(1, self.rotor.nblades):
            b = self.get_main_body('hub'+str(i+1))
            b.copy_main_body = 'hub1'
            b.add_orientation('relative')
            b.orientations[0].mbdy1_name = 'shaft'
            b.orientations[0].eulerang.append(np.array([-90, 0, 0]))
            b.orientations[0].eulerang.append(np.array([0., 60. - (i-1) * 120., 0]))
            b.orientations[0].eulerang.append(np.array([self.rotor.cone_angle, 0, 0]))
            b.add_constraint('fixed_to_body', body1='shaft')

    def configure_blade_bodies(self):
        """convenience method for adding blade bodies with orientation and constraints"""

        b = self.get_main_body('blade1')
        b.c12axis[:, :3] = self.blade_ae.c12axis
        b.c12axis[:, 3] = self.blade_ae.twist
        b.nbodies = 10
        b.add_orientation('relative')
        b.orientations[0].mbdy1_name = 'hub1'
        b.orientations[0].eulerang.append(np.array([0, 0, 0]))
        b.add_constraint('prescribed_angle', body1='hub1', con_name='pitch1', DOF=np.array([0,0,0,0,0,-1]))

        for i in range(1, self.rotor.nblades):
            b = self.get_main_body('blade'+str(i+1))
            b.copy_main_body = 'blade1'
            b.add_orientation('relative')
            b.orientations[0].mbdy1_name = 'hub'+str(i+1)
            b.orientations[0].eulerang.append(np.array([0, 0, 0]))
            b.add_constraint('prescribed_angle', body1='hub'+str(i+1), con_name='pitch'+str(i+1), DOF=np.array([0,0,0,0,0,-1]))'''