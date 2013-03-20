#!/usr/bin/env python
# encoding: utf-8

from openmdao.main.api import Component
from openmdao.main.datatypes.api import Array, Slot

from fusedwind.vartrees.rotor import DistributedLoadsVT


class RotorAeroBase(Component):
    """Base component for rotor aerodynamic analysis"""

    # inputs
    Uhub = Array(iotype='in', units='m/s')
    Omega = Array(iotype='in', units='rpm')
    pitch = Array(iotype='in', units='deg')

    # outputs
    loads = Slot(DistributedLoadsVT, iotype='out')

    def __init__(self):
        super(RotorAeroBase, self).__init__()
        self.loads = DistributedLoadsVT()
