# Turbine Cost Model Framework
# KLD 11/14/2013

from openmdao.lib.datatypes.api import Float, Int
from openmdao.main.api import Component, Assembly

##############################################################
# Turbine Cost Models

# ------------------------------------------------------------
# Basic Turbine Captial Costs

# Basic Turbine Cost Model Building Blocks
class BaseComponentCostModel(Component):
    """
    TODO: docstring
    """

    # Outputs
    cost = Float(0.0, iotype='out', desc='Overall wind tower capial costs including transportation costs')

class BaseSubAssemblyCostModel(Assembly):
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

# Basic Turbine Cost Model
class BaseTurbineCapitalCostModel(Assembly):
    """
    Framework for a turbine capital cost model
    """

    def configure(self):
       
       self.add('tcc', BaseTCCAggregator())
       
       self.driver.workflow.add(['tcc'])

       self.create_passthrough('tcc.turbine_cost')

# ------------------------------------------------------------
# Extended Turbine Capital Costs

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

# Extended Turbine Capital Cost Model Includes sub-assembly cost aggregation
class ExtendedTurbineCapitalCostModel(BaseTurbineCapitalCostModel):

    """
    TODO: docstring
    """

    def configure(self):
    
        super(ExtendedTurbineCapitalCostModel, self).configure()

        self.add('rotorCC', BaseSubAssemblyCostModel())
        self.add('nacelleCC', BaseSubAssemblyCostModel())
        self.add('towerCC', BaseSubAssemblyCostModel())
        self.replace('tcc', FullTCCAggregator())

        self.driver.workflow.add(['rotorCC', 'nacelleCC', 'towerCC'])

        self.connect('rotorCC.cost', 'tcc.rotor_cost')
        self.connect('nacelleCC.cost', 'tcc.nacelle_cost')
        self.connect('towerCC.cost', 'tcc.tower_cost')

# ------------------------------------------------------------
# Full Turbine Capital Costs

# Full Sub-Assembly Cost Models
class FullRotorCostAggregator(Component):

    # variables
    blade_cost = Float(iotype='in', units='USD', desc='individual blade cost')
    hub_system_cost = Float(iotype='in', units='USD', desc='cost for hub system')
    
    # parameters
    blade_number = Int(iotype='in', desc='number of rotor blades')
    
    # returns
    cost = Float(iotype='out', units='USD', desc='overall rotor cost')

class FullHubSystemCostAggregator(Component):

    # variables
    hub_cost = Float(iotype='in', units='USD', desc='hub component cost')
    pitch_system_cost = Float(iotype='in', units='USD', desc='pitch system cost')
    spinner_cost = Float(iotype='in', units='USD', desc='spinner component cost')
    
    # returns
    cost = Float(iotype='out', units='USD', desc='overall hub system cost')    

class FullRotorCostModel(BaseSubAssemblyCostModel):
    """
    TODO: docstring
    """

    # parameters
    blade_number = Int(iotype='in', desc='number of rotor blades')

    def configure(self):
        
        super(FullRotorCostModel, self).configure()
        
        self.add('bladeCC', BaseComponentCostModel())
        self.add('hubCC', BaseComponentCostModel())
        self.add('pitchSysCC', BaseComponentCostModel())
        self.add('spinnerCC', BaseComponentCostModel())
        self.add('hubSysCC', FullHubSystemCostAggregator())
        self.add('rcc', FullRotorCostAggregator())

        self.driver.workflow.add(['hubCC', 'pitchSysCC', 'spinnerCC', 'hubSysCC', 'bladeCC', 'rcc'])
        
        self.connect('blade_number', 'rcc.blade_number')
        self.connect('hubCC.cost', 'hubSysCC.hub_cost')
        self.connect('pitchSysCC.cost', 'hubSysCC.pitch_system_cost')
        self.connect('spinnerCC.cost', 'hubSysCC.spinner_cost')
        self.connect('hubSysCC.cost', 'rcc.hub_system_cost')
        self.connect('bladeCC.cost', 'rcc.blade_cost')
        self.connect('rcc.cost', 'cost')

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

class FullNacelleCostModel(BaseSubAssemblyCostModel):
    """
    TODO: docstring
    """

    def configure(self):
        
        super(FullNacelleCostModel, self).configure()
        
        self.add('lssCC', BaseComponentCostModel())
        self.add('bearingsCC', BaseComponentCostModel())
        self.add('gearboxCC', BaseComponentCostModel())
        self.add('hssCC', BaseComponentCostModel())
        self.add('generatorCC', BaseComponentCostModel())
        self.add('bedplateCC', BaseComponentCostModel())
        self.add('yawSysCC', BaseComponentCostModel())
        self.add('ncc', FullNacelleCostAggregator())

        self.driver.workflow.add(['lssCC', 'bearingsCC', 'gearboxCC', 'hssCC', 'generatorCC', 'bedplateCC', 'yawSysCC', 'ncc'])
        
        self.connect('lssCC.cost', 'ncc.lss_cost')
        self.connect('bearingsCC.cost', 'ncc.bearings_cost')
        self.connect('gearboxCC.cost', 'ncc.gearbox_cost')
        self.connect('hssCC.cost', 'ncc.hss_cost')
        self.connect('generatorCC.cost', 'ncc.generator_cost')
        self.connect('bedplateCC.cost', 'ncc.bedplate_cost')
        self.connect('yawSysCC.cost', 'ncc.yaw_system_cost')
        self.connect('ncc.cost', 'cost')

class FullTowerCostAggregator(Component):
    """
    TODO: docstring
    """

    # variables
    tower_cost = Float(iotype='in', units='USD', desc='component cost')
    
    # returns
    cost = Float(iotype='out', units='USD', desc='component cost')    

class FullTowerCostModel(BaseSubAssemblyCostModel):
    """
    TODO: docstring
    """

    def configure(self):
        
        super(FullTowerCostModel, self).configure()
        
        self.add('towerCC', BaseComponentCostModel())
        self.add('twrcc', FullTowerCostAggregator())

        self.driver.workflow.add(['towerCC', 'twrcc'])
        
        self.connect('towerCC.cost', 'twrcc.tower_cost')
        self.connect('twrcc.cost', 'cost')

# Full Turbine Cost Model
class FullTurbineCapitalCostModel(ExtendedTurbineCapitalCostModel):

    """
    TODO: docstring
    """

    def configure(self):
    
        super(FullTurbineCapitalCostModel, self).configure()
        
        self.replace('rotorCC', FullRotorCostModel())
        self.replace('nacelleCC', FullNacelleCostModel())
        self.replace('towerCC', FullTowerCostModel())


if __name__=="__main__":

    pass