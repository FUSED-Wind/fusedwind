# Turbine _cost Model Framework
# KLD 11/14/2013

from openmdao.lib.datatypes.api import Float, Int, VarTree
from openmdao.main.api import Component, Assembly

from fusedwind.interface import implement_base

from fusedwind.plant_flow.asym import BaseAEPModel
from fusedwind.plant_cost.fused_bos_costs import BaseBOSCostAggregator, BaseBOSCostModel, configure_base_bos, BOSVarTree, \
                                                  ExtendedBOSCostAggregator, ExtendedBOSCostModel, configure_extended_bos, FullBOSVarTree, \
                                                  FullBOSCostAggregator, FullBOSCostModel, configure_full_bos, BaseCAPEXAggregator, configure_capex
from fusedwind.plant_cost.fused_opex import BaseOPEXAggregator, BaseOPEXModel, configure_base_opex, OPEXVarTree, ExtendedOPEXAggregator, \
                                            ExtendedOPEXModel, configure_extended_opex, FullOPEXAggregator, BaseDECOMEXModel
from fusedwind.plant_cost.fused_tcc import BaseComponentCostModel, BaseSubAssemblyCostModel, configure_base_subassembly_cost, BaseSubAssemblyCostAggregator, \
                                            BaseTCCAggregator, BaseTurbineCostModel, configure_base_tcc, ExtendedTCCAggregator, \
                                            ExtendedTurbineCostModel, configure_extended_tcc, FullRotorCostAggregator, FullHubSystemCostAggregator, \
                                            FullRotorCostModel, configure_full_rcc, FullNacelleCostAggregator, FullNacelleCostModel, \
                                            configure_full_ncc, FullTowerCostAggregator, FullTowerCostModel, configure_full_twcc, \
                                            FullTCCAggregator, FullTurbineCostModel, configure_full_tcc
from fusedwind.plant_cost.fused_finance import BaseFinancialAggregator, BaseFinancialModel, configure_base_finance, BaseFinancialAnalysis, \
                                                configure_base_financial_analysis, ExtendedFinancialAnalysis, configure_extended_financial_analysis

##############################################################
# Turbine _cost Models

# ------------------------------------------------------------
# Basic Turbine Captial _costs

# Basic Turbine Cost Model Building Blocks

@implement_base(BaseTCCAggregator)
class BaseTCCAggregator_Example(Component):
    """ Base turbine capital cost aggregator for doing some auxiliary cost calculations needed to get a full wind turbine cost.    """

    # Outputs
    turbine_cost = Float(iotype='out', desc='Overall wind turbine capial costs including transportation costs')
    
    def execute(self):
        
        self.turbine_cost = 9000000.0

# Basic Turbine _cost Model
@implement_base(BaseTurbineCostModel)
class BaseTurbineCostModel_Example(Assembly):
    """ Base turbine capital cost assembly for coupling models to get a full wind turbine cost.    """

    # Outputs
    turbine_cost = Float(iotype='out', desc='Overall wind turbine capial costs including transportation costs')
    
    def configure(self):
        
        configure_base_tcc(self)
        
        self.replace('tcc', BaseTCCAggregator_Example())

# ------------------------------------------------------------
# Extended Turbine Capital Costs
@implement_base(BaseTCCAggregator)
class ExtendedTCCAggregator_Example(Component):
    """ Extended turbine capital cost aggregator for doing some auxiliary cost calculations needed to get a full wind turbine cost.  It assume sub-models for rotor, nacelle and tower cost.    """

    # Variables
    rotor_cost = Float(iotype='in', units='USD', desc='rotor cost')
    nacelle_cost = Float(iotype='in', units='USD', desc='nacelle cost')
    tower_cost = Float(iotype='in', units='USD', desc='tower cost')

    # Outputs
    turbine_cost = Float(iotype='out', desc='Overall wind turbine capial costs including transportation costs')

    def execute(self):
        
        self.turbine_cost = self.rotor_cost + self.nacelle_cost + self.tower_cost
    

# Sub-assembly models
@implement_base(BaseSubAssemblyCostAggregator)
class RotorSubAssemblyCostAggregator(Component):
    """ Base sub assembly cost aggregator for doing some auxiliary cost calculations needed to get a wind turbine component cost.    """

    # Outputs
    cost = Float(iotype='out', desc='Overall wind sub-assembly capial costs including transportation costs')

    def execute(self):
        
        self.cost = 9000000.0/3.0

