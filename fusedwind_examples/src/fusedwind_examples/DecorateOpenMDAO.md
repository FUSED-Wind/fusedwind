

    from openmdao.lib.drivers.api import CaseIteratorDriver
    from openmdao.main.api import Component, Assembly, VariableTree
    from openmdao.lib.datatypes.api import VarTree, Float, Slot, Array, Int, List
    from openmdao.lib.casehandlers.api import ListCaseIterator, ListCaseRecorder
    from openmdao.main.case import Case
    from numpy import arange
    from openmdao.main.api import set_as_top
    import re
    
    def_comp = Component()
    def_inputs = def_comp.list_inputs()
    def_outputs = def_comp.list_outputs()
    
    class openMDAOify(object):
        """Decorator that "monkey patch" a class to an OpenMDAO component.
        A class that contains an execute method is patched into an openmdao class 
        as an engine. The openmdao class is copying inputs to the engine, executing 
        the engine, and copying back the outputs to its own output parameters.
     
        Example:
        --------
        ```
                class A(object):
                    def execute(self):
                        self.var3 = self.var1 + self.var2
                        self.var4 = self.var1
    
                ## ...import OpenMDAO here...             
    
                @openMDAOify(A)
                class Ao(Component):
                    # Inputs
                    var1 = Float(0., iotype='in')
                    var2 = Float(0., iotype='in')
                    # Outputs    
                    var3 = Float(0., iotype='out')  
                    var4 = Float(0., iotype='out')    
        ```
        """
        def __init__(self, engine):
            self.engine = engine
    
        def __call__(self, cls):
            e = cls()
            inputs = [i for i in e.list_inputs() if i not in def_inputs]
            outputs = [i for i in e.list_outputs() if i not in def_outputs]
    
            class wrapped(cls):
                __engine = self.engine()
    
                def __copy_inputs(self):
                    for i in inputs:
                        setattr(self.__engine, i, getattr(self, i))
    
                def __copy_outputs(self):
                    for o in outputs:
                        setattr(self, o, getattr(self.__engine, o))
                        
                def execute(self):
                    #super(wrapped, self).execute()
                    self.__copy_inputs()
                    self.__engine.execute()
                    self.__copy_outputs()
                    
                def __call__(self, **kwargs):
                    """Running the component in partial function mode"""
                    for k,v in kwargs.iteritems():
                        if k in self.list_inputs():
                            setattr(self, k, v)
                    self.run()
                    return self                
                    
            wrapped.__doc__ = self.engine.__doc__
            wrapped.__name__ = cls.__name__        
            return wrapped       
    
        
    remove_spaces = lambda x: re.split('^[\s]*', x)[1] if x[0] == ' ' else x
    
    class openMDAO_io(object):
        """Decorator to add OpenMDAO input / output meta data to a class or a function
        Note that:
            - the order in which you document the outputs is assumed to be the same as the function outputs order.
            - The parameters should be on one line, and should all contain the word iotype.
            - iotype is used to filter the doc, so if it appears somewhere else it will create a bug.
            - The number of spaces before the variable name doesn't matter.
            
        Example:
        --------
        ```
                @openMDAO_io("" "
                var1 = Float(0., iotype='in')
                var2 = Float(0., iotype='in')
                var3 = Float(0., iotype='out')  
                var4 = Float(0., iotype='out')
                "" ")    
                def Af(var1, var2):
                    "" "doc of Af" ""
                    return var1 + var2, var1
        ```
        
        """
        def __init__(self, io_string):
            args = map(remove_spaces, filter(lambda x: len(x)>0, io_string.splitlines()))
            vars = [v.replace(' ','').split('=')[0] for v in args]
            getvarname = lambda x: x.replace(' ','').split('=')[0]
            getio = lambda x: x.split("iotype='")[1].split("'")[0]
            self.inputs = [getvarname(v) for v in args if getio(v)=='in']
            self.outputs = [getvarname(v) for v in args if getio(v)=='out']
            self.args = args
        
        def __call__(self, func):
            func.args = self.args
            func.inputs = self.inputs
            func.outputs = self.outputs        
            return func
            #return self.func(*args)   
    
    def openMDAO_docs(cls):
        """Decorator to add OpenMDAO input / output meta data to a class or a function from the doc string.
        Note that:
            - the order in which you document the outputs is assumed to be the same as the function outputs order.
            - The parameters should be on one line, and should all contain the word iotype.
            - iotype is used to filter the doc, so if it appears somewhere else it will create a bug.
            - The number of spaces before the variable name doesn't matter.
    
        
        Parameter:
        ----------
        - cls [class/function] The class/function to decorate
    
    
        Example:
        --------
        
        ```
                @openMDAO_docs
                def Af(var1, var2):
                    " ""doc of Af
    
                    OpenMDAO I/O
                    ------------
                    # Inputs
                    var1 = Float(0., iotype='in')   # <- it only keeps the lines that have "iotype" in it
                    var2 = Float(0., iotype='in')
                    # Outputs
                    var3 = Float(0., iotype='out')  # <- First output
                    var4 = Float(0., iotype='out')  # <- Second output
                    "" "    
                    return var1 + var2, var1    
        ```
        
        """
        args = map(remove_spaces, filter(lambda x: 'iotype' in x, cls.__doc__.splitlines()))
        getvarname = lambda x: x.replace(' ','').split('=')[0]
        getio = lambda x: x.split("iotype='")[1].split("'")[0]
        cls.inputs = [getvarname(v) for v in args if getio(v)=='in']
        cls.outputs = [getvarname(v) for v in args if getio(v)=='out']
        cls.args = args
        return cls
            
            
    def OpenMDAO_func(func, name=None, base='Component'):
        """Create an OpenMDAO component out of a normal function, with an `openMDAO_io` decorator
        The order in which the openmdao output variable is defined in the openMDAO_io decorator is 
        critical, as it is the same order than the function output.
        This is a very easy way to introduce untrackable bugs.
        
        
        Parameters:
        -----------
        - eng [class] The class to wrapp
        - name=None [str] The name of the newly created class. If None, it will invent one.
        - base=Component [str] The base class name the openMDAO component should inherit from        
        """
        ios = "\n    ".join(func.args)
        inputs = ", ".join([k+" = self."+k for k in func.inputs])
        outputs = ", ".join(["self."+k for k in func.outputs])    
        if not name:
            cls_name = func.__name__+'_OMDAO'
        else:
            cls_name = name
        new_class = """
    class {name}({base}):
        {ios}
        
        def execute(self):
            {outputs} = {fname}({inputs})
        """.format(base=base, ios=ios, inputs=inputs, outputs=outputs, fname=func.__name__, name=cls_name)
        print '-------- New Class -------------'
        print new_class
        print '--------------------------------' 
        exec(new_class)
        cls = eval(cls_name)
        cls.__doc__ = func.__doc__    
        return cls
    
    def OpenMDAO_class(eng, name=None, base='Component'):
        """Create an OpenMDAO component out of a normal class, with an 
        `openMDAO_io` decorator, or an `openMDAO_doc` decorator.
        
        Parameters:
        -----------
        - eng [class] The class to wrapp
        - name=None [str] The name of the newly created class. If None, it will invent one.
        - base=Component [str] The base class name the openMDAO component should inherit from    
        """
        ios = "\n    ".join(eng.args)
        if not name:
            cls_name = eng.__name__+'_OMDAO'
        else:
            cls_name = name
        new_class = """
    @openMDAOify({engine_name})    
    class {name}({base}):
        {ios}
        
        """.format(base=base, ios=ios, engine_name=eng.__name__, name=cls_name)
        print '-------- New Class -------------'
        print new_class
        print '--------------------------------' 
        exec(new_class)
        cls = eval(cls_name)
        cls.__doc__ = eng.__doc__
        return cls
    
    
    def OpenMDAO_func2(func, outputs, attrib, name=None, base=Component):
        """Create an OpenMDAO component out of a normal function, with an `openMDAO_io` decorator.
        the outputs parameter is the list of the function output. the order is critical.
        
        Parameters:
        -----------
        - func [function] The function to wrapp
        - outputs [list(str)] An ordered list of outputs for the function
        - attrib [dict] A dictionary of openMDAO variables
        - name=None [str] The name of the newly created class. If None, it will invent one.
        - base=Component [class] The base class the openMDAO component should inherit from
        """
        if not name:
            cls_name = func.__name__+'_OMDAO'
        else:
            cls_name = name
        inputs = filter(lambda x: attrib[x].iotype=='in', attrib)
        #outputs = filter(lambda x: attrib[x].iotype=='out', attrib) <- don't use that, it doesn't work.
        def exec_func(self):
            outs = func(**dict([(k, getattr(self, k)) for k in inputs]))
            for k, v in zip(outputs, outs):
                setattr(self, k, v)
        cls = type(cls_name, (base,), attrib)
        cls.execute = exec_func
        return cls

