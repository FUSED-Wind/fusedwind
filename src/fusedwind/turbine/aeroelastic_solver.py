
from openmdao.main.api import Component
from openmdao.lib.datatypes.api import VarTree

from fusedwind.interface import base, implement_base
from fusedwind.turbine.turbine_vt import AeroelasticHAWTVT


@base
class AeroElasticSolverBase(Component):
    """
    base class for aeroelastic solvers
    """

    wt = VarTree(AeroelasticHAWTVT(), iotype='in', desc='Turbine definition')