@implement_base(BaseSubAssemblyCostModel)
class RotorSubAssemblyCostModel(Assembly):
    """ Base sub assembly cost model class for an arbitrary wind turbine component.    """

    # Outputs
    cost = Float(iotype='out', desc='Overall wind sub-assembly capial costs including transportation costs')
    
    def configure(self):

        configure_base_subassembly_cost(self)
        
        self.replace('bcc',RotorSubAssemblyCostAggregator())

@implement_base(BaseSubAssemblyCostAggregator)
class NacelleSubAssemblyCostAggregator(Component):
    """ Base sub assembly cost aggregator for doing some auxiliary cost calculations needed to get a wind turbine component cost.    """

    # Outputs
    cost = Float(iotype='out', desc='Overall wind sub-assembly capial costs including transportation costs')

    def execute(self):
        
        self.cost = 9000000.0/3.0

@implement_base(BaseSubAssemblyCostModel)
class NacelleSubAssemblyCostModel(Assembly):
    """ Base sub assembly cost model class for an arbitrary wind turbine component.    """

    # Outputs
    cost = Float(iotype='out', desc='Overall wind sub-assembly capial costs including transportation costs')
    
    def configure(self):

        configure_base_subassembly_cost(self)
        
        self.replace('bcc',NacelleSubAssemblyCostAggregator())

@implement_base(BaseSubAssemblyCostAggregator)
class TowerSubAssemblyCostAggregator(Component):
    """ Base sub assembly cost aggregator for doing some auxiliary cost calculations needed to get a wind turbine component cost.    """

    # Outputs
    cost = Float(iotype='out', desc='Overall wind sub-assembly capial costs including transportation costs')

    def execute(self):
        
        self.cost = 9000000.0/3.0

@implement_base(BaseSubAssemblyCostModel)
class TowerSubAssemblyCostModel(Assembly):
    """ Base sub assembly cost model class for an arbitrary wind turbine component.    """

    # Outputs
    cost = Float(iotype='out', desc='Overall wind sub-assembly capial costs including transportation costs')
    
    def configure(self):

        configure_base_subassembly_cost(self)
        
        self.replace('bcc',TowerSubAssemblyCostAggregator())

# Extended Turbine Capital _cost Model Includes sub-assembly cost aggregation
@implement_base(ExtendedTurbineCostModel)
class ExtendedTurbineCostModel_Example(Assembly):
    """ Extended turbine capital cost assembly for coupling models to get a full wind turbine cost.    """

    # Outputs
    turbine_cost = Float(iotype='out', desc='Overall wind turbine capial costs including transportation costs')

    def configure(self):
        
        configure_extended_tcc(self)
        
        self.replace('tcc', ExtendedTCCAggregator_Example())
        self.replace('rotorCC', RotorSubAssemblyCostModel())
        self.replace('nacelleCC', NacelleSubAssemblyCostModel())
        self.replace('towerCC', TowerSubAssemblyCostModel())

# ------------------------------------------------------------
# Full Turbine Capital _costs

# Individual Component Models
# Basic Turbine Cost Model Building Blocks
@implement_base(BaseComponentCostModel)
class BladeComponentCostModel(Component):
    """ Base component cost model class for an arbitrary wind turbine component.    """

    # Outputs
    cost = Float(iotype='out', desc='Base turbine component cost')

    def execute(self):
        
        self.cost = 350000.0
        
@implement_base(BaseComponentCostModel)
class HubComponentCostModel(Component):
    """ Base component cost model class for an arbitrary wind turbine component.    """

    # Outputs
    cost = Float(iotype='out', desc='Base turbine component cost')

    def execute(self):
        
        self.cost = 300000.0

@implement_base(BaseComponentCostModel)
class PitchSysComponentCostModel(Component):
    """ Base component cost model class for an arbitrary wind turbine component.    """

    # Outputs
    cost = Float(iotype='out', desc='Base turbine component cost')

    def execute(self):
        
        self.cost = 300000.0

@implement_base(BaseComponentCostModel)
class SpinnerComponentCostModel(Component):
    """ Base component cost model class for an arbitrary wind turbine component.    """

    # Outputs
    cost = Float(iotype='out', desc='Base turbine component cost')

    def execute(self):
        
        self.cost = 400000.0