Creating some standard test


    #from pprint import pprint
    
    test_dict = dict([('var3', 5.0),
                     ('var4', 3.0),
                     ('var1', 3.0),
                     ('var2', 2.0)])
    
    def testclass(Ao):
        print '--begin test--'
        print Ao.__name__
        print Ao.__doc__
        ao = Ao()
        ao.var1 = test_dict['var1']
        ao.var2 = test_dict['var2']
        ao.run()
        #pprint(list(ao.items()))
        for k, v in test_dict.iteritems():
            print k, v, '==', getattr(ao, k)
            assert getattr(ao, k) == v
        print ' -- OK -- '

### Creating an OpenMDAO object from combining a descriptive `Component` class and a normal class, using a monkey patch technique


    class A(object):
        """doc of A"""
        def execute(self):
            self.var3 = self.var1 + self.var2
            self.var4 = self.var1
    
    ## ...import OpenMDAO here...             
            
    @openMDAOify(A)
    class Ao(Component):
        """doc of Ao"""
        # Inputs
        var1 = Float(0., iotype='in')
        var2 = Float(0., iotype='in')
        # Outputs    
        var3 = Float(0., iotype='out')  
        var4 = Float(0., iotype='out')
    
    testclass(Ao)

    --begin test--
    Ao
    doc of A
    var4 3.0 == 3.0
    var1 3.0 == 3.0
    var3 5.0 == 5.0
    var2 2.0 == 2.0
     -- OK -- 


