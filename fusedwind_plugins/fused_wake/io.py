#__all__ = ['fused_wake']
from openmdao.main.api import Component, VariableTree
from openmdao.lib.datatypes.api import Float, Array, Slot

############## IO Definitions ##########################################################


class GenericWindTurbineVT(VariableTree):
    hub_height = Float()
    rotor_diameter = Float()

class GenericWindTurbinePowerCurveVT(GenericWindTurbineVT):
    hub_height = Float()
    rotor_diameter = Float()
    power_curve = Array(desc='The power curve of the wind turbine')
    c_t_curve = Array(desc='The thrust coefficient curve of the wind turbine')


class GenericWindTurbine(Component):
    wt_desc = Slot(iotype='in')
    hub_wind_speed = Float(iotype='in')
    power = Float(0.0, iotype='out', desc='The wind turbine power')
    thrust = Float(0.0, iotype='out', desc='The wind turbine thrust')
    c_t = Float(0.0, iotype='out', desc='The wind turbine thrust coefficient')    
