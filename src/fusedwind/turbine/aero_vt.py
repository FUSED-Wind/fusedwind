
from openmdao.main.api import VariableTree
from openmdao.lib.datatypes.api import VarTree, Float, Str, Array, Int, List


class AirfoilPolar(VariableTree):
    """A single airfoil polar"""

    desc = Str()
    rthick = Float(desc='relative thickness associated with airfoil polar set')
    aoa = Array(desc='angle of attack indices')
    cl = Array(desc='associated coefficient of lift')
    cd = Array(desc='associated coefficient of drag')
    cm = Array(desc='associated coefficient of the pitching moment')


class AirfoilDataset(VariableTree):
    """A set of airfoil polars for a range of relative thicknesses"""

    np = Int(desc='number of airfoil polars in set')
    polars = List(AirfoilPolar, desc='List of polars')