### Using multiple inheritance


    class A(object):
        """doc of A"""
        def execute(self):
            self.var3 = self.var1 + self.var2
            self.var4 = self.var1
    
    ## ...import OpenMDAO here...     
            
    # A should always come before Component        
    class Ao(A, Component):
        """doc of Ao"""
        # Inputs
        var1 = Float(0., iotype='in')
        var2 = Float(0., iotype='in')
        # Outputs
        var3 = Float(0., iotype='out')  
        var4 = Float(0., iotype='out')
    
    testclass(Ao)


    --begin test--
    Ao
    doc of Ao
    var4 3.0 == 3.0
    var1 3.0 == 3.0
    var3 5.0 == 5.0
    var2 2.0 == 2.0
     -- OK -- 


### Same thing using meta class generation


    class A(object):
        """doc of A"""
        def execute(self):
            self.var3 = self.var1 + self.var2
            self.var4 = self.var1
    
    ## ...import OpenMDAO here...     
    attribs = dict(
        var1 = Float(0., iotype='in'),
        var2 = Float(0., iotype='in'),
        var3 = Float(0., iotype='out'),  
        var4 = Float(0., iotype='out')
    )
    
    # A should always come before Component
    Ao = type('Ao1', (A, Component,), attribs)
    Ao.__doc__ = A.__doc__
    testclass(Ao)


    --begin test--
    Ao1
    doc of A
    var4 3.0 == 3.0
    var1 3.0 == 3.0
    var3 5.0 == 5.0
    var2 2.0 == 2.0
     -- OK -- 


