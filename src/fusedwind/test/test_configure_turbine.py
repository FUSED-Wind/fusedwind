
import numpy as np
import unittest
import glob
import os

from openmdao.main.api import Assembly

from fusedwind.turbine.turbine_vt import create_turbine, configure_turbine


def test_basic_configure():

    top = Assembly()

    wt = create_turbine(top)
    configure_turbine(wt)
    wt.tower_height = 115.63
    wt.hub_height = 119.0
    wt.towertop_height = 2.75
    wt.shaft_length = 7.1
    wt.tilt_angle = 5.0
    wt.cone_angle = -2.5
    wt.hub_radius = 2.8
    wt.blade_length = 86.366
    wt.rotor_diameter = 178.332
    c = wt.set_machine_type('VarSpeedVarPitch')
    c.vIn = 3.
    c.vOut = 25.
    c.minOmega = 6.
    c.maxOmega = 9.6
    c.minPitch = 0.

    return top


class TestConfigureTurbine(unittest.TestCase):

    def setUp(self):

        pass

    def test_configure(self):

        top = test_basic_configure()


if __name__ == '__main__':

    unittest.main()

