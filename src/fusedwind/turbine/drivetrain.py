from openmdao.main.api import Assembly, Component
from openmdao.main.datatypes.api import Float, Bool, Int, Str, Array, Enum
from math import pi, log10, log
import numpy as np
import algopy

from fusedwind.interface import base

# Hub Base Class
@base
class HubBase(Assembly):

    # variables
    # no inputs specified since fidelity levels vary considerably

    # outputs
    hub_mass = Float(0.0, iotype='out', units='kg', desc='hub component mass')
    pitch_system_mass = Float(0.0, iotype='out', units='kg', desc='pitch system total mass')
    spinner_mass = Float(0.0, iotype='out', units='kg', desc='nose cone / spinner mass')

    hub_system_mass = Float(0.0, iotype='out', units='kg', desc='overall component mass')
    hub_system_cm = Array(iotype='out', desc='center of mass of the hub relative to tower to in yaw-aligned c.s.')
    hub_system_I = Array(iotype='out', desc='mass moments of Inertia of hub [Ixx, Iyy, Izz, Ixy, Ixz, Iyz] around its center of mass in yaw-aligned c.s.')

#Nacelle Base Class
@base
class NacelleBase(Assembly):

    # variables
    # no inputs specified since fidelity levels vary considerably

    # outputs
    low_speed_shaft_mass = Float(iotype='out', units='kg', desc='component mass')
    main_bearing_mass = Float(iotype='out', units='kg', desc='component mass')
    second_bearing_mass = Float(iotype='out', units='kg', desc='component mass')
    gearbox_mass = Float(iotype='out', units='kg', desc='component mass')
    high_speed_side_mass = Float(iotype='out', units='kg', desc='component mass')
    generator_mass = Float(iotype='out', units='kg', desc='component mass')
    bedplate_mass = Float(iotype='out', units='kg', desc='component mass')
    yaw_system_mass = Float(iotype='out', units='kg', desc='component mass')

    nacelle_mass = Float(iotype='out', units='kg', desc='nacelle mass')
    nacelle_cm = Array(iotype='out', units='m', desc='center of mass of nacelle from tower top in yaw-aligned coordinate system')
    nacelle_I = Array(iotype='out', units='kg*m**2', desc='mass moments of inertia for nacelle [Ixx, Iyy, Izz, Ixy, Ixz, Iyz] about its center of mass')