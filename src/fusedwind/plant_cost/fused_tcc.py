# Turbine _cost Model Framework
# KLD 11/14/2013

from openmdao.lib.datatypes.api import Float, Int
from openmdao.main.api import Component, Assembly

from fusedwind.interface import base, implement_base

##############################################################
# Turbine _cost Models

# ------------------------------------------------------------
# Basic Turbine Captial _costs

# Basic Turbine Cost Model Building Blocks
@base
class BaseComponentCostModel(Component):
    """ Base component cost model class for an arbitrary wind turbine component.    """

    # Outputs
    cost = Float(iotype='out', desc='Base turbine component cost')

@base
class BaseSubAssemblyCostModel(Assembly):
    """ Base sub assembly cost model class for an arbitrary wind turbine component.    """

    # Outputs
    cost = Float(iotype='out', desc='Overall wind sub-assembly capial costs including transportation costs')

    def configure(self):
        
        configure_base_subassembly_cost(self)

@base
class BaseSubAssemblyCostAggregator(Component):
    """ Base sub assembly cost aggregator for doing some auxiliary cost calculations needed to get a wind turbine component cost.    """

    # Outputs
    cost = Float(iotype='out', desc='Overall wind sub-assembly capial costs including transportation costs')

def configure_base_subassembly_cost(assembly):
    """ Configure method for base sub assembly for cost models."""

    assembly.add('bcc',BaseSubAssemblyCostAggregator())
    
    assembly.connect('bcc.cost','cost')

@base
class BaseTCCAggregator(Component):
    """ Base turbine capital cost aggregator for doing some auxiliary cost calculations needed to get a full wind turbine cost.    """

    # Outputs
    turbine_cost = Float(iotype='out', desc='Overall wind turbine capial costs including transportation costs')

# Basic Turbine _cost Model
@base
class BaseTurbineCostModel(Assembly):
    """ Base turbine capital cost assembly for coupling models to get a full wind turbine cost.    """

    # Outputs
    turbine_cost = Float(iotype='out', desc='Overall wind turbine capial costs including transportation costs')

def configure_base_tcc(assembly):
    """ Base configure method for a turbine capital cost assembly for coupling models to get a full wind turbine cost.  It adds a default turbine capital cost aggregator component.    """

    assembly.add('tcc', BaseTCCAggregator())

    assembly.driver.workflow.add(['tcc'])

    assembly.connect('tcc.turbine_cost','turbine_cost')

# ------------------------------------------------------------
# Extended Turbine Capital Costs
@implement_base(BaseTCCAggregator)
class ExtendedTCCAggregator(Component):
    """ Extended turbine capital cost aggregator for doing some auxiliary cost calculations needed to get a full wind turbine cost.  It assume sub-models for rotor, nacelle and tower cost.    """

    # Variables
    rotor_cost = Float(iotype='in', units='USD', desc='rotor cost')
    nacelle_cost = Float(iotype='in', units='USD', desc='nacelle cost')
    tower_cost = Float(iotype='in', units='USD', desc='tower cost')

    # Outputs
    turbine_cost = Float(iotype='out', desc='Overall wind turbine capial costs including transportation costs')

# Extended Turbine Capital _cost Model Includes sub-assembly cost aggregation
@implement_base(BaseTurbineCostModel)
class ExtendedTurbineCostModel(Assembly):
    """ Extended turbine capital cost assembly for coupling models to get a full wind turbine cost.    """

    # Outputs
    turbine_cost = Float(iotype='out', desc='Overall wind turbine capial costs including transportation costs')

def configure_extended_tcc(assembly):
    """ Extended configure method for a turbine capital cost assembly for coupling models to get a full wind turbine cost.  It adds a default turbine capital cost aggregator component as well as default cost models for the rotor, nacelle and tower.    """

    configure_base_tcc(assembly)

    assembly.add('rotorCC', BaseSubAssemblyCostModel())
    assembly.add('nacelleCC', BaseSubAssemblyCostModel())
    assembly.add('towerCC', BaseSubAssemblyCostModel())
    assembly.replace('tcc', ExtendedTCCAggregator())

    assembly.driver.workflow.add(['rotorCC', 'nacelleCC', 'towerCC'])

    assembly.connect('rotorCC.cost', 'tcc.rotor_cost')
    assembly.connect('nacelleCC.cost', 'tcc.nacelle_cost')
    assembly.connect('towerCC.cost', 'tcc.tower_cost')

# ------------------------------------------------------------
# Full Turbine Capital _costs

# Full Sub-Assembly _cost Models
@implement_base(BaseSubAssemblyCostAggregator)
class FullRotorCostAggregator(Component):
    """ Full rotor cost aggregator for aggregating rotor costs from blades and hub system.    """

    # variables
    blade_cost = Float(iotype='in', units='USD', desc='individual blade cost')
    hub_system_cost = Float(iotype='in', units='USD', desc='cost for hub system')
    
    # parameters
    blade_number = Int(iotype='in', desc='number of rotor blades')
    
    # returns
    cost = Float(iotype='out', units='USD', desc='overall rotor cost')

@implement_base(BaseSubAssemblyCostAggregator)
class FullHubSystemCostAggregator(Component):
    """ Full hub system cost aggregator for aggregating hub component costs.    """

    # variables
    hub_cost = Float(iotype='in', units='USD', desc='hub component cost')
    pitch_system_cost = Float(iotype='in', units='USD', desc='pitch system cost')
    spinner_cost = Float(iotype='in', units='USD', desc='spinner component cost')
    
    # returns
    cost = Float(iotype='out', units='USD', desc='overall hub system cost')    

