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

    # Outputs
    cost = Float(0.0, iotype='out', desc='Overall wind turbine component capial costs excluding transportation costs')

@base
class BaseSubAssemblyCostModel(Assembly):

    # Outputs
    cost = Float(0.0, iotype='out', desc='Overall wind sub-assembly capial costs including transportation costs')

@base
class BaseSubAssemblyCostAggregator(Component):

    # Outputs
    cost = Float(0.0, iotype='out', desc='Overall wind sub-assembly capial costs including transportation costs')

@base
class BaseTCCAggregator(Component):

    # Outputs
    turbine_cost = Float(0.0, iotype='out', desc='Overall wind turbine capial costs including transportation costs')

# Basic Turbine _cost Model
@base
class BaseTurbineCostModel(Assembly):
    """
    Framework for a turbine capital cost model
    """

    # Outputs
    turbine_cost = Float(0.0, iotype='out', desc='Overall wind turbine capial costs including transportation costs')

def configure_base_tcc(assembly):
   
   assembly.add('tcc', BaseTCCAggregator())
   
   assembly.driver.workflow.add(['tcc'])

   assembly.connect('tcc.turbine_cost','turbine_cost')

# ------------------------------------------------------------
# Extended Turbine Capital Costs
@implement_base(BaseTCCAggregator)
class ExtendedTCCAggregator(Component):

    # Variables
    rotor_cost = Float(iotype='in', units='USD', desc='rotor cost')
    nacelle_cost = Float(iotype='in', units='USD', desc='nacelle cost')
    tower_cost = Float(iotype='in', units='USD', desc='tower cost')

    # Outputs
    turbine_cost = Float(0.0, iotype='out', desc='Overall wind turbine capial costs including transportation costs')

# Extended Turbine Capital _cost Model Includes sub-assembly cost aggregation
@implement_base(BaseTurbineCostModel)
class ExtendedTurbineCostModel(Assembly):

    # Outputs
    turbine_cost = Float(0.0, iotype='out', desc='Overall wind turbine capial costs including transportation costs')

def configure_extended_tcc(assembly):

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

    # variables
    blade_cost = Float(iotype='in', units='USD', desc='individual blade cost')
    hub_system_cost = Float(iotype='in', units='USD', desc='cost for hub system')
    
    # parameters
    blade_number = Int(iotype='in', desc='number of rotor blades')
    
    # returns
    cost = Float(iotype='out', units='USD', desc='overall rotor cost')

@implement_base(BaseSubAssemblyCostAggregator)
class FullHubSystemCostAggregator(Component):

    # variables
    hub_cost = Float(iotype='in', units='USD', desc='hub component cost')
    pitch_system_cost = Float(iotype='in', units='USD', desc='pitch system cost')
    spinner_cost = Float(iotype='in', units='USD', desc='spinner component cost')
    
    # returns
    cost = Float(iotype='out', units='USD', desc='overall hub system cost')    

@implement_base(BaseSubAssemblyCostModel)
class FullRotorCostModel(BaseSubAssemblyCostModel):

    # parameters
    blade_number = Int(iotype='in', desc='number of rotor blades')

    # Outputs
    cost = Float(0.0, iotype='out', desc='Overall wind sub-assembly capial costs including transportation costs')

def configure_full_rcc(assembly):
    
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

    # returns
    cost = Float(iotype='out', units='USD', desc='component cost')

def configure_full_ncc(assembly):
    
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

    # variables
    tower_cost = Float(iotype='in', units='USD', desc='component cost')
    
    # returns
    cost = Float(iotype='out', units='USD', desc='component cost')    

@implement_base(BaseSubAssemblyCostModel)
class FullTowerCostModel(Assembly):

    # returns
    cost = Float(iotype='out', units='USD', desc='component cost')    

def configure_full_twcc(assembly):
    
    assembly.add('towerCC', BaseComponentCostModel())
    assembly.add('twrcc', FullTowerCostAggregator())

    assembly.driver.workflow.add(['towerCC', 'twrcc'])
    
    assembly.connect('towerCC.cost', 'twrcc.tower_cost')
    assembly.connect('twrcc.cost', 'cost')

# Full Turbine Cost Model
@implement_base(BaseTCCAggregator)
class FullTCCAggregator(Component):

    # Variables
    rotor_cost = Float(iotype='in', units='USD', desc='rotor cost')
    nacelle_cost = Float(iotype='in', units='USD', desc='nacelle cost')
    tower_cost = Float(iotype='in', units='USD', desc='tower cost')

    # Outputs
    turbine_cost = Float(0.0, iotype='out', desc='Overall wind turbine capial costs including transportation costs')

@implement_base(ExtendedTurbineCostModel)
class FullTurbineCostModel(Assembly):

    # Outputs
    turbine_cost = Float(0.0, iotype='out', desc='Overall wind turbine capial costs including transportation costs')

def configure_full_tcc(assembly):

    configure_extended_tcc(assembly)
    
    assembly.replace('rotorCC', FullRotorCostModel())
    assembly.replace('nacelleCC', FullNacelleCostModel())
    assembly.replace('towerCC', FullTowerCostModel())


if __name__=="__main__":

    pass