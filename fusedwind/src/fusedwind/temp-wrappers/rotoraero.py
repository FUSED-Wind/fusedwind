#!/usr/bin/env python
# encoding: utf-8
"""
rotoraero.py

Created by Andrew Ning on 2013-03-20.
Copyright (c) NREL. All rights reserved.
"""

import numpy as np

from openmdao.main.datatypes.api import Float, Bool, Int, Slot
from fusedwind.vartrees.rotor import BEMRotorVT
from fusedwind.base.rotor import RotorAeroBase

from airfoilprep import Polar, Airfoil
from ccblade import BEMAirfoil, CCBlade


def _AFDataVTtoAFPrep(airfoilVT):
    """convert from list of AirfoilData variable trees to list of AirfoilPrep objects"""

    afprep_af = [0]*len(airfoilVT)
    for i, af in enumerate(airfoilVT):

        polars = [0]*len(af.polars)
        for j, p in enumerate(af.polars):
            polars[j] = Polar(af.Re, p.alpha, p.cl, p.cd)

        afprep_af[i] = Airfoil(polars)

    return afprep_af



class CCBladeWrapper(RotorAeroBase):
    """OpenMDAO wrapper for CCBlade"""

    bemrotor = Slot(BEMRotorVT)

    # optional inputs
    rho = Float(1.225)
    mu = Float(1.81206e-5)
    iterRe = Int(1)
    usecd = Bool(True)
    tiploss = Bool(True)
    hubloss = Bool(True)
    wakerotation = Bool(True)


    def execute(self):

        # rename for convenience
        r = self.bemrotor.r
        chord = self.bemrotor.chord
        theta = self.bemrotor.theta
        airfoil = self.bemrotor.airfoil
        Rhub = self.bemrotor.Rhub
        Rtip = self.bemrotor.Rtip
        B = self.bemrotor.B

        # convert from variable trees to AirfolPrep objects
        afprep_af = _AFDataVTtoAFPrep(airfoil)

        # create grid format that CCBlade uses
        bem_af = [0]*len(afprep_af)
        for idx, af in enumerate(afprep_af):
            alpha, Re, cl, cd = af.createDataGrid()
            bem_af[idx] = BEMAirfoil(alpha, Re, cl, cd)

        raero = CCBlade(r, chord, theta, bem_af, Rhub, Rtip, B, self.rho, self.mu,
                        self.iterRe, self.usecd, self.tiploss, self.hubloss, self.wakerotation)

        r, theta, Tp, Np = raero.distributedAeroLoads(self.Uinf, self.Omega, self.pitch)

        self.loads.r = r
        self.loads.theta = np.degrees(theta)
        self.loads.Tp = Tp
        self.loads.Np = Np



class WTPerfWrapper(RotorAeroBase):
    """OpenMDAO wrapper for WTPerf"""

    bemrotor = Slot(BEMRotorVT)

    # optional parameters
    preCone = Float(0.0)
    tilt = Float(0.0)
    yaw = Float(0.0)
    rho = Float(1.225)
    mu = Float(1.81206e-5)
    shearExp = Float(1.0/7)
    tipLoss = Bool(True)
    hubLoss = Bool(True)
    swirl = Bool(True)
    skewWake = Bool(True)



    def execute(self):

        # rename for convenience
        r = self.bemrotor.r
        chord = self.bemrotor.chord
        theta = self.bemrotor.theta
        airfoil = self.bemrotor.airfoil
        Rhub = self.bemrotor.Rhub
        Rtip = self.bemrotor.Rtip
        B = self.bemrotor.B

        # convert from variable trees to AirfolPrep objects
        afprep_af = _AFDataVTtoAFPrep(self.airfoil)

        # create files that WTPerf uses
        for af in afprep_af:
            af.writeToAerodynFile(some_filename)