### Creating an OpenMDAO object from a normal *function* (with a `openMDAO_io` decorator)


    @openMDAO_io("""
    var1 = Float(0., iotype='in')
    var2 = Float(0., iotype='in')
    var3 = Float(0., iotype='out')  
    var4 = Float(0., iotype='out')
    """)    
    def Af(var1, var2):
        """doc of Af"""
        return var1 + var2, var1
    
    ## ...import OpenMDAO here...     
    Afo = OpenMDAO_func(Af)
    testclass(Afo)

    -------- New Class -------------
    
    class Af_OMDAO(Component):
        var1 = Float(0., iotype='in')
        var2 = Float(0., iotype='in')
        var3 = Float(0., iotype='out')  
        var4 = Float(0., iotype='out')
        
        def execute(self):
            self.var3, self.var4 = Af(var1 = self.var1, var2 = self.var2)
        
    --------------------------------
    --begin test--
    Af_OMDAO
    doc of Af
    var4 3.0 == 3.0
    var1 3.0 == 3.0
    var3 5.0 == 5.0
    var2 2.0 == 2.0
     -- OK -- 


Or....


    def Af(var1, var2):
        """doc of Af"""
        return var1 + var2, var1
    
    ## ...import OpenMDAO here...     
    Afo = OpenMDAO_func(openMDAO_io("""
    var1 = Float(0., iotype='in')
    var2 = Float(0., iotype='in')
    var3 = Float(0., iotype='out')  
    var4 = Float(0., iotype='out')
    """)(Af))
    testclass(Afo)


    -------- New Class -------------
    
    class Af_OMDAO(Component):
        var1 = Float(0., iotype='in')
        var2 = Float(0., iotype='in')
        var3 = Float(0., iotype='out')  
        var4 = Float(0., iotype='out')
        
        def execute(self):
            self.var3, self.var4 = Af(var1 = self.var1, var2 = self.var2)
        
    --------------------------------
    --begin test--
    Af_OMDAO
    doc of Af
    var4 3.0 == 3.0
    var1 3.0 == 3.0
    var3 5.0 == 5.0
    var2 2.0 == 2.0
     -- OK -- 


unfortunately the order of the variables in a dict is not respected, so the
output order is not defined directly.


    
    def Af(var1, var2):
        """doc of Af"""
        return var1 + var2, var1
    
    ## ...import OpenMDAO here...     
    attribs = dict(
        var1 = Float(0., iotype='in'),
        var2 = Float(0., iotype='in'),
        var3 = Float(0., iotype='out'),  
        var4 = Float(0., iotype='out')
    )
    
    Afo = OpenMDAO_func2(Af, outputs=['var3','var4'], attrib=attribs)
    testclass(Afo)


    --begin test--
    Af_OMDAO
    None
    var4 3.0 == 3.0
    var1 3.0 == 3.0
    var3 5.0 == 5.0
    var2 2.0 == 2.0
     -- OK -- 



    @openMDAO_docs
    def Af(var1, var2):
        """doc of Af
        
        OpenMDAO I/O
        ------------
        # Inputs
        var1 = Float(0., iotype='in')   # <- it only keeps the lines that have "iotype" in it
        var2 = Float(0., iotype='in')
        # Outputs
        var3 = Float(0., iotype='out')  # <- First output
        var4 = Float(0., iotype='out')  # <- Second output
        """    
        return var1 + var2, var1
    
    ## ...import OpenMDAO here...     
    Afo = OpenMDAO_func(Af)
    testclass(Afo)

    -------- New Class -------------
    
    class Af_OMDAO(Component):
        var1 = Float(0., iotype='in')   # <- it only keeps the lines that have "iotype" in it
        var2 = Float(0., iotype='in')
        var3 = Float(0., iotype='out')  # <- First output
        var4 = Float(0., iotype='out')  # <- Second output
        
        def execute(self):
            self.var3, self.var4 = Af(var1 = self.var1, var2 = self.var2)
        
    --------------------------------
    --begin test--
    Af_OMDAO
    doc of Af
        
        OpenMDAO I/O
        ------------
        # Inputs
        var1 = Float(0., iotype='in')   # <- it only keeps the lines that have "iotype" in it
        var2 = Float(0., iotype='in')
        # Outputs
        var3 = Float(0., iotype='out')  # <- First output
        var4 = Float(0., iotype='out')  # <- Second output
        
    var4 3.0 == 3.0
    var1 3.0 == 3.0
    var3 5.0 == 5.0
    var2 2.0 == 2.0
     -- OK -- 


