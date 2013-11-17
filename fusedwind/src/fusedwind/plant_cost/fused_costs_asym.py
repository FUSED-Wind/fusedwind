# KLD: Cost model for FUSED_Wind - most basic structure

from openmdao.lib.datatypes.api import Float, Int, Array, VarTree
from openmdao.main.api import Component, Assembly, VariableTree

from fusedwind.plant_cost.fused_tcc_asym import BaseTurbineCapitalCostModel

##########################################################
# Plant Balance of Station and CAPEX Models

# Balance of Station Cost Model
class BaseBOSCostAggregator(Component):

    # Outputs
    bos_costs = Float(iotype='out', desc='Overall wind plant balance of station/system costs up to point of comissioning')

class BaseBOSCostModel(Assembly):
    """
    Framework for a balance of station cost model
    """
    
    def configure(self):
        
        super(BaseBOSCostModel, self).configure()
        
        self.add('bos', BaseBOSCostAggregator())
        
        self.driver.workflow.add('bos')

        self.create_passthrough('bos.bos_costs')

class BOSVarTree(VariableTree):

    management_costs = Float(desc='Project management costs')
    development_costs = Float(desc='Overall wind plant balance of station/system costs up to point of comissioning')
    preparation_and_staging_costs = Float(desc='Site preparation and staging')
    transportation_costs = Float(desc='Any transportation costs to site / staging site')
    foundation_and_substructure_costs = Float(desc='Foundation and substructure costs')
    collection_and_substation_costs = Float(desc='Collection system and onsite substation costs')
    transmission_and_interconnection_costs = Float(desc='Transmission and grid interconnection costs')
    assembly_and_installation_costs = Float(desc='Assembly and installation costs')
    contingencies_and_insurance_costs = Float(desc='Contingencies, bonds, reserves for project')
    decommissioning_costs = Float(desc='Costs associated with plant decommissioning at end of life')
    construction_financing_costs = Float(desc='Construction financing costs')
    other_costs = Float(desc='Bucket for any other costs not captured above')
    developer_profits = Float(desc='Developer profits')

class ExtendedBOSCostAggregator(BaseBOSCostAggregator):
    """
    Framework for a balance of station cost model
    """

    # variables
    machine_rating = Float(iotype='in', units='kW', desc='turbine machine rating')
    rotor_diameter=Float(iotype='in', units='m', desc='rotor diameter')
    hub_height = Float(iotype='in', units='m', desc='hub height')
    RNA_mass = Float(iotype='in', units='kg', desc='Rotor Nacelle Assembly mass')
    turbine_cost = Float(iotype='in', units='USD', desc='Single Turbine Capital Costs')
    
    # parameters
    turbine_number = Int(iotype='in', desc='number of turbines in project')

    # outputs
    BOS_breakdown = VarTree(BOSVarTree(), iotype='out', desc='BOS cost breakdown')
    
    def __init__(self):
      
        super(ExtendedBOSCostAggregator, self).__init__()

class ExtendedBOSCostModel(BaseBOSCostModel):

    def configure(self):
      
        super(ExtendedBOSCostModel, self).configure()
        
        self.replace('bos', ExtendedBOSCostAggregator())
        
        self.create_passthrough('bos.machine_rating')
        self.create_passthrough('bos.rotor_diameter')
        self.create_passthrough('bos.hub_height')
        self.create_passthrough('bos.RNA_mass')
        self.create_passthrough('bos.turbine_number')
        self.create_passthrough('bos.turbine_cost')

        self.create_passthrough('bos.BOS_breakdown')

# CAPEX Models
class BaseCAPEXAggregator(Component):

    # Inputs
    turbine_cost = Float(iotype='in', desc = 'A Wind Turbine Capital Cost')
    turbine_number = Int(iotype = 'in', desc = 'number of turbines at plant')
    bos_cost = Float(iotype='in', desc='A Wind Plant Balance of Station Cost Model')

    # Outputs
    capex = Float(0.0, iotype='out', desc='Overall wind plant capital expenditures including turbine and balance of station costs') 


class BaseCAPEXAnalysis(Assembly):

    # Inputs
    turbine_number = Int(iotype = 'in', desc = 'number of turbines at plant')
    
    def configure(self):
        super(BaseCAPEXAnalysis, self).configure()

        # To be replaced by actual models        
        self.add('tcc',BaseTurbineCapitalCostModel())
        self.add('bos',BaseBOSCostModel())
        self.add('cap_ex',BaseCAPEXAggregator())

        self.driver.workflow.add(['tcc','bos', 'capex'])

        self.connect('turbine_number', ['bos.turbine_number', 'cap_ex.turbine_number'])     
        self.connect('tcc.turbine_cost', 'cap_ex.turbine_cost')
        self.connect('bos.bos_cost', 'cap_ex.bos_cost')
        
        self.create_passthrough('cap_ex.capex')

        
#####################################################################################
# Plant OPEX Models

# OPEX Model
class BaseOPEXAggregator(Component):

    # Outputs
    avg_annual_opex = Float(iotype='out', desc='Average annual Operating Expenditures for a wind plant over its lifetime')

class BaseOPEXModel(Assembly):
    """
    Framework for a balance of station cost model
    """
    
    def configure(self):
        
        super(BaseOPEXModel, self).configure()
        
        self.add('opex', BaseOPEXAggregator())
        
        self.driver.workflow.add('opex')

        self.create_passthrough('opex.avg_annual_opex')
        
class OPEXVT(VariableTree):

    preventative_opex = Float(desc='annual expenditures on preventative maintenance - BOP and turbines')
    corrective_opex = Float(desc='annual unscheduled maintenance costs (replacements) - BOP and turbines')
    lease_opex = Float(desc='annual lease expenditures')
    other_opex = Float(desc='other operational expenditures such as fixed costs')

class ExtendedOPEXAggregator(BaseOPEXAggregator):

    OPEX_breakdown = VarTree(OPEXVT(),iotype='out')
    
    def __init__(self):
    	  
    	  super(ExtendedOPEXAggregator, self).__init__()

class ExtendedOPEXModel(BaseOPEXModel):

    def configure(self):
    	  
    	  super(ExtendedOPEXModel, self).configure()
    	  
    	  self.replace('opex', ExtendedOPEXAggregator())
    	  
    	  self.create_passthrough('opex.OPEX_breakdown')

class FullOPEXModel(BaseOPEXModel):
    """
    Framework for an enhanced operations expenditures model that gives a series of annual operating expenditures over the the plants lifetime
    """

    # Outputs
    annual_opex = Array(iotype='out', desc='Array of annual Operating Expenditure estimates for each year of expected project operation')


########################################################################################
# Plant Decommissioning Specific Models (usually part of CAPEX or OPEX)

# DECOMEX Model
class BaseDECOMEXModel(Assembly):
    """
    Framework for a decomissioning expenditures model for plant end of life
    """

    # Outputs
    decomex = Float(iotype='out', desc='General DECOMEX model produces Decomissioning Expenditures for a wind plant for the end of its life')