# Full Sub-Assembly _cost Models
@implement_base(FullRotorCostAggregator)
class FullRotorCostAggregator_Example(Component):
    """ Full rotor cost aggregator for aggregating rotor costs from blades and hub system.    """

    # variables
    blade_cost = Float(iotype='in', units='USD', desc='individual blade cost')
    hub_system_cost = Float(iotype='in', units='USD', desc='cost for hub system')
    
    # parameters
    blade_number = Int(iotype='in', desc='number of rotor blades')
    
    # returns
    cost = Float(iotype='out', units='USD', desc='overall rotor cost')

    def execute(self):
        
        self.cost = self.blade_number * self.blade_cost + self.hub_system_cost

@implement_base(FullHubSystemCostAggregator)
class FullHubSystemCostAggregator_Example(Component):
    """ Full hub system cost aggregator for aggregating hub component costs.    """

    # variables
    hub_cost = Float(iotype='in', units='USD', desc='hub component cost')
    pitch_system_cost = Float(iotype='in', units='USD', desc='pitch system cost')
    spinner_cost = Float(iotype='in', units='USD', desc='spinner component cost')
    
    # returns
    cost = Float(iotype='out', units='USD', desc='overall hub system cost')
    
    def execute(self):
        
        self.cost = self.hub_cost + self.pitch_system_cost + self.spinner_cost

@implement_base(FullRotorCostModel)
class FullRotorCostModel_Example(Assembly):
    """ Full rotor cost sub-assembly for aggregating rotor component costs.    """

    # parameters
    blade_number = Int(iotype='in', desc='number of rotor blades')

    # Outputs
    cost = Float(iotype='out', desc='Overall wind sub-assembly capial costs including transportation costs')
    
    def configure(self):
        
        configure_full_rcc(self)

        self.replace('bladeCC', BladeComponentCostModel())
        self.replace('hubCC', HubComponentCostModel())
        self.replace('pitchSysCC', PitchSysComponentCostModel())
        self.replace('spinnerCC', SpinnerComponentCostModel())
        self.replace('hubSysCC', FullHubSystemCostAggregator_Example())
        self.replace('rcc', FullRotorCostAggregator_Example())

# Nacelle component models
@implement_base(BaseComponentCostModel)
class LSSComponentCostModel(Component):
    """ Base component cost model class for an arbitrary wind turbine component.    """

    # Outputs
    cost = Float(iotype='out', desc='Base turbine component cost')

    def execute(self):
        
        self.cost = 500000.0

@implement_base(BaseComponentCostModel)
class BearingsComponentCostModel(Component):
    """ Base component cost model class for an arbitrary wind turbine component.    """

    # Outputs
    cost = Float(iotype='out', desc='Base turbine component cost')

    def execute(self):
        
        self.cost = 500000.0

@implement_base(BaseComponentCostModel)
class GearboxComponentCostModel(Component):
    """ Base component cost model class for an arbitrary wind turbine component.    """

    # Outputs
    cost = Float(iotype='out', desc='Base turbine component cost')

    def execute(self):
        
        self.cost = 1000000.0

@implement_base(BaseComponentCostModel)
class GeneratorComponentCostModel(Component):
    """ Base component cost model class for an arbitrary wind turbine component.    """

    # Outputs
    cost = Float(iotype='out', desc='Base turbine component cost')

    def execute(self):
        
        self.cost = 500000.0

@implement_base(BaseComponentCostModel)
class HSSComponentCostModel(Component):
    """ Base component cost model class for an arbitrary wind turbine component.    """

    # Outputs
    cost = Float(iotype='out', desc='Base turbine component cost')

    def execute(self):
        
        self.cost = 500000.0

@implement_base(BaseComponentCostModel)
class BedplateComponentCostModel(Component):
    """ Base component cost model class for an arbitrary wind turbine component.    """

    # Outputs
    cost = Float(iotype='out', desc='Base turbine component cost')

    def execute(self):
        
        self.cost = 500000.0

@implement_base(BaseComponentCostModel)
class YawSystemComponentCostModel(Component):
    """ Base component cost model class for an arbitrary wind turbine component.    """

    # Outputs
    cost = Float(iotype='out', desc='Base turbine component cost')

    def execute(self):
        
        self.cost = 500000.0

