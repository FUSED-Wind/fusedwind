#!/usr/bin/env python
# encoding: utf-8

from openmdao.main.api import Component
from openmdao.main.datatypes.api import Slot, Str

from fusedwind.vartrees.airfoil import AirfoilDataVT



class ModifyAirfoilBase(Component):
    """Used for extrapolation, 3D corrections, etc.
    default behavior is to not do any modification

    """

    # inputs
    afIn = Slot(AirfoilDataVT, iotype='in', desc='tabulated airfoil data')

    # outputs
    afOut = Slot(AirfoilDataVT, iotype='out', desc='tabulated airfoil data')

    def __init__(self):
        super(ModifyAirfoilBase, self).__init__()
        self.afIn = AirfoilDataVT()
        self.afOut = AirfoilDataVT()

    def execute(self):
        """provides a default behavior (to not modify the airfoil)"""
        self.afOut = self.afIn



class ReadAirfoilBase(Component):
    """Read airfoil data from a file"""

    # inputs
    fileIn = Str(iotype='in', desc='name of file')

    # outputs
    afOut = Slot(AirfoilDataVT, iotype='out', desc='tabulated airfoil data')

    def __init__(self):
        super(ReadAirfoilBase, self).__init__()
        self.afOut = AirfoilDataVT()




class WriteAirfoilBase(Component):
    """Write airfoil data to a file"""

    # inputs
    afIn = Slot(AirfoilDataVT, iotype='in', desc='tabulated airfoil data')
    fileOut = Str(iotype='in', desc='name of file')

    def __init__(self):
        super(WriteAirfoilBase, self).__init__()
        self.afIn = AirfoilDataVT()
