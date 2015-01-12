

from openmdao.main.api import Component
from openmdao.lib.datatypes.api import VarTree, List

from fusedwind.interface import base
from fusedwind.turbine.structure_vt import CrossSectionStructureVT, BeamStructureVT


@base
class StructuralCSPropsSolver(Component):
    """
    Base class for solvers capable of computing the structural beam properties
    of a blade.
    """

    cs2d = List(CrossSectionStructureVT, iotype='in', desc='Blade cross sectional structure geometry')

    beam_structure = VarTree(BeamStructureVT(), iotype='out', desc='Structural beam properties')

