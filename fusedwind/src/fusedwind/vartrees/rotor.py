#!/usr/bin/env python
# encoding: utf-8

from openmdao.main.api import VariableTree
from openmdao.main.datatypes.api import Array, Float, Int, List, Bool
from math import sin, cos, radians, pi
import numpy as np

from fusedwind.vartrees.airfoil import AirfoilDataVT

class DistributedLoadsVT(VariableTree):
    """at one wind speed"""

    r = Array(units='m', desc='locations for distributed loads')
    theta = Array(units='deg', desc='local airfoil twist angle (necessary for coordinate transformations)')
    Np = Array(units='N/m', desc='force per unit length in normal direction of blade-aligned coordinate system')
    Tp = Array(units='N/m', desc='force per unit length in tangential direction of blade-aligned coordinate system')
    Rp = Array(units='N/m', desc='force per unit length in radial direction of blade-aligned coordinate system')


class RotorAeroOutputVT(VariableTree):

    T = Array(units='N', desc='thrust')
    Q = Array(units='N*m', desc='torque')
    P = Array(units='W', desc='power')

    CT = Array(desc='thrust coefficient: T / (q * A)')
    CQ = Array(desc='torque coefficient: Q / (q * A * R)')
    CP = Array(desc='power coefficient: P / (q * A * Uinf)')



class HubLoadsVT(VariableTree):

    Fx = Float(units='N', desc='x-force in wind-aligned coordinate system')
    Fy = Float(units='N', desc='y-force in wind-aligned coordinate system')
    Fz = Float(units='N', desc='z-force in wind-aligned coordinate system')
    Mx = Float(units='N*m', desc='x-moment in wind-aligned coordinate system')
    My = Float(units='N*m', desc='y-moment in wind-aligned coordinate system')
    Mz = Float(units='N*m', desc='z-moment in wind-aligned coordinate system')



class BEMRotorVT(VariableTree):

    r = Array(units='m', desc='radial locations where blade is defined (should be increasing and not go all the way to hub or tip)')
    chord = Array(units='m', desc='chord length at each section')
    theta = Array(units='deg', desc='twist angle at each section (positive decreases angle of attack)')
    airfoil = List(AirfoilDataVT, desc='airfoil data for each section')
    Rhub = Float(units='m', desc='hub radius')
    Rtip = Float(units='m', desc='tip radius')
    B = Int(desc='number of blades')




def getRotorAeroOutput(distributedLoads, Uhub, Omega, precone, B, R, rho):
    """convenience method to integrate distributed loads

    Parameters
    ----------
    distributedLoads : list(DistributedLoadsVT)
        loads at different wind speeds
    Uhub : array_like (m/s)
        hub height wind speed
    Omega : array_like (rpm)
        rotor rotation speed
    precone : float (deg)
        precone angle of rotor
    B : int
        number of blades
    R : float (m)
        rotor radius used in normalization
    rho : float (m)
        fluid density used in normalization

    Returns
    -------
    output : RotorAeroOutputVT
        thrust, torque, power

    """

    # initialize
    precone = radians(precone)
    T = np.zeros_like(Uhub)
    Q = np.zeros_like(Uhub)

    # loop through load cases
    for idx, load in enumerate(distributedLoads):

        T = B * (cos(precone) * np.trapz(load.Np, load.r) - sin(precone) * np.trapz(load.Rp, load.r))
        Q = B * cos(precone) * np.trapz(load.r*load.Tp, load.r)

    # power
    P = Q * Omega*pi/30.0

    # normalize
    q = 0.5 * rho * Uhub**2
    A = pi * R**2
    CT = T / (q * A)
    CQ = Q / (q * A * R)
    CP = P / (q * A * Uhub)

    output = RotorAeroOutputVT()
    output.T = T
    output.Q = Q
    output.P = P
    output.CT = CT
    output.CQ = CQ
    output.CP = CP

    return output


def getHubLoads(self):
    # TODO: need to reintegrate coordinate transformations
    pass





class MachineTypeBaseVT(VariableTree):
    """not meant to be instantiated directly"""

    Vin = Float(units='m/s')
    Vout = Float(units='m/s')
    ratedPower = Float(units='W')


class FixedSpeedFixedPitch(MachineTypeBaseVT):

    Omega = Float(units='rpm')
    pitch = Float(units='deg')

    varSpeed = Bool(False, desc='')
    varPitch = Bool(False, desc='')



class FixedSpeedVarPitch(MachineTypeBaseVT):

    Omega = Float(units='rpm')

    varSpeed = Bool(False, desc='')
    varPitch = Bool(True, desc='')


class VarSpeedFixedPitch(MachineTypeBaseVT):

    minOmega = Float(units='rpm')
    maxOmega = Float(units='rpm')
    pitch = Float(units='deg')

    varSpeed = Bool(True, desc='')
    varPitch = Bool(False, desc='')


class VarSpeedVarPitch(MachineTypeBaseVT):

    minOmega = Float(units='rpm')
    maxOmega = Float(units='rpm')

    varSpeed = Bool(True, desc='')
    varPitch = Bool(True, desc='')
