#!/usr/bin/env python
# encoding: utf-8
"""
test_FUSED_Cost.py

Created by Katherine Dykes on 2014-01-07.
Copyright (c) NREL. All rights reserved.
"""

import unittest
import numpy as np
from fusedwind.lib.utilities import check_gradient_unit_test
from fusedwind.examples.fused_cost_example import BaseFinancialAnalysis_Example, ExtendedFinancialAnalysis_Example

# Basic Financial Analysis model
class Test_BaseFinancialAnalysis(unittest.TestCase):

    def test_functionality(self):
        
        baseFinance = BaseFinancialAnalysis_Example()
        baseFinance.turbine_number = 100
        
        baseFinance.run()
        
        self.assertEqual(round(baseFinance.coe,4), 0.1655)

# Extended Financial Analysis model
class Test_ExtendedFinancialAnalysis(unittest.TestCase):

    def test_functionality(self):

        extendedFinance = ExtendedFinancialAnalysis_Example()
        extendedFinance.turbine_number = 100
        
        extendedFinance.run()
                
        self.assertEqual(round(extendedFinance.coe,4), 0.1655)

if __name__ == "__main__":
    unittest.main()
