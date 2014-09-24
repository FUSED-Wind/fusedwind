
import unittest
from fusedwind.interface import base, _implement_base, implement_base, FUSEDAssembly
from openmdao.main.datatypes.api import Float, Slot
from openmdao.main.api import Component, Assembly

class FrameworkTest(unittest.TestCase):
    def testImplements(self):
        for cls_type in [Component, Assembly]:
            @base
            class BaseClass1(cls_type):
                vi1 = Float(iotype='in')
                vi2 = Float(iotype='in')
                vo1 = Float(iotype='out')

            @_implement_base(BaseClass1)
            class MyClass(cls_type):    
                vi1 = Float(iotype='in')
                vi2 = Float(iotype='in')
                vo1 = Float(iotype='out')

            @base
            class BaseClass2(cls_type):
                vi3 = Float(iotype='in')
                vi4 = Float(iotype='in')
                vo2 = Float(iotype='out')


            @implement_base(BaseClass1, BaseClass2)
            class MyClass(cls_type):
                vi1 = Float(iotype='in')
                vi2 = Float(iotype='in')
                vi3 = Float(iotype='in')
                vi4 = Float(iotype='in')

                vo1 = Float(iotype='out')
                vo2 = Float(iotype='out')

            myinst = MyClass()


    def testMixingCompAss(self):
        """Mixing components and assemblies"""

        @base
        class BaseClass1(Component):
            vi1 = Float(iotype='in')
            vi2 = Float(iotype='in')
            vo1 = Float(iotype='out')

        @base
        class BaseClass2(Component):
            vi3 = Float(iotype='in')
            vi4 = Float(iotype='in')
            vo2 = Float(iotype='out')


        @implement_base(BaseClass1, BaseClass2)
        class MyClass(Assembly):
            vi1 = Float(iotype='in')
            vi2 = Float(iotype='in')
            vi3 = Float(iotype='in')
            vi4 = Float(iotype='in')

            vo1 = Float(iotype='out')
            vo2 = Float(iotype='out')

        myinst = MyClass()


    def testExtendingIOs(self):
        """Extending the number of inputs and outpus"""

        @base
        class BaseClass1(Component):
            vi1 = Float(iotype='in')
            vi2 = Float(iotype='in')
            vo1 = Float(iotype='out')

        @implement_base(BaseClass1)
        class MyClass(Component):
            vi1 = Float(iotype='in')
            vi2 = Float(iotype='in')
            vi3 = Float(iotype='in')
            vi4 = Float(iotype='in')

            vo1 = Float(iotype='out')
            vo2 = Float(iotype='out')

        myinst = MyClass()


    def testExternalConfigure(self):
        """Testing having external configure functions"""

        @base
        class BaseClass1(Component):
            vi1 = Float(iotype='in')
            vi2 = Float(iotype='in')
            vo1 = Float(iotype='out')


        @implement_base(BaseClass1)
        class C1(Component):
            vi1 = Float(iotype='in')
            vi2 = Float(iotype='in')
            vo1 = Float(iotype='out')

            def execute(self):
                self.vo1 = self.vi1 + self.vi2

        def configure_C1(self):
            self.add('c1', C1())
            self.connect('vi1', 'c1.vi1')
            self.connect('vi2', 'c1.vi2')
            self.connect('c1.vo1', 'vo1')
            self.driver.workflow.add('c1')

        @base
        class BaseClass2(Component):
            vi1 = Float(iotype='in')
            vi3 = Float(iotype='in')
            vo2 = Float(iotype='out')

        @implement_base(BaseClass2)
        class C2(Component):
            vi1 = Float(iotype='in')
            vi3 = Float(iotype='in')
            vo2 = Float(iotype='out')

            def execute(self):
                self.vo2 = self.vi1 * self.vi3

        def configure_C2(self):
            self.add('c2', C2())
            self.connect('vi1', 'c2.vi1')
            self.connect('vi3', 'c2.vi3')
            self.connect('c2.vo2', 'vo2')
            self.driver.workflow.add('c2')


        @implement_base(BaseClass1, BaseClass2)
        class MyClass(Assembly):
            """Assembly that nests a C1 and C2 component 
            and complies to both base classes I/Os
            """
            vi1 = Float(iotype='in')
            vi2 = Float(iotype='in')
            vi3 = Float(iotype='in')            

            vo1 = Float(iotype='out', desc='vi1+vi2')
            vo2 = Float(iotype='out', desc='vi1*vi3')

            def configure(self):
                configure_C1(self)
                configure_C2(self)                


        from random import random
        myinst = MyClass()
        myinst.vi1 = random()
        myinst.vi2 = random()
        myinst.vi3 = random()   
        myinst.run()
        self.assertEqual(myinst.vo1, myinst.vi1 + myinst.vi2) 
        self.assertEqual(myinst.vo2, myinst.vi1 * myinst.vi3) 


    def test_implement_with_init(self):
        """test for implement_base for classes that have an __init__ method"""

        @base
        class BaseClass1(Component):
            vi1 = Float(iotype='in')
            vi2 = Float(iotype='in')
            vo1 = Float(iotype='out')

        @implement_base(BaseClass1)
        class MyClass(Component):
            vi1 = Float(iotype='in')
            vi2 = Float(iotype='in')
            vi3 = Float(iotype='in')
            vo1 = Float(iotype='out')

            def __init__(self):
                super(MyClass, self).__init__()

                pass

            def execute(self):

                pass

        myinst = MyClass()

    def test_replace(self):
        @base
        class DummyC0(Component):
            input = Float(iotype='in')
            output = Float(iotype='out')
            #output2 = Float(iotype='out')    

        @implement_base(DummyC0)
        class DummyC1(Component):
            
            input = Float(iotype='in')
            output = Float(iotype='out')

            def execute(self):
                self.output = self.input **2.0

        @implement_base(DummyC0)
        class DummyC2(DummyC1):
            output2 = Float(iotype='out')    
            def execute(self):
                self.output = self.input **4.0

        class DummyC3(DummyC1):
            def execute(self):
                self.output = self.input **8.0

        @implement_base(DummyC0)        
        class DummyA(FUSEDAssembly):
            
            input = Float(iotype='in')
            output = Float(iotype='out')
            
            def configure(self):
                self.add_default('c', DummyC0())
                self.driver.workflow.add('c')
                self.connect('input', 'c.input')
                self.connect('c.output', 'output')            

        DA = DummyA()
        DA.add('c', DummyC2())
        DA.input = 2.
        DA.run()
        assert DA.input == 2.0 and DA.output == 2.0**4., 'C2 has not been added properly'

        DA.replace('c', DummyC3())
        DA.run()
        assert DA.input == 2.0 and DA.output == 2.0**8., 'C3 has not been added properly'


if __name__ == "__main__":
    unittest.main()             
