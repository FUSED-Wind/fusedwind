# KLD: Cost model for FUSED_Wind - most basic structure

from numpy import ndarray, array, loadtxt, log, zeros, cos, arccos, sin, nonzero, argsort, NaN, mean, ones, vstack, linspace, exp, arctan, arange
from numpy import pi, sqrt, dot
from numpy.linalg.linalg import norm
from openmdao.lib.datatypes.api import VarTree, Float, Slot, Array, List, Int, Str, Dict
#from openmdao.lib.drivers.api import CaseIteratorDriver # KLD: temporary version issues
from openmdao.main.api import Driver, Run_Once
from openmdao.main.api import Component, Assembly, VariableTree, Container  # , IOInterface
from openmdao.lib.casehandlers.api import ListCaseIterator
from openmdao.main.interfaces import implements, ICaseRecorder, ICaseIterator
from openmdao.main.case import Case
from fused_plant import GenericAEPModel


# ------------------------------------------------------------
# Components and Assembly Base Classes
class GenericTurbineCapitalCostModel(Assembly):
    """
    Framework for a turbine capital cost model
    """

    # Outputs
    turbine_cost = Float(0.0, iotype='out', desc='Overall wind turbine capial costs including transportation costs')


class GenericBOSCostModel(Assembly):
    """
    Framework for a balance of station cost model
    """

    # Outputs
    bos_cost = Float(0.0, iotype='out', desc='Overall wind plant balance of station/system costs up to point of comissioning')


class GenericOPEXModel(Assembly):
    """
    Framework for a operations expenditures model that gives a single annual average operations expenditure over the plants lifetime
    """

    # Outputs
    avg_annual_opex = Float(0.0, iotype='out', desc='Average annual Operating Expenditures for a wind plant over its lifetime')


class ExtendedOPEXModel(GenericOPEXModel):
    """
    Framework for an enhanced operations expenditures model that gives a series of annual operating expenditures over the the plants lifetime
    """

    # Outputs
    annual_opex = Array([], iotype='out', desc='Array of annual Operating Expenditure estimates for each year of expected project operation')


class GenericDECOMEXModel(Assembly):
    """
    Framework for a decomissioning expenditures model for plant end of life
    """

    # Outputs
    decomex = Float(0.0, iotype='out', desc='General DECOMEX model produces Decomissioning Expenditures for a wind plant for the end of its life')


class GenericFinancialModel(Assembly):
    """
    Framework for a general financial model with upfront capital cost inputs and long-term averages for OPEX and net annual energy production
    """

    # Inputs
    turbine_cost = Float(0.0, iotype='in', desc = 'A Wind Turbine Capital Cost Model')
    bos_cost = Float(0.0, iotype='in', desc='A Wind Plant Balance of Station Cost Model')
    avg_annual_opex = Float(0.0, iotype='in', desc='A Wind Plant Operations Expenditures Model')
    net_aep = Float(1.0, iotype='in', desc='A Wind Plant Annual Energy Production Model', units='kW*h')

    #Outputs
    lcoe = Float(0.0, iotype='out', desc='Levelized cost of energy for the wind plant')

class EnhancedFinancialModel(GeneralFinancialModel):
    """
    Framework for an enhanced financial / cash flow model that takes into account the variability of OPEX and net annual energy production over time
    """

    # Inputs
    annual_opex = Array([], iotype='in', desc='Array of annual Operating Expenditure estimates for each year of expected project operation')
    annual_net_aep = Array([], iotype='in', desc='Array of net annual energy production which may vary over time')


# -----------------------------------------------------------------------
# Implementation assembly shells

#KLD: this assembly will probably not be in typical use cases
class CAPEXAnalysis(Assembly):

    # Outputs
    capex = Float(0.0, iotype='out', desc='Overall wind plant capital expenditures including turbine and balance of station costs') 
    
    def configure(self):
        super(CAPEXAnalysis, self).configure()

        # To be replaced by actual models        
        self.add('tcc',GenericTurbineCapitalCostModel())
        self.add('bos',GenericBOSCostModel())

        self.driver.workflow.add(['tcc','bos'])
    
    def execute(self):
        super(CAPEXAnalysis, self).execute()
        
        self.capex = tcc.turbine_cost + bos.bos_cost


# Main financial assembly
class GenericFinancialAnalysis(Assembly):

    #Inputs
    # KLD: doesnt work for replacement which are key when connections are being added to base model set
    '''tcc = Slot(GenericTurbineCapitalCostModel, iotype='in', desc = 'A Wind Turbine Capital Cost Model')
    bos = Slot(GenericBOSCostModel, iotype='in', desc='A Wind Plant Balance of Station Cost Model')
    opex = Slot(GenericOPEXModel, iotype='in', desc='A Wind Plant Operations Expenditures Model')
    aep = Slot(GenericAEPModel, iotype='in', desc='A Wind Plant Annual Energy Production Model')
    fin = Slot(GenericFinancialModel, iotype='in', desc='A Wind Plant Financial Analysis Model')'''

    def configure(self):
        super(GenericFinancialAnalysis, self).configure()

        # To be replaced by actual models
        self.add('tcc',GenericTurbineCapitalCostModel())
        self.add('bos',GenericBOSCostModel())
        self.add('opex',GenericOPEXModel())
        self.add('aep',GenericAEPModel())
        self.add('fin',GenericFinancialModel())

        self.driver.workflow.add(['tcc','bos','opex','aep','fin'])

        self.connect('tcc.turbine_cost','fin.turbine_cost')
        self.connect('bos.bos_cost','fin.bos_cost')
        self.connect('opex.avg_annual_opex','fin.avg_annual_opex')
        self.connect('aep.net_aep','fin.net_aep')

        self.create_passthrough('fin.lcoe')
        self.create_passthrough('aep.net_aep')
        self.create_passthrough('aep.gross_aep')
        self.create_passthrough('aep.capacity_factor')
        self.create_passthrough('opex.avg_annual_opex')
        self.create_passthrough('bos.bos_cost')
        self.create_passthrough('tcc.turbine_cost')
        
    def execute(self):
        # Nothing else to be done here
        super(GenericFinancialAnalysis, self).execute()