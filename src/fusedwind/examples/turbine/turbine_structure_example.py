
import numpy as np

from openmdao.lib.datatypes.api import VarTree
from openmdao.main.api import Assembly, Component

from fusedwind.interface import implement_base
from fusedwind.turbine.geometry import read_blade_planform, redistribute_blade_planform
from fusedwind.turbine.configurations import configure_bladestructure
from fusedwind.turbine.blade_structure import SplinedBladeStructure
from fusedwind.turbine.structure_vt import BladeStructureVT3D

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

top.run()