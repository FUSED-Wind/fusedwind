# KLD: _cost model for FUSED_Wind - most basic structure

from openmdao.lib.datatypes.api import Float, Int, Array
from openmdao.main.api import Component, Assembly

from fusedwind.plant_flow.fused_plant_asym import GenericAEPModel
from fusedwind.plant_cost.fused_costs_asym import BaseBOSCostModel, BaseOPEXModel, ExtendedBOSCostModel, ExtendedOPEXModel
from fusedwind.plant_cost.fused_tcc_asym import BaseTurbineCapitalCostModel, FullTurbineCapitalCostModel

#########################################################################
# Financial models

# Financial Model

class BaseFinancialAggregator(Component):

    # Inputs
    turbine_cost = Float(iotype='in', desc = 'A Wind Turbine Capital _cost')
    turbine_number = Int(iotype = 'in', desc = 'number of turbines at plant')
    bos_costs = Float(iotype='in', desc='A Wind Plant Balance of Station _cost Model')
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
        self.create_passthrough('fin.bos_costs')
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

    def configure(self):

        super(BaseFinancialAnalysis, self).configure()

        # To be replaced by actual models
        self.add('tcc_a',BaseTurbineCapitalCostModel())
        self.add('bos_a',BaseBOSCostModel())
        self.add('opex_a',BaseOPEXModel())
        self.add('aep_a',GenericAEPModel())
        self.add('fin_a',BaseFinancialModel())

        self.driver.workflow.add(['tcc_a','bos_a','opex_a','aep_a','fin_a'])

        self.connect('tcc_a.turbine_cost',['fin_a.turbine_cost'])
        self.connect('bos_a.bos_costs','fin_a.bos_costs')
        self.connect('opex_a.avg_annual_opex','fin_a.avg_annual_opex')
        self.connect('aep_a.net_aep','fin_a.net_aep')

        self.create_passthrough('aep_a.net_aep')
        self.create_passthrough('aep_a.gross_aep')
        self.create_passthrough('aep_a.capacity_factor')
        self.create_passthrough('opex_a.avg_annual_opex')
        self.create_passthrough('bos_a.bos_costs')
        self.create_passthrough('tcc_a.turbine_cost')
        self.create_passthrough('fin_a.coe')

class ExtendedFinancialAnalysis(BaseFinancialAnalysis):

    def configure(self):

        super(ExtendedFinancialAnalysis, self).configure()

        # To be replaced by actual models
        #self.replace('tcc',FullTurbineCapitalCostModel())
        self.replace('bos_a',ExtendedBOSCostModel())
        self.replace('opex_a',ExtendedOPEXModel())

        self.connect('tcc_a.turbine_cost',['bos_a.turbine_cost'])
        self.create_passthrough('opex_a.OPEX_breakdown')
        self.create_passthrough('bos_a.BOS_breakdown')