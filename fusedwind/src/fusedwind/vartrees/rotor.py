#!/usr/bin/env python
# encoding: utf-8

from openmdao.main.api import VariableTree
from openmdao.main.datatypes.api import Array, Float, Int, List, Bool, Str, Enum
import numpy as np


# ------ INPUT: BEM rotor description -----------


class BEMRotorVT(VariableTree):

    r = Array(units='m', desc='radial locations where blade is defined (should be increasing and not go all the way to hub or tip)')
    chord = Array(units='m', desc='chord length at each section')
    theta = Array(units='deg', desc='twist angle at each section (positive decreases angle of attack)')
    airfoil = List(Str, desc='names of airfoil file')
    airfoil_base_path = Str('path to directory containing airfoil files')
    airfoil_file_type = Str('type of airfoil file (e.g., AeroDyn)')
    Rhub = Float(units='m', desc='hub radius')
    Rtip = Float(units='m', desc='tip radius')
    B = Int(desc='number of blades')
    precone = Float(0.0, desc='precone angle', units='deg')
    tilt = Float(0.0, desc='shaft tilt', units='deg')
    yaw = Float(0.0, desc='yaw error', units='deg')
    hubheight = Float(units='m')





# ----- INPUT: structural layup description ------


class RotorStructureVT(VariableTree):

    r = Array(units='m', desc='radial locations where composite sections are defined (from hub to tip)')
    chord = Array(units='m', desc='chord length at each section')
    theta = Array(units='deg', desc='twist angle at each section (positive decreases angle of attack)')
    le_location = Array(desc='location of pitch axis relative to leading edge in normalized chord units')
    nweb = Array(dtype=np.int, desc='number of shear webs at each location')

    compSec = List(Str, desc='names of composite section layup files')
    compSec_base_path = Str(desc='path to directory containing compSec files')
    compSec_file_type = Str(desc='type of compSec file (e.g., PreComp)')

    profile = List(Str, desc='names of profile shape files')
    profile_base_path = Str(desc='path to directory containing profile files')
    profile_file_type = Str(desc='type of profile file (e.g., PreComp)')

    materials = Str(desc='name/path of materials file')
    materials_file_type = Str(desc='type of materials file (e.g., PreComp)')





# ------ INPUT: Machine Type -----------


class MachineTypeBaseVT(VariableTree):
    """not meant to be instantiated directly"""

    turbine_name = Str('FUSED-Wind turbine', desc='Wind turbine name')
    orientation = Enum('upwind', ('upwind', 'downwind'))

    Vin = Float(units='m/s')
    Vout = Float(units='m/s')
    ratedPower = Float(units='W')


class FixedSpeedFixedPitch(MachineTypeBaseVT):

    Omega = Float(units='rpm')
    pitch = Float(units='deg')

    varSpeed = Bool(False)
    varPitch = Bool(False)



class FixedSpeedVarPitch(MachineTypeBaseVT):

    Omega = Float(units='rpm')

    varSpeed = Bool(False)
    varPitch = Bool(True)


class VarSpeedFixedPitch(MachineTypeBaseVT):

    minOmega = Float(units='rpm')
    maxOmega = Float(units='rpm')
    pitch = Float(units='deg')

    varSpeed = Bool(True)
    varPitch = Bool(False)


class VarSpeedVarPitch(MachineTypeBaseVT):

    minOmega = Float(units='rpm')
    maxOmega = Float(units='rpm')

    varSpeed = Bool(True)
    varPitch = Bool(True)




# # ------ OUTPUT: -----------


# class DistributedLoadsVT(VariableTree):
#     """at one wind speed"""

#     r = Array(units='m', desc='locations for distributed loads')
#     theta = Array(units='deg', desc='local airfoil twist angle (necessary for coordinate transformations)')
#     Px = Array(units='N/m', desc='force per unit length in x-direction of blade-aligned coordinate system')
#     Py = Array(units='N/m', desc='force per unit length in y-direction of blade-aligned coordinate system')
#     Pz = Array(units='N/m', desc='force per unit length in z-direction of blade-aligned coordinate system')


# class RotorAeroOutputVT(VariableTree):

#     T = Array(units='N', desc='thrust')
#     Q = Array(units='N*m', desc='torque')
#     P = Array(units='W', desc='power')

#     CT = Array(desc='thrust coefficient: T / (q * A)')
#     CQ = Array(desc='torque coefficient: Q / (q * A * R)')
#     CP = Array(desc='power coefficient: P / (q * A * Uinf)')



# class HubLoadsVT(VariableTree):

#     Fx = Float(units='N', desc='x-force in wind-aligned coordinate system')
#     Fy = Float(units='N', desc='y-force in wind-aligned coordinate system')
#     Fz = Float(units='N', desc='z-force in wind-aligned coordinate system')
#     Mx = Float(units='N*m', desc='x-moment in wind-aligned coordinate system')
#     My = Float(units='N*m', desc='y-moment in wind-aligned coordinate system')
#     Mz = Float(units='N*m', desc='z-moment in wind-aligned coordinate system')






