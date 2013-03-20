#!/usr/bin/env python
# encoding: utf-8

from openmdao.main.api import VariableTree
from openmdao.main.datatypes.api import Array, Float, Int, List

from fusedwind.vartrees.airfoil import AirfoilDataVT


class DistributedLoadsVT(VariableTree):

    r = Array(units='m', desc='locations for distributed loads')
    theta = Array(units='deg', desc='local airfoil twist angle (necessary for coordinate transformations)')
    Np = Array(units='N/m', desc='force per unit length in normal direction of blade-aligned coordinate system')
    Tp = Array(units='N/m', desc='force per unit length in tangential direction of blade-aligned coordinate system')


class RotorLoadsVT(VariableTree):

    T = Float(units='N', desc='thrust')
    Q = Float(units='N*m', desc='torque')
    P = Float(units='W', desc='power')

    CT = Float(units='N', desc='thrust')
    CQ = Float(units='N*m', desc='torque')
    CP = Float(units='W', desc='power')


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

