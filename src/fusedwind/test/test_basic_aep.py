#!/usr/bin/env python
# encoding: utf-8
"""
test_Plant_EnergySE.py

Created by Katherine Dykes on 2014-01-07.
Copyright (c) NREL. All rights reserved.
"""


import unittest
import numpy as np
from fusedwind.lib.utilities import check_gradient_unit_test
from fusedwind.plant_flow.basic_aep import aep_component, WeibullCDF, RayleighCDF, BasicAEP


# Basic AEP model tests

class Test_WeibullCDF(unittest.TestCase):

    def setUp(self):

        self.cdf = WeibullCDF()

        self.cdf.x = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0,
                 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0, 21.0, 22.0, 23.0, 24.0, 25.0, 26.0]

        self.cdf.A = 8.35
        self.cdf.k = 2.15

    def test_functionality(self):
        
        self.cdf.run()
        
        F = np.array([0.01037793,  0.04524528,  0.10480121,  0.18575653,  0.28252447,  0.38820584,
              0.49562699,  0.59829918,  0.69114560,  0.77089646,  0.83613421,  0.88704769,
              0.92500346,  0.95205646,  0.97050303,  0.98254137,  0.99006279,  0.99456267,
              0.99714093,  0.99855575,  0.99929934,  0.99967365,  0.9998541,   0.99993741,
              0.99997424,  0.99998983])
        
        self.assertEqual(self.cdf.F.all(), F.all())

    def test_gradient(self):

        check_gradient_unit_test(self, self.cdf, display=False)

class Test_RayleighCDF(unittest.TestCase):

    def setUp(self):

        self.cdf = RayleighCDF()
        self.cdf.x = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0,
                 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0, 21.0, 22.0, 23.0, 24.0, 25.0, 26.0]
        self.cdf.xbar = 8.35

    def test_functionality(self):
        
        self.cdf.run()
      
        F = np.array([0.01120142,  0.04405846,  0.09641191,  0.16492529,  0.24543643,  0.33337438,
                      0.42418386,  0.51370329,  0.59845474,  0.67582215,  0.74411323,  0.80251778,
                      0.85098711,  0.89006516,  0.92070195,  0.94407508,  0.96143762,  0.97400212,
                      0.98286327,  0.98895582,  0.99304088,  0.99571263,  0.99741748,  0.99847906,
                      0.99912422,  0.99950695])
        
        self.assertEqual(self.cdf.F.all(), F.all())

    def test_gradient(self):

        check_gradient_unit_test(self, self.cdf, display=False)

class Test_aep_component(unittest.TestCase):

    def setUp(self):

        self.aep = aep_component()
        self.aep.power_curve = [
            0.0, 0.0, 0.0, 187.0, 350.0, 658.30, 1087.4, 1658.3, 2391.5, 3307.0, 4415.70,
            5000.0, 5000.0, 5000.0, 5000.0, 5000.0, 5000.0, 5000.0, 5000.0, 5000.0, 5000.0, 5000.0, 5000.0,
            5000.0, 5000.0, 0.0]
        self.aep.CDF_V = [
            0.010, 0.045, 0.105, 0.186, 0.283, 0.388, 0.496, 0.598, 0.691, 0.771, 0.836,
            0.887, 0.925, 0.952, 0.971, 0.983, 0.990, 0.995, 0.997, 0.999, 0.999, 1.000, 1.000,
            1.000, 1.000, 1.000]

    def test_functionality(self):
        
        self.aep.run()
        
        self.assertEqual(round(self.aep.net_aep,1), 1389470583.4)

    def test_gradient(self):

        check_gradient_unit_test(self, self.aep, step_size=1.0, tol=1e-5, display=False)

class TestBasicAEP(unittest.TestCase):

    def setUp(self):

        self.aep = BasicAEP()

        self.aep.AEP_one_turbine = 75.4
        self.aep.array_losses = 0.059
        self.aep.other_losses = 0.0
        self.aep.availability = 0.94
        self.aep.turbine_number = 100

    def test_functionality(self):
        
        self.aep.run()
        
        self.assertEqual(round(self.aep.net_aep,1), 6669.4)

    def test_gradient(self):

        check_gradient_unit_test(self, self.aep)

if __name__ == "__main__":
    unittest.main()
