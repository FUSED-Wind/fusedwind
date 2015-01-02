# Input structure for FUSED_Wind turbine

import numpy as np
from openmdao.main.api import VariableTree
from openmdao.lib.datatypes.api import Int, Float, Array, List, Str, Enum, Bool, VarTree, Slot

from fusedwind.turbine.structure_vt import BeamStructureVT
from fusedwind.turbine.geometry_vt import BeamGeometryVT, BladePlanformVT, TubularTowerGeometryVT
from fusedwind.turbine.airfoilaero_vt import AirfoilDatasetVT
from fusedwind.turbine.environment_vt import TurbineEnvironmentVT


class MainBody(VariableTree):

    body_name = Str('body')
    subsystem = Enum('Tower', ('Rotor', 'Nacelle', 'Tower', 'Foundation'))

    beam_structure = VarTree(BeamStructureVT(), desc='Structural beam properties of the body')
    mass = Float(desc='mass of the body')

    damping_posdef = Array(np.zeros(6))
    concentrated_mass = List(Array())


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
    minPitch = Float(units='deg')

    varSpeed = Bool(True)
    varPitch = Bool(True)

# More generic variables can probably be added here which are pretty much in common to
# all controllers...


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


class AeroelasticHAWTVT(BasicTurbineVT):

    tilt_angle = Float(units='deg', desc='Rotor tilt angle')
    cone_angle = Float(units='deg', desc='Rotor cone angle')
    hub_radius = Float(units='m', desc='Hub radius')
    blade_length = Float(units='m', desc='blade length')
    tower_height = Float(units='m', desc='Tower height')
    towertop_length = Float(units='m', desc='Nacelle Diameter')
    shaft_length = Float(units='m', desc='Shaft length')

    airfoildata = VarTree(AirfoilDatasetVT(), desc='Airfoil Aerodynamic characteristics')

    drivetrain_performance = VarTree(DrivetrainPerformanceVT(), desc='drivetrain performance VT')

    bodies = List()

    def add_main_body(self, name, body=None):

        if body is None:

            body = MainBody()
            
            if 'blade' in name:
                body.remove('geom')
                body.add('geom', VarTree(BladePlanformVT()))
            if 'tower' in name:
                body.remove('geom')
                body.add('geom', VarTree(TubularTowerGeometryVT()))

        self.add(name, VarTree(body))
        self.bodies.append(name)

        return getattr(self, name)

    def get_main_body(self, name):

        return getattr(self, name)

    def remove_main_body(self, name):

        self.delete(name)

    def set_machine_type(self, machine_type):

        self.remove('controls')

        if machine_type == 'FixedSpeedFixedPitch':
            self.add('controls', VarTree(FixedSpeedFixedPitch()))
        if machine_type == 'FixedSpeedVarPitch':
            self.add('controls', VarTree(FixedSpeedVarPitch()))
        if machine_type == 'VarSpeedFixedPitch':
            self.add('controls', VarTree(VarSpeedFixedPitch()))
        if machine_type == 'VarSpeedVarPitch':
            self.add('controls', VarTree(VarSpeedVarPitch()))

        return self.controls

def create_turbine(cls, name='wt'):
    """
    method that adds an AeroelasticHAWTVT vartree too an Assembly instance 
    """

    cls.add(name, VarTree(AeroelasticHAWTVT()))
    return getattr(cls, name)

def configure_turbine(wt):
    """
    method that configures an AeroelasticHAWTVT instance with
    standard components
    """

    b = wt.add_main_body('tower')
    b.subsystem = 'Tower'
    wt.add_main_body('towertop')
    b.subsystem = 'Nacelle'
    wt.add_main_body('shaft')
    b.subsystem = 'Nacelle'
    wt.add_main_body('hub1')
    b.subsystem = 'Rotor'
    wt.add_main_body('blade1')
    b.subsystem = 'Rotor'

