#!/usr/bin/env python
# encoding: utf-8

from openmdao.main.api import VariableTree
from openmdao.main.datatypes.api import Array, Float
import numpy as np


class SteadyWindBase(VariableTree):

    Uref = Float(desc='reference wind speed', units='m/s')
    zref = Float(desc='height for reference wind speed', units='m')
    z_interface = Float(desc='height for ground or sea', units='m')
    rho = Float(1.225, desc='density of air', units='kg/m**3')
    mu = Float(1.81206e-5, desc='dynamic viscosity of air', units='kg/m/s')
    beta = Float(0.0, desc='angle of wind relative to inertial x-direction', units='deg')


class PowerWindVT(SteadyWindBase):

    shearExp = Float(desc='exponent in power law')


class LogWindVT(VariableTree):

    roughness_length = Float(desc='surface roughness length of terrain', units='m')



class LinearWaveVT(VariableTree):

    hs = Float(desc='significant wave height (crest-to-trough)', units='m')
    T = Float(desc='period of waves', units='s')
    uc = Float(desc='mean current speed', units='m/s')
    z_surface = Float(desc='z location of water surface', units='m')
    z_bottom = Float(desc='z location of bottom of water', units='m')
    g = Float(9.81, iotype='in', desc='acceleration of gravity', units='m/s')
    rho = Float(1025.0, iotype='in', desc='water density', units='kg/m**3')
    mu = Float(8.9e-4, iotype='in', desc='dynamic viscosity of water', units='kg/m/s')
    cm = Float(2.0, iotype='in', desc='mass coefficient')
    beta = Float(0.0, iotype='in', desc='current directionality relative to x-direction', units='rad')



class SimpleSoilVT(VariableTree):

    G = Float(80.8e9, iotype='in', desc='shear modulus of soil', units='Pa')
    nu = Float(0.4, iotype='in', desc='Poissons ratio of soil')
    depth = Float(10.0, iotype='in', desc='depth of soil')
    rigid = Array(np.array([0, 1, 2, 3, 4, 5]), dtype=np.int,
        desc='indices for degrees of freedom which should be considered infinitely rigid \
        (order is x, theta_x, y, theta_y, z, theta_z)')