@implement_base(FullNacelleCostAggregator)
class FullNacelleCostAggregator_Example(Component):
    """ Full nacelle cost aggregator to aggregate costs of individual nacelle components.    """

    # variables
    lss_cost = Float(iotype='in', units='USD', desc='component cost')
    bearings_cost = Float(iotype='in', units='USD', desc='component cost')
    gearbox_cost = Float(iotype='in', units='USD', desc='component cost')
    hss_cost = Float(iotype='in', units='USD', desc='component cost')
    generator_cost = Float(iotype='in', units='USD', desc='component cost')
    bedplate_cost = Float(iotype='in', units='USD', desc='component cost')
    yaw_system_cost = Float(iotype='in', units='USD', desc='component cost')
    
    # returns
    cost = Float(iotype='out', units='USD', desc='component cost')

    def execute(self):
        
        self.cost = self.lss_cost + self.bearings_cost + self.gearbox_cost + self.hss_cost + self.generator_cost + self.bedplate_cost + self.yaw_system_cost

@implement_base(FullNacelleCostModel)
class FullNacelleCostModel_Example(Assembly):
    """ Full nacelle cost sub-assembly for bringing together individual nacelle component cost models.    """

    # returns
    cost = Float(iotype='out', units='USD', desc='component cost')
    
    def configure(self):
        
        configure_full_ncc(self)

        self.replace('lssCC', LSSComponentCostModel())
        self.replace('bearingsCC', BearingsComponentCostModel())
        self.replace('gearboxCC', GearboxComponentCostModel())
        self.replace('hssCC', HSSComponentCostModel())
        self.replace('generatorCC', GeneratorComponentCostModel())
        self.replace('bedplateCC', BedplateComponentCostModel())
        self.replace('yawSysCC', YawSystemComponentCostModel())
        self.replace('ncc', FullNacelleCostAggregator_Example())


# Tower models and sub-assemblies
@implement_base(BaseComponentCostModel)
class TowerComponentCostModel(Component):
    """ Base component cost model class for an arbitrary wind turbine component.    """

    # Outputs
    cost = Float(iotype='out', desc='Base turbine component cost')

    def execute(self):
        
        self.cost = 4000000.0

@implement_base(FullTowerCostAggregator)
class FullTowerCostAggregator_Example(Component):
    """ Full tower cost aggregator to aggregate costs of individual tower components.    """

    # variables
    tower_cost = Float(iotype='in', units='USD', desc='component cost')
    
    # returns
    cost = Float(iotype='out', units='USD', desc='component cost')    
    
    def execute(self):
        
        self.cost = self.tower_cost

@implement_base(FullTowerCostModel)
class FullTowerCostModel_Example(Assembly):
    """ Full tower cost sub-assembly for bringing together individual tower component cost models.    """

    # returns
    cost = Float(iotype='out', units='USD', desc='component cost')  
    
    def configure(self):
        
        configure_full_twcc(self)
        
        self.replace('towerCC', TowerComponentCostModel())  
        self.replace('twrcc',FullTowerCostAggregator_Example())

# Full Turbine Cost Model
@implement_base(FullTCCAggregator)
class FullTCCAggregator_Example(Component):
    """ Full turbine capital cost aggregator for doing some auxiliary cost calculations needed to get a full wind turbine cost.  It assume sub-models for rotor, nacelle and tower cost.    """

    # Variables
    rotor_cost = Float(iotype='in', units='USD', desc='rotor cost')
    nacelle_cost = Float(iotype='in', units='USD', desc='nacelle cost')
    tower_cost = Float(iotype='in', units='USD', desc='tower cost')

    # Outputs
    turbine_cost = Float(iotype='out', desc='Overall wind turbine capial costs including transportation costs')
    
    def execute(self):
        
        self.turbine_cost = self.rotor_cost + self.nacelle_cost + self.tower_cost

@implement_base(FullTurbineCostModel)
class FullTurbineCostModel_Example(Assembly):
    """ Full turbine capital cost assembly for coupling models to get a full wind turbine cost.    """

    # Outputs
    turbine_cost = Float(iotype='out', desc='Overall wind turbine capial costs including transportation costs')
    
    def configure(self):
        
        configure_full_tcc(self)
        
        self.replace('rotorCC', FullRotorCostModel_Example())
        self.replace('nacelleCC', FullNacelleCostModel_Example())
        self.replace('towerCC', FullTowerCostModel_Example())
        self.replace('tcc',FullTCCAggregator_Example())

