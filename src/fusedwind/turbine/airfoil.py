
from openmdao.main.api import Component
from openmdao.main.datatypes.api import Slot, Str, Float, Array, VarTree

from fusedwind.interface import base
from fusedwind.turbine.airfoil_vt import AirfoilDataVT


@base
class BasicAirfoilBase(Component):
    """Evaluation of airfoil at angle of attack and Reynolds number"""

    # inputs
    alpha = Float(iotype='in', units='deg', desc='angle of attack')
    Re = Float(iotype='in', desc='Reynolds number')

    # outputs
    cl = Float(iotype='out', desc='lift coefficient')
    cd = Float(iotype='out', desc='drag coefficient')
    cm = Float(iotype='out', desc='pitching moment coefficient')

    def forces(self, alpha, Re):
        """convenience method to use BasicAirfoilBase
        as a regular Python function as opposed to a component"""

        self.alpha = alpha
        self.Re = Re
        self.run()
        return self.cl, self.cd, self.cm


@base
class BasicAirfoilPolarBase(Component):
    """Evaluation of airfoil at a specific Reynolds number across an angle of attack range"""

    # inputs
    alpha = Array(iotype='in', units='deg', desc='angle of attack')
    Re = Float(iotype='in', desc='Reynolds number')

    # outputs
    cl = Array(iotype='out', desc='lift coefficient')
    cd = Array(iotype='out', desc='drag coefficient')
    cm = Array(iotype='out', desc='pitching moment coefficient')


@base
class ModifyAirfoilBase(Component):
    """Used for extrapolation, 3D corrections, etc.
    default behavior is to not do any modification
    """

    # inputs
    afIn = VarTree(AirfoilDataVT(), iotype='in', desc='tabulated airfoil data')

    # outputs
    afOut = VarTree(AirfoilDataVT(), iotype='out', desc='tabulated airfoil data')

    def execute(self):
        """provides a default behavior (to not modify the airfoil)"""

        self.afOut = self.afIn


@base
class ReadAirfoilBase(Component):
    """Read airfoil data from a file"""

    # inputs
    fileIn = Str(iotype='in', desc='name of file')

    # outputs
    afOut = VarTree(AirfoilDataVT(), iotype='out', desc='tabulated airfoil data')


@base
class WriteAirfoilBase(Component):
    """Write airfoil data to a file"""

    # inputs
    afIn = VarTree(AirfoilDataVT(), iotype='in', desc='tabulated airfoil data')
    fileOut = Str(iotype='in', desc='name of file')

