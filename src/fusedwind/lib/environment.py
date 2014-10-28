#!/usr/bin/env python
# encoding: utf-8
"""
environment.py

Created by Andrew Ning on 2012-01-20.
Copyright (c) NREL. All rights reserved.
"""

import math
import numpy as np
from scipy.optimize import brentq
from openmdao.main.api import Component
from openmdao.main.datatypes.api import Float, Array

from utilities import hstack, vstack

# -----------------
#  Base Components
# -----------------


class WindBase(Component):
    """base component for wind speed/direction"""

    # TODO: if I put required=True here for Uref there is another bug

    # variables
    Uref = Float(iotype='in', units='m/s', desc='reference wind speed (usually at hub height)')
    zref = Float(iotype='in', units='m', desc='corresponding reference height')
    z = Array(iotype='in', units='m', desc='heights where wind speed should be computed')

    # parameters
    z0 = Float(0.0, iotype='in', units='m', desc='bottom of wind profile (height of ground/sea)')

    # out
    U = Array(iotype='out', units='m/s', desc='magnitude of wind speed at each z location')
    beta = Array(iotype='out', units='deg', desc='corresponding wind angles relative to inertial coordinate system')

    missing_deriv_policy = 'assume_zero'  # TODO: for now OpenMDAO issue


class WaveBase(Component):
    """base component for wave speed/direction"""

    # variables
    z = Array(iotype='in', units='m', desc='heights where wave speed should be computed')

    # out
    U = Array(iotype='out', units='m/s', desc='magnitude of wave speed at each z location')
    A = Array(iotype='out', units='m/s**2', desc='magnitude of wave acceleration at each z location')
    beta = Array(iotype='out', units='deg', desc='corresponding wave angles relative to inertial coordinate system')
    U0 = Float(iotype='out', units='m/s', desc='magnitude of wave speed at z=MSL')
    A0 = Float(iotype='out', units='m/s**2', desc='magnitude of wave acceleration at z=MSL')
    beta0 = Float(iotype='out', units='deg', desc='corresponding wave angles relative to inertial coordinate system at z=MSL')

    missing_deriv_policy = 'assume_zero'

    def execute(self):
        """default to no waves"""
        n = len(self.z)
        self.U = np.zeros(n)
        self.A = np.zeros(n)
        self.beta = np.zeros(n)
        self.U0 = 0.
        self.A0 = 0.
        self.beta0 = 0.



class SoilBase(Component):
    """base component for soil stiffness"""

    # out
    k = Array(iotype='out', units='N/m', required=True, desc='spring stiffness. rigid directions should use \
        ``float(''inf'')``. order: (x, theta_x, y, theta_y, z, theta_z)')

    missing_deriv_policy = 'assume_zero'  # TODO: for now OpenMDAO issue


# -----------------------
#  Subclassed Components
# -----------------------


class PowerWind(WindBase):
    """power-law profile wind.  any nodes must not cross z0, and if a node is at z0
    it must stay at that point.  otherwise gradients crossing the boundary will be wrong."""

    # parameters
    shearExp = Float(0.2, iotype='in', desc='shear exponent')
    betaWind = Float(0.0, iotype='in', units='deg', desc='wind angle relative to inertial coordinate system')

    missing_deriv_policy = 'assume_zero'


    def execute(self):

        # rename
        z = self.z
        zref = self.zref
        z0 = self.z0

        # velocity
        idx = z > z0
        n = len(z)
        self.U = np.zeros(n)
        self.U[idx] = self.Uref*((z[idx] - z0)/(zref - z0))**self.shearExp
        self.beta = self.betaWind*np.ones_like(z)

        # # add small cubic spline to allow continuity in gradient
        # k = 0.01  # fraction of profile with cubic spline
        # zsmall = z0 + k*(zref - z0)

        # self.spline = CubicSpline(x1=z0, x2=zsmall, f1=0.0, f2=Uref*k**shearExp,
        #     g1=0.0, g2=Uref*k**shearExp*shearExp/(zsmall - z0))

        # idx = np.logical_and(z > z0, z < zsmall)
        # self.U[idx] = self.spline.eval(z[idx])

        # self.zsmall = zsmall
        # self.k = k


    def list_deriv_vars(self):

        inputs = ('Uref', 'z', 'zref')
        outputs = ('U',)

        return inputs, outputs


    def provideJ(self):

        # rename
        z = self.z
        zref = self.zref
        z0 = self.z0
        shearExp = self.shearExp
        U = self.U
        Uref = self.Uref

        # gradients
        n = len(z)
        dU_dUref = np.zeros(n)
        dU_dz = np.zeros(n)
        dU_dzref = np.zeros(n)

        idx = z > z0
        dU_dUref[idx] = U[idx]/Uref
        dU_dz[idx] = U[idx]*shearExp/(z[idx] - z0)
        dU_dzref[idx] = -U[idx]*shearExp/(zref - z0)


        # # cubic spline region
        # idx = np.logical_and(z > z0, z < zsmall)

        # # d w.r.t z
        # dU_dz[idx] = self.spline.eval_deriv(z[idx])

        # # d w.r.t. Uref
        # df2_dUref = k**shearExp
        # dg2_dUref = k**shearExp*shearExp/(zsmall - z0)
        # dU_dUref[idx] = self.spline.eval_deriv_params(z[idx], 0.0, 0.0, 0.0, df2_dUref, 0.0, dg2_dUref)

        # # d w.r.t. zref
        # dx2_dzref = k
        # dg2_dzref = -Uref*k**shearExp*shearExp/k/(zref - z0)**2
        # dU_dzref[idx] = self.spline.eval_deriv_params(z[idx], 0.0, dx2_dzref, 0.0, 0.0, 0.0, dg2_dzref)

        J = hstack([dU_dUref, np.diag(dU_dz), dU_dzref])

        return J




