import numpy as np
from openmdao.lib.datatypes.api import Int, Float, Array, List, Str, Enum
from fusedwind.lib.fusedvartree import FusedIOVariableTree


class WindTurbineVT(FusedIOVariableTree):
    name = Str(desc='Wind turbine name')
    orientation = Enum('upwind', ('upwind','downwind'))
    

class RotorVT(FusedIOVariableTree):

    hub_height = Float(desc='Hub height')
    nb = Int(desc='Number of blades')
    tilt_angle = Float(desc='Tilt angle')
    cone_angle = Float(desc='Cone angle')
    diameter = Float(desc='Rotor diameter')
    mass = Float(desc='Total mass')
    overhang = Float(desc='Rotor overhang')


class BladeVT(FusedIOVariableTree):

    length = Float(desc='blade length')
    mass = Float(desc='blade mass')
    I_x = Float(desc='first area moment of inertia')
    I_y = Float(desc='Second area moment of inertia')
    root_chord = Float(desc='Blade root chord')
    max_chord = Float(desc='Blade maximum chord')
    tip_chord = Float(desc='Blade tip chord')
    airfoils = List(desc='List of airfoil names used on blade')


class HubVT(FusedIOVariableTree):

    diameter = Float(desc='blade length')
    mass = Float(desc='blade mass')
    I_x = Float(desc='first area moment of inertia')
    I_y = Float(desc='Second area moment of inertia')
    CM = Array(np.zeros(3), desc='')


class NacelleVT(FusedIOVariableTree):

    mass = Float(desc='blade mass')
    I_x = Float(desc='first area moment of inertia')
    I_y = Float(desc='Second area moment of inertia')
    CM = Array(np.zeros(3), desc='')


class TowerVT(FusedIOVariableTree):

    height = Float(desc='Tower height')
    bottom_diameter = Float(desc='Tower bottom diameter')
    top_diameter = Float(desc='Tower bottom diameter')