We don't even have to put a decorator. We can just call the decorator as a
function when building the openMDAO class.


    def Af(var1, var2):
        """doc of Af
        
        OpenMDAO I/O
        ------------
        # Inputs
        var1 = Float(0., iotype='in')   # <- it only keeps the lines that have "iotype" in it
        var2 = Float(0., iotype='in')
        # Outputs
        var3 = Float(0., iotype='out')  # <- First output
        var4 = Float(0., iotype='out')  # <- Second output
        """    
        return var1 + var2, var1
    
    ## ...import OpenMDAO here...     
    Afo = OpenMDAO_func(openMDAO_docs(Af))
    testclass(Afo)

    -------- New Class -------------
    
    class Af_OMDAO(Component):
        var1 = Float(0., iotype='in')   # <- it only keeps the lines that have "iotype" in it
        var2 = Float(0., iotype='in')
        var3 = Float(0., iotype='out')  # <- First output
        var4 = Float(0., iotype='out')  # <- Second output
        
        def execute(self):
            self.var3, self.var4 = Af(var1 = self.var1, var2 = self.var2)
        
    --------------------------------
    --begin test--
    Af_OMDAO
    doc of Af
        
        OpenMDAO I/O
        ------------
        # Inputs
        var1 = Float(0., iotype='in')   # <- it only keeps the lines that have "iotype" in it
        var2 = Float(0., iotype='in')
        # Outputs
        var3 = Float(0., iotype='out')  # <- First output
        var4 = Float(0., iotype='out')  # <- Second output
        
    var4 3.0 == 3.0
    var1 3.0 == 3.0
    var3 5.0 == 5.0
    var2 2.0 == 2.0
     -- OK -- 


### Creating an OpenMDAO object from a normal *class* (with a `openMDAO_io` decorator)


    @openMDAO_io("""
    var1 = Float(0., iotype='in')
    var2 = Float(0., iotype='in')
    var3 = Float(0., iotype='out')  
    var4 = Float(0., iotype='out')
    """)    
    class A(object):
        """doc of A"""
        def execute(self):
            self.var3 = self.var1 + self.var2
            self.var4 = self.var1
    
    ## ...import OpenMDAO here...     
    Ao2 = OpenMDAO_class(A)
    testclass(Ao2)

    -------- New Class -------------
    
    @openMDAOify(A)    
    class A_OMDAO(Component):
        var1 = Float(0., iotype='in')
        var2 = Float(0., iotype='in')
        var3 = Float(0., iotype='out')  
        var4 = Float(0., iotype='out')
        
        
    --------------------------------
    --begin test--
    A_OMDAO
    doc of A
    var4 3.0 == 3.0
    var1 3.0 == 3.0
    var3 5.0 == 5.0
    var2 2.0 == 2.0
     -- OK -- 


### Normal class using an `@openMDAO_docs` decorator


    @openMDAO_docs
    class A(object):
        """ doc of A
        
        OpenMDAO I/O
        ------------
        # Inputs
        var1 = Float(0., iotype='in')
        var2 = Float(0., iotype='in')
        # Outputs
        var3 = Float(0., iotype='out')  
        var4 = Float(0., iotype='out')
        """
        def execute(self):
            self.var3 = self.var1 + self.var2
            self.var4 = self.var1
            
    A.args
    
    ## ...import OpenMDAO here...     
    Afo = OpenMDAO_class(A)
    testclass(Afo)

    -------- New Class -------------
    
    @openMDAOify(A)    
    class A_OMDAO(Component):
        var1 = Float(0., iotype='in')
        var2 = Float(0., iotype='in')
        var3 = Float(0., iotype='out')  
        var4 = Float(0., iotype='out')
        
        
    --------------------------------
    --begin test--
    A_OMDAO
     doc of A
        
        OpenMDAO I/O
        ------------
        # Inputs
        var1 = Float(0., iotype='in')
        var2 = Float(0., iotype='in')
        # Outputs
        var3 = Float(0., iotype='out')  
        var4 = Float(0., iotype='out')
        
    var4 3.0 == 3.0
    var1 3.0 == 3.0
    var3 5.0 == 5.0
    var2 2.0 == 2.0
     -- OK -- 


