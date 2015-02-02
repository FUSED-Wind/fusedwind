
# --- 1 -----
import os
import pkg_resources
import numpy as np
import matplotlib.pylab as plt

from fusedwind.turbine.geometry_vt import AirfoilShape

def redistribute_airfoil_example():

    af = AirfoilShape(np.loadtxt('data/ffaw3301.dat'))

    print 'number of points, ni: ', af.ni
    print 'Airfoil leading edge (x, y): ', af.LE
    print 'Airfoil leading edge curve fraction (s): ', af.sLE

    plt.figure()
    plt.plot(af.points[:, 0], af.points[:, 1], '-x', label='original')

    # redistribute 200 points along the surface
    # and let the LE cell size be determined based on curvature
    aff = af.redistribute(200, dLE=True)

    plt.plot(aff.points[:, 0], aff.points[:, 1], '-<', label='redistributed')

    plt.plot(aff.LE[0], aff.LE[1], 'o', label='LE')

    plt.legend(loc='best')
    plt.axis('equal')
    plt.show()


# --- 2 -----

import os
from fusedwind.turbine.configurations import configure_bladesurface
from fusedwind.turbine.geometry import read_blade_planform
from openmdao.main.api import Assembly

def lofted_blade_shape_example():

    top = Assembly()

    configure_bladesurface(top, 'data/DTU_10MW_RWT_blade_axis_prebend.dat', planform_nC=6)

    # load the planform file
    top.blade_length = 86.366
    top.span_ni = 50

    print 'planform variables: ', top.pf_splines.pfOut.list_vars()

    b = top.blade_surface

    # distribute 200 points evenly along the airfoil sections
    b.chord_ni = 200

    # load the airfoil shapes defining the blade
    for f in ['data/ffaw3241.dat',
              'data/ffaw3301.dat',
              'data/ffaw3360.dat',
              'data/ffaw3480.dat' ,
              'data/tc72.dat' ,
              'data/cylinder.dat']:

        b.base_airfoils.append(np.loadtxt(f))

    b.blend_var = np.array([0.241, 0.301, 0.36, 0.48, 0.72, 1.])

    top.run()

    pf = top.pf_splines.pfOut

    plt.figure()
    plt.title('chord')
    plt.plot(pf.s, pf.chord)
    plt.savefig('chord.eps')
    plt.figure()
    plt.title('twist')
    plt.plot(pf.s, pf.rot_z)
    plt.savefig('twist.eps')
    plt.figure()
    plt.title('relative thickness')
    plt.plot(pf.s, pf.rthick)
    plt.savefig('rthick.eps')
    plt.figure()
    plt.title('pitch axis aft leading edge')
    plt.plot(pf.s, pf.p_le)
    plt.savefig('p_le.eps')

    plt.figure()
    plt.axis('equal')
    for i in range(b.span_ni):
        plt.plot(b.surfout.surface[:, i, 0], b.surfout.surface[:, i, 1])
    plt.savefig('lofted_blade.eps')
    plt.savefig('lofted_blade.png')

    return top


# --- 3 -----
