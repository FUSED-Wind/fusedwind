# Turbine _cost Model Framework
# KLD 11/14/2013

from openmdao.lib.datatypes.api import Float, Int
from openmdao.main.api import Component, Assembly

##############################################################
# Turbine _cost Models

# ------------------------------------------------------------
# Basic Turbine Captial _costs

# Basic Turbine _cost Model Building Blocks
class BaseComponent_costModel(Component):
    """
    TODO: docstring
    """

    # Outputs
    cost = Float(0.0, iotype='out', desc='Overall wind tower capial costs including transportation costs')

class BaseSubAssembly_costModel(Assembly):
    """
    TODO: docstring
    """

    # Outputs
    cost = Float(0.0, iotype='out', desc='Overall wind sub-assembly capial costs including transportation costs')

class BaseTCCAggregator(Component):
    """
    TODO: docstring
    """

    # Outputs
    turbine_cost = Float(0.0, iotype='out', desc='Overall wind turbine capial costs including transportation costs')

# Basic Turbine _cost Model
class BaseTurbineCapitalCostModel(Assembly):
    """
    Framework for a turbine capital cost model
    """

    def configure(self):
       
       self.add('tcc', BaseTCCAggregator())
       
       self.driver.workflow.add(['tcc'])

       self.create_passthrough('tcc.turbine_cost')

# ------------------------------------------------------------
# Extended Turbine Capital _costs

class FullTCCAggregator(BaseTCCAggregator):
    """
    TODO: docstring
    """

    # Variables
    rotor_cost = Float(iotype='in', units='USD', desc='rotor cost')
    nacelle_cost = Float(iotype='in', units='USD', desc='nacelle cost')
    tower_cost = Float(iotype='in', units='USD', desc='tower cost')

    def __init__(self):
      
        super(FullTCCAggregator, self).__init__()

# Extended Turbine Capital _cost Model Includes sub-assembly cost aggregation
class ExtendedTurbineCapitalCostModel(BaseTurbineCapitalCostModel):

    """
    TODO: docstring
    """

    def configure(self):
    
        super(ExtendedTurbineCapitalCostModel, self).configure()

        self.add('rotorCC', BaseSubAssembly_costModel())
        self.add('nacelleCC', BaseSubAssembly_costModel())
        self.add('towerCC', BaseSubAssembly_costModel())
        self.replace('tcc', FullTCCAggregator())

        self.driver.workflow.add(['rotorCC', 'nacelleCC', 'towerCC'])

        self.connect('rotorCC.cost', 'tcc.rotor_cost')
        self.connect('nacelleCC.cost', 'tcc.nacelle_cost')
        self.connect('towerCC.cost', 'tcc.tower_cost')

# ------------------------------------------------------------
# Full Turbine Capital _costs

# Full Sub-Assembly _cost Models
class FullRotor_costAggregator(Component):

    # variables
    blade_cost = Float(iotype='in', units='USD', desc='individual blade cost')
    hub_system_cost = Float(iotype='in', units='USD', desc='cost for hub system')
    
    # parameters
    blade_number = Int(iotype='in', desc='number of rotor blades')
    
    # returns
    cost = Float(iotype='out', units='USD', desc='overall rotor cost')

class FullHubSystem_costAggregator(Component):

    # variables
    hub_cost = Float(iotype='in', units='USD', desc='hub component cost')
    pitch_system_cost = Float(iotype='in', units='USD', desc='pitch system cost')
    spinner_cost = Float(iotype='in', units='USD', desc='spinner component cost')
    
    # returns
    cost = Float(iotype='out', units='USD', desc='overall hub system cost')    

class FullRotor_costModel(BaseSubAssembly_costModel):
    """
    TODO: docstring
    """

    # parameters
    blade_number = Int(iotype='in', desc='number of rotor blades')

    def configure(self):
        
        super(FullRotor_costModel, self).configure()
        
        self.add('bladeCC', BaseComponent_costModel())
        self.add('hubCC', BaseComponent_costModel())
        self.add('pitchSysCC', BaseComponent_costModel())
        self.add('spinnerCC', BaseComponent_costModel())
        self.add('hubSysCC', FullHubSystem_costAggregator())
        self.add('rcc', FullRotor_costAggregator())

        self.driver.workflow.add(['hubCC', 'pitchSysCC', 'spinnerCC', 'hubSysCC', 'bladeCC', 'rcc'])
        
        self.connect('blade_number', 'rcc.blade_number')
        self.connect('hubCC.cost', 'hubSysCC.hub_cost')
        self.connect('pitchSysCC.cost', 'hubSysCC.pitch_system_cost')
        self.connect('spinnerCC.cost', 'hubSysCC.spinner_cost')
        self.connect('hubSysCC.cost', 'rcc.hub_system_cost')
        self.connect('bladeCC.cost', 'rcc.blade_cost')
        self.connect('rcc.cost', 'cost')

class FullNacelle_costAggregator(Component):

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

class FullNacelle_costModel(BaseSubAssembly_costModel):
    """
    TODO: docstring
    """

    def configure(self):
        
        super(FullNacelle_costModel, self).configure()
        
        self.add('lssCC', BaseComponent_costModel())
        self.add('bearingsCC', BaseComponent_costModel())
        self.add('gearboxCC', BaseComponent_costModel())
        self.add('hssCC', BaseComponent_costModel())
        self.add('generatorCC', BaseComponent_costModel())
        self.add('bedplateCC', BaseComponent_costModel())
        self.add('yawSysCC', BaseComponent_costModel())
        self.add('ncc', FullNacelle_costAggregator())

        self.driver.workflow.add(['lssCC', 'bearingsCC', 'gearboxCC', 'hssCC', 'generatorCC', 'bedplateCC', 'yawSysCC', 'ncc'])
        
        self.connect('lssCC.cost', 'ncc.lss_cost')
        self.connect('bearingsCC.cost', 'ncc.bearings_cost')
        self.connect('gearboxCC.cost', 'ncc.gearbox_cost')
        self.connect('hssCC.cost', 'ncc.hss_cost')
        self.connect('generatorCC.cost', 'ncc.generator_cost')
        self.connect('bedplateCC.cost', 'ncc.bedplate_cost')
        self.connect('yawSysCC.cost', 'ncc.yaw_system_cost')
        self.connect('ncc.cost', 'cost')

class FullTower_costAggregator(Component):
    """
    TODO: docstring
    """

    # variables
    tower_cost = Float(iotype='in', units='USD', desc='component cost')
    
    # returns
    cost = Float(iotype='out', units='USD', desc='component cost')    

class FullTower_costModel(BaseSubAssembly_costModel):
    """
    TODO: docstring
    """

    def configure(self):
        
        super(FullTower_costModel, self).configure()
        
        self.add('towerCC', BaseComponent_costModel())
        self.add('twrcc', FullTower_costAggregator())

        self.driver.workflow.add(['towerCC', 'twrcc'])
        
        self.connect('towerCC.cost', 'twrcc.tower_cost')
        self.connect('twrcc.cost', 'cost')

# Full Turbine _cost Model
class FullTurbineCapitalCostModel(ExtendedTurbineCapitalCostModel):

    """
    TODO: docstring
    """

    def configure(self):
    
        super(FullTurbineCapitalCostModel, self).configure()
        
        self.replace('rotorCC', FullRotor_costModel())
        self.replace('nacelleCC', FullNacelle_costModel())
        self.replace('towerCC', FullTower_costModel())


if __name__=="__main__":

    pass