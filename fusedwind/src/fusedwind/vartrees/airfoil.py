#!/usr/bin/env python
# encoding: utf-8

from openmdao.main.api import VariableTree
from openmdao.main.datatypes.api import Array, Slot, List


class PolarDataVT(VariableTree):
    """airfoil data at a given Reynolds number"""

    alpha = Array(units='deg', desc='angles of attack')
    cl = Array(desc='corresponding lift coefficients')
    cd = Array(desc='corresponding drag coefficients')
    cm = Array(desc='corresponding pitching moment coefficients')



class AirfoilDataVT(VariableTree):

    Re = Array(desc='Reynolds number')
    polars = List(Slot(PolarDataVT), desc='corresponding Polar data')



