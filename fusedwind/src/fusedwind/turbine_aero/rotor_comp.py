#!/usr/bin/env python
# encoding: utf-8

from openmdao.main.api import Component
from openmdao.main.datatypes.api import Array, Slot, List, Bool

from fusedwind.vartrees.rotor import DistributedLoadsVT, RotorAeroOutputVT, HubLoadsVT


class RotorAeroBase(Component):
    """Base component for rotor aerodynamic analysis"""

    # inputs
    Uhub = Array(iotype='in', units='m/s')
    Omega = Array(iotype='in', units='rpm')
    pitch = Array(iotype='in', units='deg')

    # temporary until Justin implements LazyComponent
    onlyRotorOut = Bool(True)

    # outputs
    rotorOut = Slot(RotorAeroOutputVT, iotype='out')
    distributedLoads = List(Slot(DistributedLoadsVT), iotype='out')
    hubLoads = List(Slot(HubLoadsVT), iotype='out')

    def __init__(self):
        super(RotorAeroBase, self).__init__()
        self.rotorOut = RotorAeroOutputVT()
        # self.distributedLoads = [DistributedLoadsVT()]
        # self.hubLoads = [HubLoadsVT()]



