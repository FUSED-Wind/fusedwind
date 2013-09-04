#!/usr/bin/env python
# encoding: utf-8

from openmdao.main.api import VariableTree
from openmdao.main.datatypes.api import Array, Float
import numpy as np


class MonopileVT(VariableTree):

    z = Array(units='m', desc='reference heights of monopile/tower')
    d = Array(units='m', desc='diameter at ref heights')
    t = Array(units='m', desc='shell thickness at ref heights')
    n = Array(dtype=np.int, desc='number of elments for each section')

    E = Float(210e9, desc='modulus of elasticity', units='Pa')
    G = Float(80.8e9, desc='shear modulus of elasticity', units='Pa')
    rho = Float(8500.0, desc='modulus of elasticity', units='kg/m**3')
    sigma_y = Float(450.0e6, desc='yield stress', units='Pa')
