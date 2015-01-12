
# --- 1 ---

from openmdao.main.api import Assembly, Component
from openmdao.lib.datatypes.api import VarTree

from fusedwind.interface import implement_base
from fusedwind.turbine.aeroelastic_solver import AeroElasticSolverBase
from fusedwind.turbine.turbine_vt import configure_turbine, AeroelasticHAWTVT
from fusedwind.turbine.geometry import SplinedBladePlanform, read_blade_planform
from fusedwind.turbine.environment_vt import TurbineEnvironmentVT
from fusedwind.turbine.rotoraero_vt import RotorOperationalData, \
                                           DistributedLoadsExtVT, \
                                           RotorLoadsVT, \
                                           BeamDisplacementsVT


@implement_base(AeroElasticSolverBase)
class AEsolver(Component):

    wt = VarTree(AeroelasticHAWTVT(), iotype='in', desc='Turbine definition')
    inflow = VarTree(TurbineEnvironmentVT(), iotype='in', desc='Inflow conditions')

    oper = VarTree(RotorOperationalData(), iotype='out', desc='Operational data')
    rotor_loads = VarTree(RotorLoadsVT(), iotype='out', desc='Rotor torque, power, and thrust')
    blade_loads = VarTree(DistributedLoadsExtVT(), iotype='out', desc='Spanwise load distributions')
    blade_disps = VarTree(BeamDisplacementsVT(), iotype='out', desc='Blade deflections and rotations')

    def execute(self):

        print 'run some analysis here'

# --- 2 ---

top = Assembly()

# add splined planform description
top.add('pf_splines', SplinedBladePlanform())
top.driver.workflow.add('pf_splines')

top.pf_splines.blade_length = 86.366
top.pf_splines.pfIn = read_blade_planform('data/DTU_10MW_RWT_blade_axis_prebend.dat')

# add aeroelastic solver
top.add('ae', AEsolver())
top.driver.workflow.add('ae')

# --- 3 ---

# configure the turbine with standard sub-components
configure_turbine(top.ae.wt)

# define overall dimensions
wt = top.ae.wt
wt.turbine_name = 'DTU 10MW RWT'
wt.doc = 'FUSED-Wind definition of the DTU 10MW RWT'
wt.tower_height = 115.63
wt.hub_height = 119.0
wt.towertop_height = 2.75
wt.shaft_length = 7.1
wt.tilt_angle = 5.0
wt.cone_angle = -2.5
wt.hub_radius = 2.8
wt.blade_length = 86.366
wt.rotor_diameter = 178.332
c = wt.set_machine_type('VarSpeedVarPitch')
c.vIn = 3.
c.vOut = 25.
c.minOmega = 6.
c.maxOmega = 9.6
c.minPitch = 0.

# --- 4 ---

# connect the splined planform to the blade geometry vartree
# in the aeroelastic solver
top.connect('pf_splines.pfOut', 'ae.wt.blade1.geom')

# --- 5 ---

# run it
top.run()

# --- 6 ---