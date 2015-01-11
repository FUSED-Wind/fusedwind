
from openmdao.main.api import VariableTree, Component
from openmdao.lib.datatypes.api import Int, Float, Array, List, Str, Enum, Bool, VarTree, Slot


class TurbineEnvironmentVT(VariableTree):

    vhub = Float(desc='Hub-height velocity')
    direction = Float(desc='Incident wind direction')
    density = Float(1.225, desc='air density')
    viscosity = Float(1.78405e-5, desc='air viscosity')
    ti = Float(0., desc='Turbulence intensity in percent')
    inflow_type = Enum('constant', ('constant','log','powerlaw','linear','user'), desc='shear type')
    shear_exp = Float(0., iotype='in', desc='Shear exponent (when applicaple)') 
    kappa = Float(0.4, iotype='in', desc='Von Karman constant')
    z0 = Float(0.111, iotype='in', desc='Roughness length')


class OffshoreTurbineEnvironmentVT(TurbineEnvironmentVT):

    Hs = Float(units='m', desc='Significant wave height')
    Tp = Float(units='s', desc='Peak wave period')
    WaveDir = Float(units='deg', desc='Direction of waves relative to turbine')