
from openmdao.main.api import Component
from openmdao.lib.datatypes.api import VarTree, Str

from fusedwind.interface import base, implement_base
from fusedwind.turbine.geometry_vt import BladePlanformVT
from fusedwind.turbine.turbine_vt import AeroelasticHAWTVT
from fusedwind.turbine.environment_vt import TurbineEnvironmentVT
from fusedwind.turbine.rotoraero_vt import RotorOperationalData,\
                                           RotorOperationalDataArray,\
                                           DistributedLoadsVT,\
                                           DistributedLoadsExtVT,\
                                           RotorLoadsVT,\
                                           BeamDisplacementsVT


@base
class RotorAeroBase(Component):
    """
    Base class for models that can predict the power and thrust of wind turbine rotor
    for a single inflow case
    """

    pf = VarTree(BladePlanformVT(), iotype='in', desc='Blade geometric definition')
    inflow = VarTree(TurbineEnvironmentVT(), iotype='in', desc='Rotor inflow conditions')

    oper = VarTree(RotorOperationalData(), iotype='out', desc='Operational data')
    rotor_loads = VarTree(RotorLoadsVT(), iotype='out', desc='Rotor torque, power, and thrust')


@implement_base(RotorAeroBase)
class RotorAero(Component):
    """
    Class that extends the TurbineAeroBase with distributed blade
    loads for a single inflow case
    """

    pf = VarTree(BladePlanformVT(), iotype='in', desc='Blade geometric definition')
    inflow = VarTree(TurbineEnvironmentVT(), iotype='in', desc='Rotor inflow conditions')

    oper = VarTree(RotorOperationalData(), iotype='out', desc='Operational data')
    rotor_loads = VarTree(RotorLoadsVT(), iotype='out', desc='Rotor torque, power, and thrust')
    blade_loads = VarTree(DistributedLoadsExtVT(), iotype='out', desc='Spanwise load distributions')

@base
class RotorStructureBase(Component):
    """
    Base class for models that can predict blade deflections
    based on load distribution
    """

    blade_disps = VarTree(BeamDisplacementsVT(), iotype='out', desc='Blade deflections and rotations')


@base
class AeroElasticSolverBase(Component):
    """
    base class for aeroelastic solvers that computes both steady state aerodynamic loads
    and structural deflections in a monolithic analysis for a single case
    """

    wt = VarTree(AeroelasticHAWTVT(), iotype='in', desc='Turbine definition')
    inflow = VarTree(TurbineEnvironmentVT(), iotype='in', desc='Inflow conditions')

    oper = VarTree(RotorOperationalData(), iotype='out', desc='Operational data')
    rotor_loads = VarTree(RotorLoadsVT(), iotype='out', desc='Rotor torque, power, and thrust')
    blade_loads = VarTree(DistributedLoadsVT(), iotype='out', desc='Spanwise load distributions')

    blade_disps = VarTree(BeamDisplacementsVT(), iotype='out', desc='Blade deflections and rotations')


