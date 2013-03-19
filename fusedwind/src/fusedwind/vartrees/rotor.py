#!/usr/bin/env python
# encoding: utf-8

from openmdao.main.api import VariableTree
from openmdao.main.datatypes.api import Array, Float


class DistributedLoads(VariableTree):

    r = Array(units='m', desc='locations for distributed loads')
    theta = Array(units='deg', desc='local airfoil twist angle (necessary for coordinate transformations)')
    Np = Array(units='N/m', desc='force per unit length in normal direction of blade-aligned coordinate system')
    Tp = Array(units='N/m', desc='force per unit length in tangential direction of blade-aligned coordinate system')


class RotorLoads(VariableTree):

    T = Float(units='N', desc='thrust')
    Q = Float(units='N*m', desc='torque')
    P = Float(units='W', desc='power')

    CT = Float(units='N', desc='thrust')
    CQ = Float(units='N*m', desc='torque')
    CP = Float(units='W', desc='power')


class HubLoads(VariableTree):

    Fx = Float(units='N', desc='x-force in wind-aligned coordinate system')
    Fy = Float(units='N', desc='y-force in wind-aligned coordinate system')
    Fz = Float(units='N', desc='z-force in wind-aligned coordinate system')
    Mx = Float(units='N*m', desc='x-moment in wind-aligned coordinate system')
    My = Float(units='N*m', desc='y-moment in wind-aligned coordinate system')
    Mz = Float(units='N*m', desc='z-moment in wind-aligned coordinate system')
