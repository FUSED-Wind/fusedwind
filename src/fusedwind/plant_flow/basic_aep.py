"""
aep_csm_component.py

Created by NWTC Systems Engineering Sub-Task on 2012-08-01.
Copyright (c) NREL. All rights reserved.
"""

import numpy as np

from openmdao.main.api import Component, Assembly, set_as_top, VariableTree
from openmdao.main.datatypes.api import Int, Bool, Float, Array, VarTree

from fusedwind.lib.utilities import hstack, vstack

from fusedwind.plant_flow.asym import BaseAEPModel, BaseAEPModel_NoFlow
from fusedwind.plant_flow.comp import BaseAEPAggregator, BaseAEPAggregator_NoFlow, CDFBase
from fusedwind.interface import implement_base

###################################################
# AEP where single turbine AEP is input

@implement_base(BaseAEPModel_NoFlow)
class aep_assembly(Assembly):
    """ Basic assembly for aep estimation for an entire wind plant based on the AEP input from one turbine."""

    # variables
    AEP_one_turbine = Float(iotype='in', units='kW*h')

    # parameters
    array_losses = Float(0.059, iotype='in', desc='energy losses due to turbine interactions - across entire plant')
    other_losses = Float(0.0, iotype='in', desc='energy losses due to blade soiling, electrical, etc')
    availability = Float(0.94, iotype='in', desc='average annual availbility of wind turbines at plant')
    turbine_number = Int(100, iotype='in', desc='total number of wind turbines at the plant')
    machine_rating = Float(5000.0, iotype='in', desc='machine rating of turbine')

    # outputs
    gross_aep = Float(iotype='out', desc='Gross Annual Energy Production before availability and loss impacts', units='kW*h')
    net_aep = Float(iotype='out', desc='Net Annual Energy Production after availability and loss impacts', units='kW*h')
    capacity_factor = Float(iotype='out', desc='plant capacity factor')

    def configure(self):

        super(aep_assembly, self).configure()

        self.add('aep', BasicAEP())

        self.driver.workflow.add(['aep'])

        #inputs
        self.connect('AEP_one_turbine', 'aep.AEP_one_turbine')
        self.connect('array_losses', 'aep.array_losses')
        self.connect('other_losses', 'aep.other_losses')
        self.connect('availability', 'aep.availability')
        self.connect('turbine_number', 'aep.turbine_number')

        # outputs
        self.connect('aep.gross_aep', 'gross_aep')
        self.connect('aep.net_aep', 'net_aep')
        self.connect('aep.capacity_factor','capacity_factor')

@implement_base(BaseAEPAggregator_NoFlow)
class BasicAEP(Component):
    """ Basic component for aep estimation for an entire wind plant based on the AEP input from one turbine."""

    # in
    AEP_one_turbine = Float(iotype='in', units='kW*h')

    # parameters
    array_losses = Float(0.059, iotype='in', desc='energy losses due to turbine interactions - across entire plant')
    other_losses = Float(0.0, iotype='in', desc='energy losses due to blade soiling, electrical, etc')
    availability = Float(0.94, iotype='in', desc='average annual availbility of wind turbines at plant')
    turbine_number = Int(100, iotype='in', desc='total number of wind turbines at the plant')
    machine_rating = Float(5000.0, iotype='in', desc='machine rating of turbine')

    # outputs
    gross_aep = Float(iotype='out', desc='Gross Annual Energy Production before availability and loss impacts', units='kW*h')
    net_aep = Float(iotype='out', desc='Net Annual Energy Production after availability and loss impacts', units='kW*h')
    capacity_factor = Float(iotype='out', desc='plant capacity factor')
    
    def __init__(self):
        
        Component.__init__(self)
        
        self.missing_deriv_policy = 'assume_zero'

    def execute(self):

        self.gross_aep = self.turbine_number * self.AEP_one_turbine
        self.net_aep = self.availability * (1-self.array_losses) * (1-self.other_losses) * self.gross_aep
        self.capacity_factor = self.AEP_one_turbine / (8760. * self.machine_rating)

    def list_deriv_vars(self):

        inputs = ('AEP_one_turbine',)
        outputs = ('gross_aep', 'net_aep')

        return inputs, outputs

    def provideJ(self):

        J = np.array([[self.turbine_number],  [self.availability * (1-self.array_losses) * (1-self.other_losses) * self.turbine_number]])

        return J

################################
# AEP where power curve and environmental conditions are input


