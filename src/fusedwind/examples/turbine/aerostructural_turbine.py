
# --- 1 ---

import numpy as np

from openmdao.main.api import Assembly, Component
from openmdao.lib.datatypes.api import List, VarTree

from fusedwind.interface import implement_base
from fusedwind.turbine.geometry import read_blade_planform
from fusedwind.turbine.configurations import configure_bladestructure
from fusedwind.turbine.blade_structure import SplinedBladeStructure
from fusedwind.turbine.structure_vt import BladeStructureVT3D, BeamStructureVT
from fusedwind.turbine.turbine_vt import AeroelasticHAWTVT, configure_turbine

from fusedwind.turbine.aeroelastic_solver import AeroElasticSolverBase
from fusedwind.turbine.structural_props_solver import StructuralCSPropsSolver

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

        print ''
        print 'running aeroelastic analysis ...'


@implement_base(StructuralCSPropsSolver)
class CS2Dsolver(Component):

    cs2d = List(iotype='in')
    beam_structure = VarTree(BeamStructureVT(), iotype='out')

    def execute(self):

        print ''
        for i, cs in enumerate(self.cs2d):
            print 'processing cross section %i' % i

# --- 2 ---

top = Assembly()

configure_bladestructure(top, 'data/DTU10MW', planform_nC=6, structure_nC=5)

top.st_writer.filebase = 'st_test'

top.blade_length = 86.366

top.pf_splines.pfIn = read_blade_planform('data/DTU_10MW_RWT_blade_axis_prebend.dat')
top.blade_surface.chord_ni = 300

for f in ['data/ffaw3241.dat',
          'data/ffaw3301.dat',
          'data/ffaw3360.dat',
          'data/ffaw3480.dat',
          'data/tc72.dat',
          'data/cylinder.dat']:

    top.blade_surface.base_airfoils.append(np.loadtxt(f))

top.blade_surface.blend_var = np.array([0.241, 0.301, 0.36, 0.48, 0.72, 1.])

# spanwise distribution of planform spline DVs
top.pf_splines.Cx = [0, 0.2, 0.4, 0.6, 0.8, 1.]

# spanwise distribution of sptructural spline DVs
top.st_splines.Cx = [0, 0.2, 0.4, 0.75, 1.]

# spanwise distribution of points where
# cross-sectional structure vartrees will be created
top.st_splines.x = np.linspace(0, 1, 12)

# --- 3 ---

# add structural solver
top.add('st', CS2Dsolver())
top.driver.workflow.add('st')


# add aeroelastic solver
top.add('ae', AEsolver())
top.driver.workflow.add('ae')


# --- 4 ---

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

# --- 5 ---

# connect the parameterized structure vartrees to the 
# structural solver
top.connect('st_builder.cs2d', 'st.cs2d')

# connect the splined planform to the blade geometry vartree
# in the aeroelastic solver
top.connect('pf_splines.pfOut', 'ae.wt.blade1.geom')

# connect computed beam structure to input vartree in the
# aeroelastic solver
top.connect('st.beam_structure', 'ae.wt.blade1.beam_structure')

# --- 6 ---

# run it
top.run()

# --- 7 ---