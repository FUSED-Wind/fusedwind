
from openmdao.main.interfaces import Interface, implements
from zope.interface import implementer
from openmdao.main.api import Component, Assembly, VariableTree
from openmdao.lib.datatypes.api import Slot, Instance


# FUSED Framework ----------------------------------
def interface(comp_cls):
    """Returns the class ICompCls(Interface)"""
    class MyInterface(Interface):pass
    MyInterface.__name__ = 'I' + comp_cls.__name__
    return MyInterface

def base(cls):
    """Decorator for a FUSED base class"""
    return implementer(interface(cls))(cls)


def cls_list_vars(cls):
    """Return a list of variables in a VariableTree class"""
    return [k for k,v in cls.__class_traits__.iteritems() if k not in VariableTree.__class_traits__ and not v.vartypename == None]

def cls_list_outputs(cls):
    """Return a list of outputs in a Component class"""    
    return [k for k, v in cls.__class_traits__.iteritems() if v.iotype=='out' and k not in Component.__class_traits__ and not v.vartypename == None]
    
def cls_list_inputs(cls):
    """Return a list of inputs in a Component class"""    
    return [k for k, v in cls.__class_traits__.iteritems() if v.iotype=='in' and k not in Component.__class_traits__  and not v.vartypename == None]
    

class _implement_base(object):
    """
    tag the curent class with the base class interface. 
    Add a check on the I/O. 

    Usage:
    ------

    @base
    class BaseClass(object):
        vi1 = Float(iotype='in')
        vi2 = Float(iotype='in')
        vo1 = Float(iotype='out')

    @_implement_base(BaseClass)
    class MyClass(object):    
        vi1 = Float(iotype='in')
        vi2 = Float(iotype='in')
        vo1 = Float(iotype='out')
    """
    def __init__(self, cls):
        """Store the base calss in the object variable _base

        parameters
        ----------
        cls     class
                the base class to store

        """
        self._base = cls
        
    def __call__(self, cls):
        """Check if the new class satisfy the requirements 
        of the base class and return the implementation of 
        the new class

        parameters
        ----------
        cls     class
                the new class to process

        """
        self.check(cls)
        return base(implementer(interface(self._base))(cls))

    def check(self, cls):
        """Do some checks on the I/O compatibility of the class with its base:

        TODO:
        -----
            * Add test on variable type
        """

        if issubclass(cls, VariableTree) or issubclass(self._base, VariableTree):
            try: 
                assert set(cls_list_vars(self._base)).issubset(set(cls_list_vars(cls)))
            except:
                raise Exception('Variables of the class %s are different from base %s:'%(cls.__name__, self._base.__name__), set(cls_list_vars(self._base))-set(cls_list_vars(cls)))
        else: ## Assuming it's a Component or Assembly
            try: 
                assert set(cls_list_inputs(self._base)).issubset(set(cls_list_inputs(cls)))
            except:
                raise Exception('Inputs of the class %s are different from base %s.  The missing input(s) of %s are: %s'%(cls.__name__, self._base.__name__,cls.__name__, (set(cls_list_inputs(self._base))-set(cls_list_inputs(cls))))) #, cls_list_inputs(cls), cls_list_inputs(self._base))
            try:
                assert set(cls_list_outputs(self._base)).issubset(cls_list_outputs(cls))
            except:
                raise Exception('Outputs of the class %s are different from base %s.  The missing output(s) of %s are: %s'%(cls.__name__, self._base.__name__,cls.__name__, (set(cls_list_outputs(self._base))-set(cls_list_outputs(cls))))) #, cls_list_outputs(ob), cls_list_outputs(self._base))


class implement_base(object):
    """
    Decorator to implements the bases. Can both be used for Components and Assemblies

    Usage:
    ------

    @base
    class BaseClass1(object):
        vi1 = Float(iotype='in')
        vi2 = Float(iotype='in')
        vo1 = Float(iotype='out')

    @base
    class BaseClass2(object):
        vi3 = Float(iotype='in')
        vi4 = Float(iotype='in')
        vo2 = Float(iotype='out')

    @implement_base(BaseClass1, BaseClass2)
    class MyClass(object):
        vi1 = Float(iotype='in')
        vi2 = Float(iotype='in')
        vi3 = Float(iotype='in')
        vi4 = Float(iotype='in')

        vo1 = Float(iotype='out')
        vo2 = Float(iotype='out')


    """
    def __init__(self, *args):
        self._bases = args
    def __call__(self, cls):
        out = cls
        for base in self._bases:
            out = _implement_base(base)(out)
        return out

    
def InterfaceInstance(cls, *args, **kwargs):
    return Instance(interface(cls), *args, **kwargs)



