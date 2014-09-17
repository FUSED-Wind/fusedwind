#!/usr/bin/env python
# encoding: utf-8
"""
airfoilprep-mdo.py

Created by Andrew Ning on 2013-03-12.
Copyright (c) NREL. All rights reserved.
"""

from enthought.traits.api import on_trait_change
from openmdao.main.api import Component
from openmdao.main.datatypes.api import Float, Array, Slot

from fusedwind.vartrees.airfoil import PolarDataVT, AirfoilDataVT
from fusedwind.base.airfoil import BasicAirfoilBase, ModifyAirfoilBase, \
    ReadAirfoilBase, WriteAirfoilBase
from airfoilprep import Polar, Airfoil


def _convertToAirfoil(afData):
    """convert fusedwind.basic_airfoil.AirfoilDataVT to airfoilprep.Airfoil"""

    n = len(afData.Re)

    polars = [0]*n
    for i in range(n):
        pData = afData.polars[i]
        polars[i] = Polar(afData.Re[i], pData.alpha, pData.cl, pData.cd)

    return Airfoil(polars)


def _convertToAFData(af):
    """convert airfoilprep.Airfoil to fusedwind.basic_airfoil.AirfoilDataVT"""

    afData = AirfoilDataVT()
    afData.Re = [p.Re for p in af.polars]
    n = len(afData.Re)

    polars = [0]*n
    for i in range(n):
        polars[i] = PolarDataVT()
        polars[i].alpha = af.polars[i].alpha
        polars[i].cl = af.polars[i].cl
        polars[i].cd = af.polars[i].cd

    afData.polars = polars

    return afData


class EvalTabulatedAirfoilComponent(BasicAirfoilBase):
    """Uses tabulated data"""

    afData = Slot(AirfoilDataVT, iotype='in')

    # TODO: get rid of once OpenMDAO updates
    def __init__(self):
        super(EvalTabulatedAirfoilComponent, self).__init__()
        self.afData = AirfoilDataVT()


    @on_trait_change('afData')
    def _reinitializeAF(self, object, name, new):
        print 'afData changed in EvalTabulatedAirfoilComponent'

        # rename for convenience
        afData = new

        # check input airfoil data (may need additional checks)
        if len(afData.Re) == 0:
            self.valid_data = False
            return

        self.valid_data = True
        self.af = _convertToAirfoil(afData)



    def execute(self):
        print 'evaluated tabulated data'

        # TODO: error handling
        if not self.valid_data:
            print 'need to provide valid airfoil data first'
            return

        self.cl, self.cd, self.cm = self.af.evaluate(self.alpha, self.Re)



class BlendAirfoilComponent(Component):
    """blend two airfoil's aerodynamic data"""

    afData1 = Slot(AirfoilDataVT, iotype='in')
    afData2 = Slot(AirfoilDataVT, iotype='in')
    weight = Float(iotype='in')

    afOut = Slot(AirfoilDataVT, iotype='in')

    # TODO: remove shortly
    def __init__(self):
        super(BlendAirfoilComponent, self).__init__()
        self.afData1 = AirfoilDataVT()
        self.afData2 = AirfoilDataVT()
        self.afOut = AirfoilDataVT()

    def execute(self):
        print 'blending af1 with af2 using specified weighting'

        af1 = _convertToAirfoil(self.afData1)
        af2 = _convertToAirfoil(self.afData2)
        afblend = af1.blend(af2, self.weight)

        self.afOut = _convertToAFData(afblend)



class EggersAirfoilComponent(ModifyAirfoilBase):
    """a 3D correction method"""

    r_over_R = Float(iotype='in')
    chord_over_r = Float(iotype='in')
    tsr = Float(iotype='in')
    alpha_max_corr = Float(30, iotype='in')
    alpha_linear_min = Float(-5, iotype='in')
    alpha_linear_max = Float(5, iotype='in')

    def execute(self):
        print 'applying Eggers corrections'

        af = _convertToAirfoil(self.afIn)

        af = af.correction3D(self.r_over_R, self.chord_over_r, self.tsr, self.alpha_max_corr,
                             self.alpha_linear_min, self.alpha_linear_max)

        self.afOut = _convertToAFData(af)



class ViternaAirfoilComponent(ModifyAirfoilBase):
    """extrapolate to high alpha"""

    cdmax = Float(iotype='in')
    AR = Float(iotype='in')
    cdmin = Float(0.001, iotype='in')

    def execute(self):
        print 'Viterna extension'

        af = _convertToAirfoil(self.afIn)

        af = af.extrapolate(self.cdmax, self.AR, self.cdmin)

        self.afOut = _convertToAFData(af)


class CommonAnglesOfAttackComponent(ModifyAirfoilBase):
    """interpolate all Polars to a common set of angles of attack"""

    alpha = Array(iotype='in', units='deg',
                  desc='optional, if provided interpolates to this angle of attack, \
                  otherwise uses union of all angles of attack defined in Polars')

    def execute(self):
        'interpolating to common set of angles of attack'

        af = _convertToAirfoil(self.afIn)

        if len(self.alpha) == 0:
            alpha = None
        else:
            alpha = self.alpha
        af = af.interpToCommonAlpha(alpha)

        self.afOut = _convertToAFData(af)


class ReadAeroDynFileComponent(ReadAirfoilBase):

    def execute(self):
        print 'reading file', self.fileIn, 'and initializing airfoil data'

        af = Airfoil.initFromAerodynFile(self.fileIn)
        self.afOut = _convertToAFData(af)



class WriteAeroDynFileComponent(WriteAirfoilBase):

    def execute(self):
        print 'writing af data to AeroDyn file:', self.fileOut

        af = _convertToAirfoil(self.afIn)
        af.writeToAerodynFile(self.fileOut)



if __name__ == '__main__':

    import numpy as np
    from fusedwind.assemblies.airfoil import AirfoilPreprocessingAssembly

    # -------- airfoil preprocessing assembly --------
    # setup
    afPrep = AirfoilPreprocessingAssembly()

    # use specific read/write methods
    read = ReadAeroDynFileComponent()

    write = WriteAeroDynFileComponent()
    write.useCommonSetOfAnglesOfAttack = True

    afPrep.replace('read', read)
    afPrep.replace('write', write)

    # add 3D correction
    correct3D = EggersAirfoilComponent()
    correct3D.r_over_R = 0.5
    correct3D.chord_over_r = 0.1
    correct3D.tsr = 5.0
    afPrep.replace('mod1', correct3D)

    # add extraplation
    extrapolate = ViternaAirfoilComponent()
    extrapolate.AR = 15.0
    afPrep.replace('mod2', extrapolate)

    # add interp to common set of angles of attack
    commonAlpha = CommonAnglesOfAttackComponent()
    # commonAlpha.alpha = np.linspace(-180, 180, 361)
    # afPrep.replace('mod3', commonAlpha)

    # read/write files
    afPrep.fileIn = 'DU21_A17.dat'
    afPrep.fileOut = 'out.dat'
    afPrep.run()




    # -------- spline component --------
    print ''
    readin = ReadAeroDynFileComponent()
    readin.fileIn = 'out.dat'
    readin.run()

    afSpline = EvalTabulatedAirfoilComponent()
    afSpline.afData = readin.afOut

    alpha = 1.5
    Re = 1e6
    cl, cd, cm = afSpline.forces(alpha, Re)
    print cl, cd, cm

    alpha = 2.5
    Re = 2e6
    cl, cd, cm = afSpline.forces(alpha, Re)
    print cl, cd, cm