@implement_base(CDFBase)
class WeibullCDF(Component):
    """Weibull cumulative distribution function"""

    # Inputs
    A = Float(iotype='in', desc='scale factor')
    k = Float(iotype='in', desc='shape or form factor')
    x = Array(iotype='in', desc='input curve')

    # Outputs
    F = Array(iotype='out', desc='probabilities out')

    def __init__(self):

        super(WeibullCDF,self).__init__()

        #controls what happens if derivatives are missing
        self.missing_deriv_policy = 'assume_zero'

    def execute(self):

        self.F = 1.0 - np.exp(-(self.x/self.A)**self.k)

        self.d_F_d_x = np.diag(- np.exp(-(self.x/self.A)**self.k) * (1./self.A) * (-self.k * ((self.x/self.A)**(self.k-1.0))))
        self.d_F_d_A = - np.exp(-(self.x/self.A)**self.k) * (1./self.x) * (self.k * ((self.A/self.x)**(-self.k-1.0)))
        self.d_F_d_k = - np.exp(-(self.x/self.A)**self.k) * -(self.x/self.A)**self.k * np.log(self.x/self.A)

    def list_deriv_vars(self):

        inputs = ['x', 'A', 'k']
        outputs = ['F']

        return inputs, outputs


    def provideJ(self):

        self.J = hstack((self.d_F_d_x, self.d_F_d_A, self.d_F_d_k))

        return self.J


class RayleighCDF(CDFBase):
    """Rayleigh cumulative distribution function"""

    # Inputs
    xbar = Float(iotype='in', desc='mean value of distribution')
    x = Array(iotype='in', desc='input curve')

    # Outputs
    F = Array(iotype='out', desc='probabilities out')

    def __init__(self):

        super(RayleighCDF,self).__init__()

        #controls what happens if derivatives are missing
        self.missing_deriv_policy = 'assume_zero'

    def execute(self):

        self.F = 1.0 - np.exp(-np.pi/4.0*(self.x/self.xbar)**2)

        self.d_F_d_x = np.diag(- np.exp(-np.pi/4.0*(self.x/self.xbar)**2) * ((-np.pi/2.0)*(self.x/self.xbar)) * (1.0 / self.xbar))
        self.d_F_d_xbar = - np.exp(-np.pi/4.0*(self.x/self.xbar)**2) * ((np.pi/2.0)*(self.xbar/self.x)**(-3)) * (1.0 / self.x)

    def list_deriv_vars(self):

        inputs = ['x', 'xbar']
        outputs = ['F']

        return inputs, outputs

    def provideJ(self):

        self.J = hstack((self.d_F_d_x, self.d_F_d_xbar))

        return self.J

@implement_base(BaseAEPModel_NoFlow)
class aep_weibull_assembly(Assembly):
    """ Basic assembly for aep estimation for an entire wind plant with the wind resource and single turbine power curve as inputs."""

    # variables
    A = Float(iotype='in', desc='scale factor')
    k = Float(iotype='in', desc='shape or form factor')
    wind_curve = Array(iotype='in', units='m/s', desc='wind curve')
    power_curve = Array(iotype='in', units='W', desc='power curve (power)')
    machine_rating = Float(units='kW', iotype='in', desc='machine power rating')

    # parameters
    array_losses = Float(0.059, iotype='in', desc = 'energy losses due to turbine interactions - across entire plant')
    other_losses = Float(0.0, iotype='in', desc = 'energy losses due to blade soiling, electrical, etc')
    availability = Float(0.94, iotype='in', desc = 'average annual availbility of wind turbines at plant')
    turbine_number = Int(100, iotype='in', desc = 'total number of wind turbines at the plant')

    # outputs
    gross_aep = Float(iotype='out', desc='Gross Annual Energy Production before availability and loss impacts', units='kW*h')
    net_aep = Float(iotype='out', desc='Net Annual Energy Production after availability and loss impacts', units='kW*h')
    capacity_factor = Float(iotype='out', desc='plant capacity factor')

    def configure(self):

        super(aep_weibull_assembly, self).configure()

        self.add('aep', aep_component())
        self.add('cdf', WeibullCDF())

        self.driver.workflow.add(['aep', 'cdf'])

        #inputs
        self.connect('power_curve', 'aep.power_curve')
        self.connect('array_losses', 'aep.array_losses')
        self.connect('other_losses', 'aep.other_losses')
        self.connect('availability', 'aep.availability')
        self.connect('turbine_number', 'aep.turbine_number')
        self.connect('machine_rating','aep.machine_rating')
        self.connect('A','cdf.A')
        self.connect('k','cdf.k')
        self.connect('wind_curve','cdf.x')

        # connections
        self.connect('cdf.F', 'aep.CDF_V')

        # outputs
        self.connect('aep.gross_aep', 'gross_aep')
        self.connect('aep.net_aep', 'net_aep')
        self.connect('aep.capacity_factor','capacity_factor')