class LogWind(WindBase):
    """logarithmic-profile wind"""

    # parameters
    z_roughness = Float(10.0, iotype='in', units='mm', desc='surface roughness length')
    betaWind = Float(0.0, iotype='in', units='deg', desc='wind angle relative to inertial coordinate system')

    missing_deriv_policy = 'assume_zero'

    def execute(self):

        # rename
        z = self.z
        zref = self.zref
        z0 = self.z0
        z_roughness = self.z_roughness/1e3  # convert to m

        # find velocity
        idx = [z - z0 > z_roughness]
        self.U = np.zeros_like(z)
        self.U[idx] = self.Uref*np.log((z[idx] - z0)/z_roughness) / math.log((zref - z0)/z_roughness)
        self.beta = self.betaWind*np.ones_like(z)


    def list_deriv_vars(self):

        inputs = ('Uref', 'z', 'zref')
        outputs = ('U',)

        return inputs, outputs


    def provideJ(self):

        # rename
        z = self.z
        zref = self.zref
        z0 = self.z0
        z_roughness = self.z_roughness/1e3
        Uref = self.Uref

        n = len(z)

        dU_dUref = np.zeros(n)
        dU_dz_diag = np.zeros(n)
        dU_dzref = np.zeros(n)

        idx = [z - z0 > z_roughness]
        lt = np.log((z[idx] - z0)/z_roughness)
        lb = math.log((zref - z0)/z_roughness)
        dU_dUref[idx] = lt/lb
        dU_dz_diag[idx] = Uref/lb / (z[idx] - z0)
        dU_dzref[idx] = -Uref*lt / math.log((zref - z0)/z_roughness)**2 / (zref - z0)

        J = hstack([dU_dUref, np.diag(dU_dz_diag), dU_dzref])

        return J



class LinearWaves(WaveBase):
    """linear (Airy) wave theory"""

    # variables
    Uc = Float(iotype='in', units='m/s', desc='mean current speed')

    # parameters
    z_surface = Float(iotype='in', units='m', desc='vertical location of water surface')
    hs = Float(iotype='in', units='m', desc='significant wave height (crest-to-trough)')
    T = Float(iotype='in', units='s', desc='period of waves')
    z_floor = Float(0.0, iotype='in', units='m', desc='vertical location of sea floor')
    g = Float(9.81, iotype='in', units='m/s**2', desc='acceleration of gravity')
    betaWave = Float(0.0, iotype='in', units='deg', desc='wave angle relative to inertial coordinate system')


    def execute(self):

        # water depth
        d = self.z_surface - self.z_floor

        # design wave height
        h = 1.1*self.hs

        # circular frequency
        omega = 2.0*math.pi/self.T

        # compute wave number from dispersion relationship
        k = brentq(lambda k: omega**2 - self.g*k*math.tanh(d*k), 0, 10*omega**2/self.g)

        # zero at surface
        z_rel = self.z - self.z_surface

        # maximum velocity
        self.U = h/2.0*omega*np.cosh(k*(z_rel + d))/math.sinh(k*d) + self.Uc
        self.U0 = h/2.0*omega*np.cosh(k*(0. + d))/math.sinh(k*d) + self.Uc

        # check heights
        self.U[np.logical_or(self.z < self.z_floor, self.z > self.z_surface)] = 0.

        # acceleration
        self.A  = self.U * omega
        self.A0 = self.U0 * omega
        # angles
        self.beta = self.betaWave*np.ones_like(self.z)
        self.beta0 =self.betaWave

        # derivatives
        dU_dz = h/2.0*omega*np.sinh(k*(z_rel + d))/math.sinh(k*d)*k
        dU_dUc = np.ones_like(self.z)
        idx = np.logical_or(self.z < self.z_floor, self.z > self.z_surface)
        dU_dz[idx] = 0.0
        dU_dUc[idx] = 0.0
        dA_dz = omega*dU_dz
        dA_dUc = omega*dU_dUc

        self.J = vstack([hstack([np.diag(dU_dz), dU_dUc]), hstack([np.diag(dA_dz), dA_dUc])])


    def list_deriv_vars(self):

        inputs = ('z', 'Uc')
        outputs = ('U', 'A', 'U0', 'A0')

        return inputs, outputs


    def provideJ(self):

        return self.J