### A simple vartree class created from `dict`


    class dictree(dict):
        """Transform a dictionary into a tree"""
        __getattr__ = dict.__getitem__
        __setattr__ = dict.__setitem__
        
        def __init__(self, *args, **kwargs):
            if len(args)>0:
                # Detecting if it's looking like a VariableTree (duck typing style!)
                if 'items' in dir(args[0]):
                    # We initialise the instance using an OpenMDAO VariableTree
                    super(dictree, self).__init__(dict(args[0].items()))
                else:
                    super(dictree, self).__init__(*args, **kwargs)
            else:
                super(dictree, self).__init__(*args, **kwargs)
        
        def VariableTree(self, cls):
            """ Creates an openMDAO VariableTree and fills it with the dic content
            """
            obj = cls()
            for k,v in self.iteritems():
                if k in obj.list_vars():
                    setattr(obj, k, v)
            return obj
    
    wt = dictree(hub_height=100., rotor_diameter=80., power_rating=2000000.)
    
    assert wt['rotor_diameter'] == wt.rotor_diameter
    
    wt_omdao = wt.VariableTree(GenericWindTurbineVT) # <- creating a VariableTree from a dictree
    print list(wt_omdao.items())
    wt2 = dictree(wt_omdao) # <- creating a dictree from a VariableTree
    print wt2

    [('power_rating', 2000000.0), ('rotor_diameter', 80.0), ('hub_height', 100.0)]
    {'hub_height': 100.0, 'rotor_diameter': 80.0, 'power_rating': 2000000.0}



    class GenericWindTurbineVT(VariableTree):
        hub_height = Float(desc='Machine hub height', unit='m')
        rotor_diameter = Float(desc='Machine rotor diameter', unit='m')
        power_rating = Float(desc='Machine power rating', unit='W') # KLD: 
        
    class GenericWSPosition(Component):
        """Calculate the positions where we should calculate the wind speed on the rotor"""
        wt_desc = VarTree(GenericWindTurbineVT(), iotype='in')
        ws_positions = Array([], iotype='out', desc='the position [n,3] of the ws_array', unit='m')
        wt_xy = List([0.0, 0.0], iotype='in', desc='The x,y position of the wind turbine', unit='m')
    
    class HubCenterWSPosition(GenericWSPosition):
        """
        Generate the positions at the center of the wind turbine rotor
        """
        def execute(self):
            self.ws_positions = array([[self.wt_xy[0], self.wt_xy[1], self.wt_desc.hub_height]])



    @openMDAO_docs
    def hub_center_ws_position(wt_desc, wt_xy):
        """
        Generate the positions at the center of the wind turbine rotor
        
        OpenMDAO I/O:
        -------------
        wt_desc = VarTree(GenericWindTurbineVT(), iotype='in')
        wt_xy = List([0.0, 0.0], iotype='in', desc='The x,y position of the wind turbine', unit='m')
        ws_positions = Array([], iotype='out', desc='the position [n,3] of the ws_array', unit='m')
        """
        return array([[wt_xy[0], wt_xy[1], wt_desc.hub_height]])
    
    ## Testing the function
    wt_xy = [20, 300]
    wt = dictree(hub_height=100., rotor_diameter=80., power_rating=2000000.)
    ws_positions = hub_center_ws_position(wt, wt_xy)
    
    ### ... Import OpenMDAO here...
    HubCenterWSPosition2 = OpenMDAO_func(hub_center_ws_position, name='HubCenterWSPosition2', base='GenericWSPosition')
    
    HPos = HubCenterWSPosition2()
    HPos.wt_desc = wt.VariableTree(GenericWindTurbineVT) # Notice how the VariableTree is created from the dictree
    HPos.wt_xy = wt_xy
    HPos.run()
    
    
    print ws_positions, '==', HPos.ws_positions
    assert norm(ws_positions - HPos.ws_positions) == 0.0
    
    dictree(HPos)


    -------- New Class -------------
    
    class HubCenterWSPosition2(GenericWSPosition):
        wt_desc = VarTree(GenericWindTurbineVT(), iotype='in')
        wt_xy = List([0.0, 0.0], iotype='in', desc='The x,y position of the wind turbine', unit='m')
        ws_positions = Array([], iotype='out', desc='the position [n,3] of the ws_array', unit='m')
        
        def execute(self):
            self.ws_positions = hub_center_ws_position(wt_desc = self.wt_desc, wt_xy = self.wt_xy)
        
    --------------------------------
    [[  20.  300.  100.]] == [[  20.  300.  100.]]





    {'derivative_exec_count': 0,
     'directory': '',
     'exec_count': 1,
     'force_execute': False,
     'force_fd': False,
     'itername': '',
     'missing_deriv_policy': 'error',
     'ws_positions': array([[  20.,  300.,  100.]]),
     'wt_desc': <__main__.GenericWindTurbineVT at 0x111d57050>,
     'wt_xy': [20, 300]}




    @openMDAO_docs
    class HubCenterWSPosition1(object):
        """
        Generate the positions at the center of the wind turbine rotor
    
        OpenMDAO I/O:
        -------------
        wt_desc = VarTree(GenericWindTurbineVT(), iotype='in')
        wt_xy = List([0.0, 0.0], iotype='in', desc='The x,y position of the wind turbine', unit='m')
        ws_positions = Array([], iotype='out', desc='the position [n,3] of the ws_array', unit='m')    
        """
        def execute(self):
            self.ws_positions = array([[self.wt_xy[0], self.wt_xy[1], self.wt_desc.hub_height]])
    
    wt_xy = [20, 300]
    wt = dictree(hub_height=100., rotor_diameter=80., power_rating=2000000.)        
            
    HPos1 = HubCenterWSPosition1()
    HPos1.wt_desc = wt
    HPos1.wt_xy = wt_xy
    HPos1.execute()        
            
    ### ... Import OpenMDAO here...
    HubCenterWSPosition3 = OpenMDAO_class(HubCenterWSPosition1, name='HubCenterWSPosition3', base='GenericWSPosition')
    
    HPos3 = HubCenterWSPosition3()
    HPos3.wt_desc = wt.VariableTree(GenericWindTurbineVT) # Notice how the VariableTree is created from the dictree
    HPos3.wt_xy = wt_xy
    HPos3.run()
    
    
    print HPos1.ws_positions, '==', HPos3.ws_positions
    assert norm(HPos1.ws_positions - HPos3.ws_positions) == 0.0
    
    
    from pprint import pprint
    pprint(HPos1.__dict__)
    pprint(dictree(HPos3))
            

    -------- New Class -------------
    
    @openMDAOify(HubCenterWSPosition1)    
    class HubCenterWSPosition3(GenericWSPosition):
        wt_desc = VarTree(GenericWindTurbineVT(), iotype='in')
        wt_xy = List([0.0, 0.0], iotype='in', desc='The x,y position of the wind turbine', unit='m')
        ws_positions = Array([], iotype='out', desc='the position [n,3] of the ws_array', unit='m')    
        
        
    --------------------------------
    [[  20.  300.  100.]] == [[  20.  300.  100.]]
    {'ws_positions': array([[  20.,  300.,  100.]]),
     'wt_desc': {'hub_height': 100.0,
                 'power_rating': 2000000.0,
                 'rotor_diameter': 80.0},
     'wt_xy': [20, 300]}
    {'derivative_exec_count': 0,
     'directory': '',
     'exec_count': 1,
     'force_execute': False,
     'force_fd': False,
     'itername': '',
     'missing_deriv_policy': 'error',
     'ws_positions': array([[  20.,  300.,  100.]]),
     'wt_desc': <__main__.GenericWindTurbineVT object at 0x111d57c50>,
     'wt_xy': [20, 300]}



    
