# Input structure for FUSED_Wind turbine
# extends vartrees.py from Frederik

import numpy as np
from openmdao.main.api import VariableTree, Component
from openmdao.lib.datatypes.api import Int, Float, Array, List, Str, Enum, Bool, VarTree, Slot

class AeroElasticSimulationSetup(VariableTree):

    time_start = Float(0., desc='Starting time of sampled output')
    time_stop = Float(0., desc='Ending time of sampled output')
    timestep = Float(0.001, desc='Sampling time step for simulation')


class TurbineEnvironmentVT(VariableTree):

    vhub = Float(desc='Hub-height velocity')
    density = Float(1.225, desc='air density')
    viscosity = Float(1.78405e-5, desc='air viscosity')

    inflow_type = Enum('constant',('constant','log','powerlaw','linear','user'), desc='shear type')
    shear_exp = Float(0.,iotype='in',desc='Shear exponent (when applicaple)') 
    kappa = Float(0.4,iotype='in',desc='Von Karman constant')
    z0 = Float(0.111,iotype='in',desc='Roughness length')


class OffshoreTurbineEnvironmentVT(TurbineEnvironment):

    Hs = Float(units='m', desc='Significant wave height')
    Tp = Float(units='s', desc='Peak wave period')
    WaveDir = Float(units='deg', desc='Direction of waves relative to turbine')

# I think it could be quite convenient to normalize all dimensions relative to e.g. blade length.
# The RotorAeroVT vartree then knows the radius and can be used in a code to dimensionalize the blade.
class BeamGeometryVT(VariableTree):

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
    I_p = Array(desc='torsional stiffness constant with respect to ze axis at the shear center', units='m**4/rad')
    k_x = Array(desc='shear factor for force in principal bending xe direction', units=None)
    k_y = Array(desc='shear factor for force in principal bending ye direction', units=None)
    A = Array(desc='cross sectional area', units='m**2')
    pitch = Array(desc='structural pitch relative to main axis.', units='deg')
    x_e = Array(desc='x-distance from main axis to center of elasticity', units='m')
    y_e = Array(desc='y-distance from main axis to center of elasticity', units='m')

class TowerGeometryVT(BeamGeometryVT):

    radius = Array(desc='Tower radius along main_axis')

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
    polars = List(AirfoilPolar, desc='List of polars')


# frza: haven't changed anything here, but having added BladeGeometryVT a lot of this vartree becomes redundant.
# We should discuss generality vs convenience: it is for readability easier to define stuff multiple times like this
# but geometry definitions are needed across a number of components such as structural, CFD and aeroelastic codes,
# so to me it makes sense to separate it from the RotorAeroVT vartree.
class RotorAeroVT(VariableTree):

    # geometry
    Rhub = Float(units='m', desc='hub radius')
    Rtip = Float(units='m', desc='tip radius')
    r = Array(units='m', desc='radial locations where blade is defined (should be increasing and not go all the way to hub or tip)')
    chord = Array(units='m', desc='chord length at each section')
    theta = Array(units='deg', desc='twist angle at each section (positive decreases angle of attack)')
    #c12_axis = Array(desc='Pitch axis of blade') # todo: variable location - used by Andrew's model and HAWC2 and indexed with radial stations
    af_set = VarTree(AirfoilDataset(), desc='names of airfoil file')

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
    subsystem = Enum('Rotor', ('Rotor', 'Nacelle', 'Tower', 'Foundation'))

    #Distributed blade properties
    ### TBD - would like to see what Andrew and Frederik think

class HubVT(TurbineComponent):

    diameter = Float(desc='hub diameter')
    subsystem = Enum('Rotor', ('Rotor', 'Nacelle', 'Tower', 'Foundation'))
 
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
    subsystem = Enum('Nacelle', ('Rotor', 'Nacelle', 'Tower', 'Foundation'))

class BearingVT(TurbineComponent):

    diameter = Float()
    subsystem = Enum('Nacelle', ('Rotor', 'Nacelle', 'Tower', 'Foundation'))
    
class GearboxVT(TurbineComponent):

    height = Float()
    length = Float()
    subsystem = Enum('Nacelle', ('Rotor', 'Nacelle', 'Tower', 'Foundation'))

# ? include high speed side or no?
class HighSpeedShaftVT(TurbineComponent):

    length = Float()
    subsystem = Enum('Nacelle', ('Rotor', 'Nacelle', 'Tower', 'Foundation'))

