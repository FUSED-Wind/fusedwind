#!/usr/bin/env python
# encoding: utf-8

from openmdao.main.api import Component
from openmdao.main.datatypes.api import Slot, Float

from fusedwind.vartrees.rotor import DistributedLoads, RotorLoads, HubLoads


class IntegrateLoads(Component):
    """integrate distributed blade loads to compute thrust, torque, power, and hub loads"""

    distributedLoads = Slot(DistributedLoads, iotype='in')
    R = Float(iotype='in', units='m', desc='rotor radius used in normalization')
    rho = Float(iotype='in', units='kg/m**3', desc='fluid density used in normalization')

    rotorLoads = Slot(RotorLoads, iotype='out')
    hubLoads = Slot(HubLoads, iotype='out')

    def __init__(self):
        super(IntegrateLoads, self).__init__()
        self.distributedLoads = DistributedLoads()
        self.rotorLoads = RotorLoads()
        self.hubLoads = HubLoads()

    def execute(self):
        print 'integrating loads'
