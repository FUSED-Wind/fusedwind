#!/usr/bin/env python
# encoding: utf-8

from openmdao.main.api import Component
from openmdao.main.datatypes.api import Slot, Str, Float

from fusedwind.vartrees.airfoil import AirfoilDataVT


class BasicAirfoilBase(Component):
    """Evaluation of airfoil at angle of attack and Reynolds number"""

    # inputs
    alpha = Float(iotype='in', units='deg', desc='angle of attack')
    Re = Float(iotype='in', desc='Reynolds number')

    # outputs
    cl = Float(iotype='out', desc='lift coefficient')
    cd = Float(iotype='out', desc='drag coefficient')

    def forces(self, alpha, Re):
        """convenience method to use BasicAirfoilBase
        as a regular Python function as opposed to a component"""

        self.alpha = alpha
        self.Re = Re
        self.run()
        return self.cl, self.cd


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