@implement_base(BaseAEPAggregator_NoFlow)
class aep_component(Component):
    """ Basic component for aep estimation for an entire wind plant with the wind resource and single turbine power curve as inputs."""

    # variables
    CDF_V = Array(iotype='in')
    power_curve = Array(iotype='in', units='W', desc='power curve (power)')
    machine_rating = Float(units='kW', iotype='in', desc='machine power rating')

    # parameters
    array_losses = Float(0.059, iotype='in', desc='energy losses due to turbine interactions - across entire plant')
    other_losses = Float(0.0, iotype='in', desc='energy losses due to blade soiling, electrical, etc')
    availability = Float(0.94, iotype='in', desc='average annual availbility of wind turbines at plant')
    turbine_number = Int(100, iotype='in', desc='total number of wind turbines at the plant')

    # outputs
    gross_aep = Float(iotype='out', desc='Gross Annual Energy Production before availability and loss impacts', unit='kWh')
    net_aep = Float(iotype='out', desc='Net Annual Energy Production after availability and loss impacts', unit='kWh')
    capacity_factor = Float(iotype='out', desc='plant capacity factor')

    def __init__(self):

        Component.__init__(self)

        #controls what happens if derivatives are missing
        self.missing_deriv_policy = 'assume_zero'

    def execute(self):

        self.gross_aep = self.turbine_number * np.trapz(self.power_curve, self.CDF_V)*365.0*24.0  # in kWh
        self.net_aep = self.availability * (1-self.array_losses) * (1-self.other_losses) * self.gross_aep
        self.capacity_factor = self.net_aep / (8760. * self.machine_rating * self.turbine_number)

    def list_deriv_vars(self):

        inputs = ['CDF_V', 'power_curve']
        outputs = ['gross_aep', 'net_aep']

        return inputs, outputs

    def provideJ(self):

        P = self.power_curve
        CDF = self.CDF_V
        factor = self.availability * (1-self.other_losses)*(1-self.array_losses)*365.0*24.0 * self.turbine_number

        n = len(P)
        dAEP_dP = np.gradient(CDF)
        dAEP_dP[0] /= 2
        dAEP_dP[-1] /= 2
        d_gross_d_p = dAEP_dP * 365.0 * 24.0 * self.turbine_number
        d_net_d_p = dAEP_dP * factor

        dAEP_dCDF = -np.gradient(P)
        dAEP_dCDF[0] = -0.5*(P[0] + P[1])
        dAEP_dCDF[-1] = 0.5*(P[-1] + P[-2])
        d_gross_d_cdf = dAEP_dCDF * 365.0 * 24.0 * self.turbine_number
        d_net_d_cdf = dAEP_dCDF * factor

        #loss_factor = self.availability * (1-self.array_losses) * (1-self.other_losses)

        #dAEP_dlossFactor = np.array([self.net_aep/loss_factor])

        self.J = np.zeros((2, 2*n))
        self.J[0, 0:n] = d_gross_d_cdf
        self.J[0, n:2*n] = d_gross_d_p
        self.J[1, 0:n] = d_net_d_cdf
        self.J[1, n:2*n] = d_net_d_p
        #self.J[0, 2*n] = dAEP_dlossFactor

        return self.J

def example():

    aeptest = aep_weibull_assembly()

    #print aeptest.aep.machine_rating

    aeptest.wind_curve = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, \
                           11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0, 21.0, 22.0, 23.0, 24.0, 25.0, 26.0])
    aeptest.power_curve = np.array([0.0, 0.0, 0.0, 187.0, 350.0, 658.30, 1087.4, 1658.3, 2391.5, 3307.0, 4415.70, \
                          5000.0, 5000.0, 5000.0, 5000.0, 5000.0, 5000.0, 5000.0, 5000.0, 5000.0, 5000.0, 5000.0, 5000.0, \
                          5000.0, 5000.0, 0.0])
    aeptest.A = 8.35
    aeptest.k = 2.15
    aeptest.array_losses = 0.059
    aeptest.other_losses = 0.0
    aeptest.availability = 0.94
    aeptest.turbine_number = 100

    aeptest.run()

    print "Annual energy production for an offshore wind plant with 100 NREL 5 MW reference turbines."
    print "AEP gross output (before losses): {0:.1f} kWh".format(aeptest.gross_aep)
    print "AEP net output (after losses): {0:.1f} kWh".format(aeptest.net_aep)

if __name__=="__main__":

    example()