@implement_base(BaseSubAssemblyCostModel)
class FullRotorCostModel(Assembly):
    """ Full rotor cost sub-assembly for aggregating rotor component costs.    """

    # parameters
    blade_number = Int(iotype='in', desc='number of rotor blades')

    # Outputs
    cost = Float(iotype='out', desc='Overall wind sub-assembly capial costs including transportation costs')

def configure_full_rcc(assembly):
    """ Configure method for a detailed rotor cost model including cost models for each major rotor system component.    """

    assembly.add('bladeCC', BaseComponentCostModel())
    assembly.add('hubCC', BaseComponentCostModel())
    assembly.add('pitchSysCC', BaseComponentCostModel())
    assembly.add('spinnerCC', BaseComponentCostModel())
    assembly.add('hubSysCC', FullHubSystemCostAggregator())
    assembly.add('rcc', FullRotorCostAggregator())

    assembly.driver.workflow.add(['hubCC', 'pitchSysCC', 'spinnerCC', 'hubSysCC', 'bladeCC', 'rcc'])
    
    assembly.connect('blade_number', 'rcc.blade_number')
    assembly.connect('hubCC.cost', 'hubSysCC.hub_cost')
    assembly.connect('pitchSysCC.cost', 'hubSysCC.pitch_system_cost')
    assembly.connect('spinnerCC.cost', 'hubSysCC.spinner_cost')
    assembly.connect('hubSysCC.cost', 'rcc.hub_system_cost')
    assembly.connect('bladeCC.cost', 'rcc.blade_cost')
    assembly.connect('rcc.cost', 'cost')

@implement_base(BaseSubAssemblyCostAggregator)
class FullNacelleCostAggregator(Component):
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

@implement_base(BaseSubAssemblyCostModel)
class FullNacelleCostModel(Assembly):
    """ Full nacelle cost sub-assembly for bringing together individual nacelle component cost models.    """

    # returns
    cost = Float(iotype='out', units='USD', desc='component cost')

def configure_full_ncc(assembly):
    """ Configure method for a detailed nacelle cost model including cost models for each major nacelle system component.    """

    assembly.add('lssCC', BaseComponentCostModel())
    assembly.add('bearingsCC', BaseComponentCostModel())
    assembly.add('gearboxCC', BaseComponentCostModel())
    assembly.add('hssCC', BaseComponentCostModel())
    assembly.add('generatorCC', BaseComponentCostModel())
    assembly.add('bedplateCC', BaseComponentCostModel())
    assembly.add('yawSysCC', BaseComponentCostModel())
    assembly.add('ncc', FullNacelleCostAggregator())

    assembly.driver.workflow.add(['lssCC', 'bearingsCC', 'gearboxCC', 'hssCC', 'generatorCC', 'bedplateCC', 'yawSysCC', 'ncc'])
    
    assembly.connect('lssCC.cost', 'ncc.lss_cost')
    assembly.connect('bearingsCC.cost', 'ncc.bearings_cost')
    assembly.connect('gearboxCC.cost', 'ncc.gearbox_cost')
    assembly.connect('hssCC.cost', 'ncc.hss_cost')
    assembly.connect('generatorCC.cost', 'ncc.generator_cost')
    assembly.connect('bedplateCC.cost', 'ncc.bedplate_cost')
    assembly.connect('yawSysCC.cost', 'ncc.yaw_system_cost')
    assembly.connect('ncc.cost', 'cost')

@implement_base(BaseSubAssemblyCostAggregator)
class FullTowerCostAggregator(Component):
    """ Full tower cost aggregator to aggregate costs of individual tower components.    """

    # variables
    tower_cost = Float(iotype='in', units='USD', desc='component cost')
    
    # returns
    cost = Float(iotype='out', units='USD', desc='component cost')    

@implement_base(BaseSubAssemblyCostModel)
class FullTowerCostModel(Assembly):
    """ Full tower cost sub-assembly for bringing together individual tower component cost models.    """

    # returns
    cost = Float(iotype='out', units='USD', desc='component cost')    

def configure_full_twcc(assembly):
    """ Configure method for a detailed tower cost model including cost models for each major tower system component.    """

    assembly.add('towerCC', BaseComponentCostModel())
    assembly.add('twrcc', FullTowerCostAggregator())

    assembly.driver.workflow.add(['towerCC', 'twrcc'])
    
    assembly.connect('towerCC.cost', 'twrcc.tower_cost')
    assembly.connect('twrcc.cost', 'cost')

# Full Turbine Cost Model
@implement_base(BaseTCCAggregator)
class FullTCCAggregator(Component):
    """ Full turbine capital cost aggregator for doing some auxiliary cost calculations needed to get a full wind turbine cost.  It assume sub-models for rotor, nacelle and tower cost.    """

    # Variables
    rotor_cost = Float(iotype='in', units='USD', desc='rotor cost')
    nacelle_cost = Float(iotype='in', units='USD', desc='nacelle cost')
    tower_cost = Float(iotype='in', units='USD', desc='tower cost')

    # Outputs
    turbine_cost = Float(iotype='out', desc='Overall wind turbine capial costs including transportation costs')

@implement_base(ExtendedTurbineCostModel)
class FullTurbineCostModel(Assembly):
    """ Full turbine capital cost assembly for coupling models to get a full wind turbine cost.    """

    # Outputs
    turbine_cost = Float(iotype='out', desc='Overall wind turbine capial costs including transportation costs')

def configure_full_tcc(assembly):
    """ full configure method for a turbine capital cost assembly for coupling models to get a full wind turbine cost.  It replaces cost models for the rotor, nacelle and tower with full sub-assembly cost models.    """

    configure_extended_tcc(assembly)
    
    assembly.replace('rotorCC', FullRotorCostModel())
    assembly.replace('nacelleCC', FullNacelleCostModel())
    assembly.replace('towerCC', FullTowerCostModel())
    assembly.replace('tcc', FullTCCAggregator())