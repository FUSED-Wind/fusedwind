
import unittest
from openmdao.main.datatypes.api import Float, Slot, Array, List
from openmdao.main.api import Component, Assembly, VariableTree
from fusedwind.fused_helper import init_container
import numpy as np


class test_init_container(unittest.TestCase):
    def test_list_to_array(self):
        """Test that the container array can be intialized with a list"""
        class Arr(VariableTree):
            a = Array()

        inputs = {'a': range(10)}
        obj = Arr()

        init_container(obj, **inputs)

    def test_array_to_list(self):
        """Test that the container list can be intialized with an array"""
        class Arr(VariableTree):
            a = List()

        inputs = {'a': np.arange(10)}
        obj = Arr()

        init_container(obj, **inputs)




if __name__ == "__main__":
    unittest.main()        		