##########################################################
# Plant Balance of Station and CAPEX Models

# Balance of Station Cost Model
# Base Variable Trees, Components and Assemblies
@implement_base(BaseBOSCostAggregator)
class BaseBOSCostAggregator_Example(Component):
    """ Base balance of station cost aggregator for doing some auxiliary cost calculations needed to get a full wind plant balance of station cost estimate.    """

    # Outputs
    bos_costs = Float(iotype='out', desc='Overall wind plant balance of station/system costs up to point of comissioning')

    def execute(self):
        
        self.bos_costs = 1800000000.0

@implement_base(BaseBOSCostModel)
class BaseBOSCostModel_Example(Assembly):
    """ Base balance of station cost assembly for coupling models to get a full wind plant balance of station cost estimate.    """

    # Outputs
    bos_costs = Float(iotype='out', desc='Overall wind plant balance of station/system costs up to point of comissioning')

    def configure(self):
        
        configure_base_bos(self)

        self.replace('bos', BaseBOSCostAggregator_Example())


#Extended Variable Trees, Components and Assemblies

@implement_base(ExtendedBOSCostAggregator)
class ExtendedBOSCostAggregator_Example(Component):
    """ Extended balance of station cost aggregator for doing some auxiliary cost calculations needed to get a full wind plant balance of station cost estimate as well as a detailed cost breakdown.    """

    # Outputs
    bos_breakdown = VarTree(BOSVarTree(), iotype='out', desc='BOS cost breakdown')
    bos_costs = Float(iotype='out', desc='Overall wind plant balance of station/system costs up to point of comissioning')

    def execute(self):
        
        self.bos_costs = 1800000000.0
        self.bos_breakdown.development_costs = self.bos_costs * 0.05
        self.bos_breakdown.preparation_and_staging_costs = self.bos_costs * 0.10
        self.bos_breakdown.transportation_costs = self.bos_costs * 0.20
        self.bos_breakdown.foundation_and_substructure_costs = self.bos_costs * 0.20
        self.bos_breakdown.electrical_costs = self.bos_costs * 0.15
        self.bos_breakdown.assembly_and_installation_costs = self.bos_costs * 0.15
        self.bos_breakdown.soft_costs = self.bos_costs * 0.10
        self.bos_breakdown.other_costs = self.bos_costs * 0.05

@implement_base(ExtendedBOSCostModel)
class ExtendedBOSCostModel_Example(Assembly):
    """ Extended balance of station cost assembly for coupling models to get a full wind plant balance of station cost estimate as well as a detailed cost breakdown.    """

    # Outputs
    bos_breakdown = VarTree(BOSVarTree(), iotype='out', desc='BOS cost breakdown')
    bos_costs = Float(iotype='out', desc='Overall wind plant balance of station/system costs up to point of comissioning')

    def configure(self):
        
        configure_extended_bos(self)

        self.replace('bos', ExtendedBOSCostAggregator_Example())

# Full BOS Cost Aggregator Variable Trees, Costs and Assemblies
@implement_base(FullBOSCostAggregator)
class FullBOSCostAggregator_Example(Component):
    """ Full balance of station cost aggregator for doing some auxiliary cost calculations needed to get a full wind plant balance of station cost estimate as well as a detailed cost breakdown.    """

    # outputs
    bos_breakdown = VarTree(FullBOSVarTree(), iotype='out', desc='BOS cost breakdown')
    bos_costs = Float(iotype='out', desc='Output BOS cost elements')

    def execute(self):
        
        self.bos_costs = 1800000000.0
        self.bos_breakdown.management_costs = self.bos_costs * 0.025
        self.bos_breakdown.development_costs = self.bos_costs * 0.025
        self.bos_breakdown.preparation_and_staging_costs = self.bos_costs * 0.10
        self.bos_breakdown.transportation_costs = self.bos_costs * 0.10
        self.bos_breakdown.foundation_and_substructure_costs = self.bos_costs * 0.15
        self.bos_breakdown.collection_and_substation_costs = self.bos_costs * 0.15
        self.bos_breakdown.transmission_and_interconnection_costs = self.bos_costs * 0.10
        self.bos_breakdown.assembly_and_installation_costs = self.bos_costs * 0.15
        self.bos_breakdown.contingencies_and_insurance_costs = self.bos_costs * 0.05
        self.bos_breakdown.decommissioning_costs = self.bos_costs * 0.05
        self.bos_breakdown.construction_financing_costs = self.bos_costs * 0.05
        self.bos_breakdown.other_costs = self.bos_costs * 0.025
        self.bos_breakdown.developer_profits = self.bos_costs * 0.025

