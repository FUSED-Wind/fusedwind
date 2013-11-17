# KLD: Cost model for FUSED_Wind - most basic structure

from openmdao.lib.datatypes.api import Float, Int, Array
from openmdao.main.api import Component, Assembly

from fusedwind.plant_flow.fused_plant_asym import GenericAEPModel
from fusedwind.plant_cost.fused_costs_asym import BaseBOSCostModel, BaseOPEXModel
from fusedwind.plant_cost.fused_tcc_asym import BaseTurbineCapitalCostModel

#########################################################################
# Financial models

# Financial Model

class BaseFinancialAggregator(Component):

    # Inputs
    turbine_cost = Float(iotype='in', desc = 'A Wind Turbine Capital Cost')
    turbine_number = Int(iotype = 'in', desc = 'number of turbines at plant')
    bos_cost = Float(iotype='in', desc='A Wind Plant Balance of Station Cost Model')
    avg_annual_opex = Float(iotype='in', desc='A Wind Plant Operations Expenditures Model')
    net_aep = Float(iotype='in', desc='A Wind Plant Annual Energy Production Model', units='kW*h')

    #Outputs
    coe = Float(iotype='out', desc='Levelized cost of energy for the wind plant')

class BaseFinancialModel(Assembly):
    """
    Framework for a general financial model with upfront capital cost inputs and long-term averages for OPEX and net annual energy production
    """
    
    def configure(self):
    
        super(BaseFinancialModel, self).configure()
        
        self.add('fin', BaseFinancialAggregator())
        
        self.driver.workflow.add(['fin'])
        
        self.create_passthrough('fin.turbine_cost')
        self.create_passthrough('fin.turbine_number')
        self.create_passthrough('fin.bos_cost')
        self.create_passthrough('fin.avg_annual_opex')
        self.create_passthrough('fin.net_aep')

        self.create_passthrough('fin.coe')

class ExtendedFinancialModel(BaseFinancialModel):
    """
    Framework for an enhanced financial / cash flow model that takes into account the variability of OPEX and net annual energy production over time
    """

    # Inputs
    annual_opex = Array(iotype='in', desc='Array of annual Operating Expenditure estimates for each year of expected project operation')
    annual_net_aep = Array(iotype='in', desc='Array of net annual energy production which may vary over time')



#########################################################################
# Implementation assembly shells

# Main financial assembly
class BaseFinancialAnalysis(Assembly):

    #Inputs
    # KLD: doesnt work for replacement which are key when connections are being added to base model set
    '''tcc = Slot(BaseTurbineCapitalCostModel, iotype='in', desc = 'A Wind Turbine Capital Cost Model')
    bos = Slot(BaseBOSCostModel, iotype='in', desc='A Wind Plant Balance of Station Cost Model')
    opex = Slot(BaseOPEXModel, iotype='in', desc='A Wind Plant Operations Expenditures Model')
    aep = Slot(BaseAEPModel, iotype='in', desc='A Wind Plant Annual Energy Production Model')
    fin = Slot(BaseFinancialModel, iotype='in', desc='A Wind Plant Financial Analysis Model')'''

    def configure(self):
        super(BaseFinancialAnalysis, self).configure()

        # To be replaced by actual models
        self.add('tcc',BaseTurbineCapitalCostModel())
        self.add('bos',BaseBOSCostModel())
        self.add('opex',BaseOPEXModel())
        self.add('aep',GenericAEPModel())
        self.add('fin',BaseFinancialModel())

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
        super(BaseFinancialAnalysis, self).execute()