class MechanicalBrakeVT(TurbineComponent):

    diameter = Float()
    subsystem = Enum('Nacelle', ('Rotor', 'Nacelle', 'Tower', 'Foundation'))

class GeneratorVT(TurbineComponent):

    height = Float()
    diameter = Float()
    subsystem = Enum('Nacelle', ('Rotor', 'Nacelle', 'Tower', 'Foundation'))

class BedplateVT(TurbineComponent):

    front_length = Float()
    rear_length = Float()
    subsystem = Enum('Nacelle', ('Rotor', 'Nacelle', 'Tower', 'Foundation'))

class YawSystemVT(TurbineComponent):

    diameter = Float()
    subsystem = Enum('Nacelle', ('Rotor', 'Nacelle', 'Tower', 'Foundation'))

#class NacelleVT(TurbineComponent): # kld - move to turbine, composite of individual components, up to wrapper to translate

    #diameter = Float() 

class TowerVT(TurbineComponent):

    height = Float(desc='Tower height')
    bottom_diameter = Float(desc='Tower bottom diameter')
    top_diameter = Float(desc='Tower bottom diameter')
    subsystem = Enum('Tower', ('Rotor', 'Nacelle', 'Tower', 'Foundation'))

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
    beam_structure = List(BeamStructureVT)
    body_set = List([1, 1], desc='Index of beam structure set to use from st file')
    nbodies = Int(1)
    node_distribution = Str('c2_def')
    damping_posdef = Array(np.zeros(6))
    copy_main_body = Str()
    geom = VarTree(BeamGeometryVT(), desc='Geometry of body containing main axis and rotations')
    concentrated_mass = List(Array())
    body_set = Array([1, 1])
    orientations = List()
    constraints = List()

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

    pass


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
    

class DrivetrainPerformanceVT(VariableTree):
    pass


class ControlsVT(VariableTree):

    "TBD controls VT"
    # Options in FAST include: yaw, pitch, variable-speed, mech brake, tip-brake, rotor-teeter, furling, partial-span pitch

#####################
# Overall turbine definition in multi-body formulation


class TurbineVT(VariableTree):

    """ connects the set of components together using a HAWC2 multi-body approach """ 

    # overall characteristics (could go into a separate vartree to become accessible to lower fidelity models)
    nblades = Int(3, desc='number of blades')
    orientation = Str('upwind')
    rotor_radius = Float(units='m', desc='Nacelle Diameter')
    hub_height = Float(units='m', desc='Hub height')
    tilt_angle = Float(units='deg', desc='rotor tilt angle')
    cone_angle = Float(units='deg', desc='rotor cone angle')
    hub_overhang = Float(units='m', desc='Horizontal distance from tower axis to rotor center')
    hub_radius = Float(units='m', desc='Hub radius')
    tower_height = Float(units='m', desc='Tower height')
    tower_bottom_radius = Float(units='m', desc='Tower bottom radius')
    tower_top_radius = Float(units='m', desc='Tower top radius')
    nacelle_diameter = Float(units='m', desc='Nacelle Diameter')
    shaft_length = Float(units='m', desc='Shaft length')

    # vartrees
    blade_geom = VarTree(BladeGeometryVT(), desc='Blade geometry')
    tower_geom = VarTree(TowerGeometryVT(), desc='Tower geometry')

    inflow = VarTree(TurbineInflowVT(), desc='Inflow conditions')

    airfoildata = VarTree(AirfoilDataset(), desc='Airfoil Aerodynamic characteristics')
    rotor_aero = VarTree(RotorAeroVT(), desc='rotor aero properties VT')
    controller = VarTree(ControlsVT(), desc='controller settings')

    main_bodies = Slot(MainBodies(), desc='List of main bodies')

    nacelle_cd = Float(desc='nacelle drag coefficient')
    tower_cd = Float(desc='tower drag coeffficient')
    
    # ? include key aggregate properties of tilt, overhang, and coning?
    
    # drive and control properties   
    drivetrain_performance = VarTree(DrivetrainPerformanceVT(), desc='drivetrain performance VT')
    gen_performance = VarTree(GeneratorPerformanceVT(), desc='generator performance VT')
    controls = VarTree(ControlsVT(), desc='control specifications VT')

