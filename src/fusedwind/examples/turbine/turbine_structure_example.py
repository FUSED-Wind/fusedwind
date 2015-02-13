
# --- 1 -----

import numpy as np

from openmdao.lib.datatypes.api import VarTree
from openmdao.main.api import Assembly, Component

from fusedwind.interface import implement_base
from fusedwind.turbine.geometry import read_blade_planform, redistribute_blade_planform
from fusedwind.turbine.configurations import configure_bladestructure, configure_bladesurface
from fusedwind.turbine.blade_structure import SplinedBladeStructure
from fusedwind.turbine.structure_vt import BladeStructureVT3D

top = Assembly()

configure_bladesurface(top, 'data/DTU_10MW_RWT_blade_axis_prebend.dat', planform_nC=6)
configure_bladestructure(top, 'data/DTU10MW', structure_nC=5)

top.st_writer.filebase = 'st_test'

top.blade_length = 86.366
top.span_ni = 30
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

# --- 2 -----

top.pf_splines.chord_C[3]-=0.008

top.run()

p=top.pf_splines.chord.P-top.pf_splines.chord.Pbase

import matplotlib
import matplotlib.pylab as plt

font = {'family' : 'normal',
        'weight' : 'normal',
        'size'   : 16 }  

matplotlib.rc('font', **font)
plt.rc('lines', linewidth=3)

plt.plot(top.pf_splines.pfIn.s, top.pf_splines.pfIn.chord, 'r-', label='Original')
plt.plot(top.pf_splines.pfOut.s, top.pf_splines.pfOut.chord, 'b-',label='New')
plt.plot(top.pf_splines.chord.Cx,top.pf_splines.chord.C, 'g--o',label='FFD CPs')
plt.plot(top.pf_splines.chord.x,p, 'b--',label='FFD spline')
plt.plt.legend(loc='best')
plt.title('Chord')
plt.xlabel('r/R [-]')
plt.ylabel('c/R [-]')
plt.savefig('chord_ffd_spline.eps')
plt.savefig('chord_ffd_spline.png')

# --- 3 -----

top.st_splines.r04uniaxT_C[2]+=0.01
plt.figure()
plt.plot(top.st_splines.st3dOut.x, top.st_splines.st3dOut.region04.uniax.thickness, 'r-', label='Original')
top.run()
plt.plot(top.st_splines.st3dOut.x, top.st_splines.st3dOut.region04.uniax.thickness, 'b-', label='New')

p=top.st_splines.r04uniaxT.P-top.st_splines.r04uniaxT.Pbase
plt.plot(top.st_splines.r04uniaxT.Cx,top.st_splines.r04uniaxT.C, 'g--o',label='FFD CPs')
plt.plot(top.st_splines.st3dOut.x, p, 'b--',label='FFD spline')
plt.plt.legend(loc='best')
plt.title('Spar cap uniax thickness')
plt.xlabel('r/R [-]')
plt.ylabel('Thickness [m]')
plt.savefig('turbine_structure_uniax_perturb.eps')
plt.savefig('turbine_structure_uniax_perturb.png')

# --- 4 -----