class TowerSoil(SoilBase):
    """textbook soil stiffness method"""

    # variable
    r0 = Float(1.0, iotype='in', units='m', desc='radius of base of tower')
    depth = Float(1.0, iotype='in', units='m', desc='depth of foundation in the soil')

    # parameter
    G = Float(140e6, iotype='in', units='Pa', desc='shear modulus of soil')
    nu = Float(0.4, iotype='in', desc='Poisson''s ratio of soil')
    rigid = Array(iotype='in', dtype=np.bool, desc='directions that should be considered infinitely rigid\
        order is x, theta_x, y, theta_y, z, theta_z')

    missing_deriv_policy = 'assume_zero'


    def execute(self):

        G = self.G
        nu = self.nu
        h = self.depth
        r0 = self.r0

        # vertical
        eta = 1.0 + 0.6*(1.0-nu)*h/r0
        k_z = 4*G*r0*eta/(1.0-nu)

        # horizontal
        eta = 1.0 + 0.55*(2.0-nu)*h/r0
        k_x = 32.0*(1.0-nu)*G*r0*eta/(7.0-8.0*nu)

        # rocking
        eta = 1.0 + 1.2*(1.0-nu)*h/r0 + 0.2*(2.0-nu)*(h/r0)**3
        k_thetax = 8.0*G*r0**3*eta/(3.0*(1.0-nu))

        # torsional
        k_phi = 16.0*G*r0**3/3.0

        self.k = np.array([k_x, k_thetax, k_x, k_thetax, k_z, k_phi])
        self.k[self.rigid] = float('inf')


    def list_deriv_vars(self):

        inputs = ('r0', 'depth')
        outputs = ('k',)

        return inputs, outputs


    def provideJ(self):

        G = self.G
        nu = self.nu
        h = self.depth
        r0 = self.r0

        # vertical
        eta = 1.0 + 0.6*(1.0-nu)*h/r0
        deta_dr0 = -0.6*(1.0-nu)*h/r0**2
        dkz_dr0 = 4*G/(1.0-nu)*(eta + r0*deta_dr0)

        deta_dh = 0.6*(1.0-nu)/r0
        dkz_dh = 4*G*r0/(1.0-nu)*deta_dh

        # horizontal
        eta = 1.0 + 0.55*(2.0-nu)*h/r0
        deta_dr0 = -0.55*(2.0-nu)*h/r0**2
        dkx_dr0 = 32.0*(1.0-nu)*G/(7.0-8.0*nu)*(eta + r0*deta_dr0)

        deta_dh = 0.55*(2.0-nu)/r0
        dkx_dh = 32.0*(1.0-nu)*G*r0/(7.0-8.0*nu)*deta_dh

        # rocking
        eta = 1.0 + 1.2*(1.0-nu)*h/r0 + 0.2*(2.0-nu)*(h/r0)**3
        deta_dr0 = -1.2*(1.0-nu)*h/r0**2 - 3*0.2*(2.0-nu)*(h/r0)**3/r0
        dkthetax_dr0 = 8.0*G/(3.0*(1.0-nu))*(3*r0**2*eta + r0**3*deta_dr0)

        deta_dh = 1.2*(1.0-nu)/r0 + 3*0.2*(2.0-nu)*(1.0/r0)**3*h**2
        dkthetax_dh = 8.0*G*r0**3/(3.0*(1.0-nu))*deta_dh

        # torsional
        dkphi_dr0 = 16.0*G*3*r0**2/3.0
        dkphi_dh = 0.0

        dk_dr0 = np.array([dkx_dr0, dkthetax_dr0, dkx_dr0, dkthetax_dr0, dkz_dr0, dkphi_dr0])
        dk_dr0[self.rigid] = 0.0
        dk_dh = np.array([dkx_dh, dkthetax_dh, dkx_dh, dkthetax_dh, dkz_dh, dkphi_dh])
        dk_dh[self.rigid] = 0.0

        J = hstack((dk_dr0, dk_dh))

        return J






if __name__ == '__main__':
    p = LogWind()
    p.Uref = 10.0
    p.zref = 100.0
    p.z0 = 1.0
    p.z = np.linspace(1.0, 5, 20)
    p.shearExp = 0.2
    p.betaWind = 0.0

    p.run()

    import matplotlib.pyplot as plt
    plt.plot(p.z, p.U)
    plt.show()
