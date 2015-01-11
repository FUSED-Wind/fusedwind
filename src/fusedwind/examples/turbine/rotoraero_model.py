

from openmdao.main.api import Component
from openmdao.lib.datatypes.api import VarTree

from fusedwind.interface import implement_base
from fusedwind.turbine.geometry_vt import BladePlanformVT
from fusedwind.turbine.environment_vt import TurbineEnvironmentVT
from fusedwind.turbine.aeroelastic_solver import RotorAero
from fusedwind.turbine.rotoraero_vt import RotorOperationalData, \
                                           DistributedLoadsVT, \
                                           DistributedLoadsExtVT, \
                                           RotorLoadsVT


@implement_base(RotorAero)
class RotorAeroCode(Component):
    """
    Wrapper for a code capable of predicting the distributed loads
    on a rotor
    """

    pf = VarTree(BladePlanformVT(), iotype='in', desc='Blade geometric definition')
    inflow = VarTree(TurbineEnvironmentVT(), iotype='in', desc='Rotor inflow conditions')

    oper = VarTree(RotorOperationalData(), iotype='out', desc='Operational data')
    rotor_loads = VarTree(RotorLoadsVT(), iotype='out', desc='Rotor torque, power, and thrust')
    blade_loads = VarTree(DistributedLoadsExtVT(), iotype='out', desc='Spanwise load distributions')

    def execute(self):

        print 'perform analysis here'