@implement_base(FullBOSCostModel)
class FullBOSCostModel_Example(Assembly):
    
    # outputs
    bos_breakdown = VarTree(FullBOSVarTree(), iotype='out', desc='BOS cost breakdown')
    bos_costs = Float(iotype='out', desc='Output BOS cost elements')  
    
    def configure(self):

        configure_full_bos(self)

        self.replace('bos', FullBOSCostAggregator_Example())

#####################################################################################
# Plant OPEX Models

# OPEX Model Variable Trees, Components and Assemblies
@implement_base(BaseOPEXAggregator)
class BaseOPEXAggregator_Example(Component):
    """ Base operational expenditures aggregator for doing some auxiliary cost calculations needed to get a full wind plant operational expenditures estimate.    """

    # Outputs
    avg_annual_opex = Float(iotype='out', desc='Average annual Operating Expenditures for a wind plant over its lifetime')

    def execute(self):
        
        self.avg_annual_opex = 50000000.00

@implement_base(BaseOPEXModel)
class BaseOPEXModel_Example(Assembly):
    """ Base operational expenditures assembly for coupling models to get a full wind plant operational expenditures estimate.    """

    # Outputs
    avg_annual_opex = Float(iotype='out', desc='Average annual Operating Expenditures for a wind plant over its lifetime')

    def configure(self):
        
        configure_base_opex(self)
        
        self.replace('opex',BaseOPEXAggregator_Example())

# Extended Variable Trees, Components and Assemblies
@implement_base(ExtendedOPEXAggregator)
class ExtendedOPEXAggregator_Example(Component):
    """ Extended operational expenditures aggregator for doing some auxiliary cost calculations needed to get a full wind plant operational expenditures estimate as well as a detailed cost breakdown.    """

    # Outputs
    avg_annual_opex = Float(iotype='out', desc='Average annual Operating Expenditures for a wind plant over its lifetime')
    opex_breakdown = VarTree(OPEXVarTree(),iotype='out')

    def execute(self):
        
        self.avg_annual_opex = 50000000.00
        self.opex_breakdown.preventative_opex = self.avg_annual_opex * 0.25
        self.opex_breakdown.corrective_opex = self.avg_annual_opex * 0.50
        self.opex_breakdown.lease_opex = self.avg_annual_opex * 0.25
        self.opex_breakdown.other_opex = 0.0

@implement_base(ExtendedOPEXModel)
class ExtendedOPEXModel_Example(Assembly):
    """ Extended operational expenditures assembly for coupling models to get a full wind plant operational expenditures estimate as well as a detailed cost breakdown.    """

    # Outputs
    avg_annual_opex = Float(iotype='out', desc='Average annual Operating Expenditures for a wind plant over its lifetime')
    opex_breakdown = VarTree(OPEXVarTree(),iotype='out')

    def configure(self):
        
        configure_extended_opex(self)
        
        self.replace('opex',ExtendedOPEXAggregator_Example())

#########################################################################
# AEP model

@implement_base(BaseAEPModel)
class BaseAEPModel_Example(Assembly):

    # Outputs
    gross_aep = Float(1752000000.0, iotype='out', units='kW*h',  desc='Gross Annual Energy Production before availability and loss impacts')
    net_aep = Float(1752000000.0, iotype='out', units='kW*h',  desc='Net Annual Energy Production after availability and loss impacts')
    capacity_factor = Float(0.4, iotype='out', desc='Capacity factor for wind plant')

#########################################################################
# Financial models

