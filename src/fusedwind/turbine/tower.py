#!/usr/bin/env python
# encoding: utf-8

from openmdao.main.api import Component
from openmdao.lib.datatypes.api import Float, Array, Bool
from fusedwind.interface import base


@base
class TowerFromCSProps(Component):

    # cross-sectional data along tower.
    z = Array(iotype='in', units='m', desc='location along tower.  start at bottom at go to top.')
    Az = Array(iotype='in', units='m**2', desc='cross-sectional area')
    Asx = Array(iotype='in', units='m**2', desc='x shear area')
    Asy = Array(iotype='in', units='m**2', desc='y shear area')
    Jz = Array(iotype='in', units='m**4', desc='polar moment of inertia')
    Ixx = Array(iotype='in', units='m**4', desc='area moment of inertia about x-axis')
    Iyy = Array(iotype='in', units='m**4', desc='area moment of inertia about y-axis')

    # material properties along tower.
    E = Array(iotype='in', units='N/m**2', desc='modulus of elasticity')
    G = Array(iotype='in', units='N/m**2', desc='shear modulus')
    rho = Array(iotype='in', units='kg/m**3', desc='material density')
    sigma_y = Array(iotype='in', units='N/m**2', desc='yield stress')

    # locations where stress should be evaluated
    theta_stress = Array(iotype='in', units='deg', desc='location along azimuth where stress should be evaluated.  0 corresponds to +x axis.  follows unit circle direction and c.s.')

    # spring reaction data.  Use float('inf') for rigid constraints.
    kidx = Array(iotype='in', desc='indices of z where external stiffness reactions should be applied.')
    kx = Array(iotype='in', units='m', desc='spring stiffness in x-direction')
    ky = Array(iotype='in', units='m', desc='spring stiffness in y-direction')
    kz = Array(iotype='in', units='m', desc='spring stiffness in z-direction')
    ktx = Array(iotype='in', units='m', desc='spring stiffness in theta_x-rotation')
    kty = Array(iotype='in', units='m', desc='spring stiffness in theta_y-rotation')
    ktz = Array(iotype='in', units='m', desc='spring stiffness in theta_z-rotation')

    # extra mass
    midx = Array(iotype='in', desc='indices where added mass should be applied.')
    m = Array(iotype='in', units='kg', desc='added mass')
    mIxx = Array(iotype='in', units='kg*m**2', desc='x mass moment of inertia about some point p')
    mIyy = Array(iotype='in', units='kg*m**2', desc='y mass moment of inertia about some point p')
    mIzz = Array(iotype='in', units='kg*m**2', desc='z mass moment of inertia about some point p')
    mIxy = Array(iotype='in', units='kg*m**2', desc='xy mass moment of inertia about some point p')
    mIxz = Array(iotype='in', units='kg*m**2', desc='xz mass moment of inertia about some point p')
    mIyz = Array(iotype='in', units='kg*m**2', desc='yz mass moment of inertia about some point p')
    mrhox = Array(iotype='in', units='m', desc='x-location of p relative to node')
    mrhoy = Array(iotype='in', units='m', desc='y-location of p relative to node')
    mrhoz = Array(iotype='in', units='m', desc='z-location of p relative to node')
    addGravityLoadForExtraMass = Bool(True, iotype='in', desc='add gravitational load')

    # gravitational load
    g = Float(9.81, iotype='in', units='m/s**2', desc='acceleration of gravity (magnitude)')

    # point loads (if addGravityLoadForExtraMass=True be sure not to double count by adding those force here also)
    plidx = Array(iotype='in', desc='indices where point loads should be applied.')
    Fx = Array(iotype='in', units='N', desc='point force in x-direction')
    Fy = Array(iotype='in', units='N', desc='point force in y-direction')
    Fz = Array(iotype='in', units='N', desc='point force in z-direction')
    Mxx = Array(iotype='in', units='N*m', desc='point moment about x-axis')
    Myy = Array(iotype='in', units='N*m', desc='point moment about y-axis')
    Mzz = Array(iotype='in', units='N*m', desc='point moment about z-axis')

    # distributed loads
    Px = Array(iotype='in', units='N/m', desc='force per unit length in x-direction')
    Py = Array(iotype='in', units='N/m', desc='force per unit length in y-direction')
    Pz = Array(iotype='in', units='N/m', desc='force per unit length in z-direction')
    q = Array(iotype='in', units='N/m**2', desc='dynamic pressure')

    # safety factors
    gamma_f = Float(1.35, iotype='in', desc='safety factor on loads')
    gamma_m = Float(1.1, iotype='in', desc='safety factor on materials')
    gamma_n = Float(1.0, iotype='in', desc='safety factor on consequence of failure')

    # outputs
    mass = Float(iotype='out')
    f1 = Float(iotype='out', units='Hz', desc='First natural frequency')
    f2 = Float(iotype='out', units='Hz', desc='Second natural frequency')
    top_deflection = Float(iotype='out', units='m', desc='Deflection of tower top in yaw-aligned +x direction')
    stress = Array(iotype='out', units='N/m**2', desc='Von Mises stress utilization along tower at specified locations.  incudes safety factor.')