# Base Financial Model
@implement_base(BaseFinancialAggregator)
class BaseFinancialAggregator_Example(Component):
    """ Base financial aggregator for doing some auxiliary cost calculations needed to get a full wind plant cost of energy estimate.    """

    # Inputs
    turbine_cost = Float(iotype='in', desc = 'A Wind Turbine Capital _cost')
    turbine_number = Int(iotype = 'in', desc = 'number of turbines at plant')
    bos_costs = Float(iotype='in', desc='A Wind Plant Balance of Station _cost Model')
    avg_annual_opex = Float(iotype='in', desc='A Wind Plant Operations Expenditures Model')
    net_aep = Float(iotype='in', desc='A Wind Plant Annual Energy Production Model', units='kW*h')

    #Outputs
    coe = Float(iotype='out', desc='Levelized cost of energy for the wind plant')

    def execute(self):
        
        self.coe = (0.1 * (self.turbine_cost * self.turbine_number + self.bos_costs) + 0.4 * self.avg_annual_opex)/self.net_aep

@implement_base(BaseFinancialModel)
class BaseFinancialModel_Example(Assembly):
    """ Base financial assembly for coupling models to get a full wind plant cost of energy estimate.    """

    # Inputs
    turbine_cost = Float(iotype='in', desc = 'A Wind Turbine Capital _cost')
    turbine_number = Int(iotype = 'in', desc = 'number of turbines at plant')
    bos_costs = Float(iotype='in', desc='A Wind Plant Balance of Station _cost Model')
    avg_annual_opex = Float(iotype='in', desc='A Wind Plant Operations Expenditures Model')
    net_aep = Float(iotype='in', desc='A Wind Plant Annual Energy Production Model', units='kW*h')

    #Outputs
    coe = Float(iotype='out', desc='Levelized cost of energy for the wind plant')
    
    def configure(self):
        
        configure_base_finance(self)
        
        self.replace('fin', BaseFinancialAggregator_Example())

# Ignoring more detailed financial model structures for now

#########################################################################
# Implementation assembly shells

# Main financial assembly
@implement_base(BaseFinancialAnalysis)
class BaseFinancialAnalysis_Example(Assembly):
    """ Base financial analysis assembly for coupling models to get a full wind plant cost of energy estimate.    """

    # Inputs
    turbine_number = Int(iotype = 'in', desc = 'number of turbines at plant')

    #Outputs
    turbine_cost = Float(iotype='out', desc = 'A Wind Turbine Capital _cost')
    bos_costs = Float(iotype='out', desc='A Wind Plant Balance of Station _cost Model')
    avg_annual_opex = Float(iotype='out', desc='A Wind Plant Operations Expenditures Model')
    net_aep = Float(iotype='out', desc='A Wind Plant Annual Energy Production Model', units='kW*h')
    coe = Float(iotype='out', desc='Levelized cost of energy for the wind plant')

    def configure(self):
      
        configure_base_financial_analysis(self)
        
        self.replace('tcc_a',BaseTurbineCostModel_Example())
        self.replace('bos_a',BaseBOSCostModel_Example())
        self.replace('opex_a',BaseOPEXModel_Example())
        self.replace('aep_a',BaseAEPModel_Example())
        self.replace('fin_a',BaseFinancialModel_Example())

@implement_base(ExtendedFinancialAnalysis)
class ExtendedFinancialAnalysis_Example(Assembly):
    """ Extended financial analysis assembly for coupling models to get a full wind plant cost of energy estimate as well as provides a detailed cost breakdown for the plant.    """

    # Inputs
    turbine_number = Int(iotype = 'in', desc = 'number of turbines at plant')

    #Outputs
    turbine_cost = Float(iotype='out', desc = 'A Wind Turbine Capital _cost')
    bos_costs = Float(iotype='out', desc='A Wind Plant Balance of Station _cost Model')
    avg_annual_opex = Float(iotype='out', desc='A Wind Plant Operations Expenditures Model')
    net_aep = Float(iotype='out', desc='A Wind Plant Annual Energy Production Model', units='kW*h')
    coe = Float(iotype='out', desc='Levelized cost of energy for the wind plant')
    opex_breakdown = VarTree(OPEXVarTree(),iotype='out')
    bos_breakdown = VarTree(BOSVarTree(), iotype='out', desc='BOS cost breakdown')
    
    def configure(self):
        
        configure_extended_financial_analysis(self)

        self.replace('tcc_a',BaseTurbineCostModel_Example())
        self.replace('aep_a',BaseAEPModel_Example())
        self.replace('fin_a',BaseFinancialModel_Example())        
        self.replace('bos_a',ExtendedBOSCostModel_Example())
        self.replace('opex_a',ExtendedOPEXModel_Example())