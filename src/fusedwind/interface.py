
from openmdao.main.interfaces import Interface, implements
from zope.interface import implementer
from openmdao.main.api import Component, Assembly, VariableTree
from openmdao.lib.datatypes.api import Slot, Instance
from fused_helper import fused_autodoc


# FUSED Framework ----------------------------------
def interface(comp_cls):
    """Returns the class ICompCls(Interface)"""
    class MyInterface(Interface):
        pass
    MyInterface.__name__ = 'I' + comp_cls.__name__
    return MyInterface


def base(cls):
    """Decorator for a FUSED base class"""
    # desactivating the autodoc feature
    return fused_autodoc(implementer(interface(cls))(cls))
    # return implementer(interface(cls))(cls)


def cls_list_vars(cls):
    """Return a list of variables in a VariableTree class"""
    return [k for k, v in cls.__class_traits__.iteritems() if k not in VariableTree.__class_traits__ and not v.vartypename == None]


def cls_list_outputs(cls):
    """Return a list of outputs in a Component class"""
    return [k for k, v in cls.__class_traits__.iteritems() if v.iotype == 'out' and k not in Component.__class_traits__ and not v.vartypename == None]


def cls_list_inputs(cls):
    """Return a list of inputs in a Component class"""
    return [k for k, v in cls.__class_traits__.iteritems() if v.iotype == 'in' and k not in Component.__class_traits__ and not v.vartypename == None]


def check_base_compliance(base, cls):
    """Do some checks on the I/O compatibility of the class with its base:

    parameters
    ----------
    base    class
            the base class to be satisfied

    cls     class
            the current class to check
    """
    if issubclass(cls, VariableTree) or issubclass(base, VariableTree):
        try:
            assert set(cls_list_vars(base)).issubset(set(cls_list_vars(cls)))
        except:
            raise Exception('Variables of the class %s are different from base %s:' % (
                cls.__name__, base.__name__), '.'.join(set(cls_list_vars(base)) - set(cls_list_vars(cls))))
    else:  # Assuming it's a Component or Assembly
        try:
            assert set(cls_list_inputs(base)).issubset(
                set(cls_list_inputs(cls)))
        except:
            raise Exception('Inputs of the class %s are different from base %s.  The missing input(s) of %s are: %s' % (
                cls.__name__, base.__name__, cls.__name__, ','.join(set(cls_list_inputs(base)) - set(cls_list_inputs(cls)))))  # , cls_list_inputs(cls), cls_list_inputs(base))
        try:
            assert set(cls_list_outputs(base)).issubset(
                cls_list_outputs(cls))
        except:
            raise Exception('Outputs of the class %s are different from base %s.  The missing output(s) of %s are: %s' % (
                cls.__name__, base.__name__, cls.__name__, '.'.join(set(cls_list_outputs(base)) - set(cls_list_outputs(cls)))))  # , cls_list_outputs(ob), cls_list_outputs(base))


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
        if not hasattr(cls, '_fused_base'):
            cls._fused_base = []
        cls._fused_base.append(self._base)
        return base(implementer(interface(self._base))(cls))

    def check(self, cls):
        """Do some checks on the I/O compatibility of the class with its base:

        TODO:
        -----
            * Add test on variable type
        """
        return check_base_compliance(self._base, cls)


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


class configure_base(object):
    """decorator that enforces a check that the function first argument instance (i.e. self)
    is in compliance with the base class.
    """

    def __init__(self, base):
        self._base = base

    def __call__(self, func):
        def new_func(_self, *args, **kwargs):
            # Check if _self satisfies the base class
            check_base_compliance(self._base, _self.__class__)
            return func(_self, *args, **kwargs)

        # let it be a well-behaved decorator.
        new_func.__name__ = func.__name__
        new_func.__doc__ = func.__doc__
        new_func.__dict__.update(func.__dict__)
        return new_func


def InterfaceInstance(cls, *args, **kwargs):
    return Instance(interface(cls), *args, **kwargs)


def InterfaceSlot(cls, *args, **kwargs):
    return Slot(interface(cls), *args, **kwargs)


class FUSEDAssembly(Assembly):
    _debug = False


    def __init__(self, **kwargs):
        super(FUSEDAssembly, self).__init__()
        for k, v in kwargs.iteritems():
            if k in self.list_containers():
                self.add(k, v)

            if k in self.list_inputs():
                setattr(self, k, v)

    def add_default(self, name, obj):
        obj_name = self._add(name, obj, replace=False)
        self._fused_components[name]['default'] = obj
        # Check the previously added components compatibility with
        # the default component
        for k, v in self._fused_components[name].iteritems():
            if not k == 'default':
                self.check_compatibility_with_default(name, v)
        return obj_name

    def add(self, name, obj):
        obj = self._add(name, obj, replace=True)
        return obj

    def _add(self, name, obj, replace=True):
        """Method to replace components with other compatible components

        Parameters
        ----------

        self:    Assembly
                 the assembly where the components are going to be added

        name:     str
                 The name of the component to add

        obj:     Component instance
                 The component to add to the self Assembly

        replace: bool
                 A flag to indicate if the object should replace a
                 previously added component


        Example
        --------



        """
        if not hasattr(self, '_fused_components'):
            # This is the first time that this method is run
            self._fused_components = {}

        # Check the compatibility of the new object with the existing
        # classes
        self.check_compatibility_with_default(name, obj)

        name_id = obj.__class__.__name__
        if name not in self._fused_components:
            self._fused_components[name] = {}
            self._fused_components[name][name_id] = obj
            if self._debug:
                print 'adding', name, '=', name_id
            # Call the original add
            return super(FUSEDAssembly, self).add(name, obj)
        elif replace:
            self._fused_components[name][name_id] = obj
            if self._debug:
                print 'replacing', name, 'with', name_id
            return super(FUSEDAssembly, self).add(name, obj)
        else:
            self._fused_components[name][name_id] = obj
            if self._debug:
                print 'not replacing', name, 'with', name_id
            return name

    def check_compatibility_with_default(self, name, obj):
        if name in self._fused_components:
            if 'default' in self._fused_components[name]:
                default = self._fused_components[name]['default']
                self.check_compatibility(default, obj)

    def check_compatibility(self, obj1, obj2):
        """Check if the obj2 is satisfying the same interface as obj1
        """
        if self._debug:
            print 'checking that', obj2.__class__.__name__, 'is compatible with', obj1.__class__.__name__
        if issubclass(obj2.__class__, VariableTree) or \
           issubclass(obj1.__class__, VariableTree):
            try:
                assert set(obj1.list_vars()).issubset(set(obj2.list_vars()))
            except:
                raise Exception('Variables of the class %s are different from base %s:' % (
                    obj2.__class__.__name__, obj1.__class__.__name__), obj2.list_vars(), ', '.join(obj1.list_vars()))
        else:  # Assuming it's a Component or Assembly
            try:
                assert set(obj1.list_inputs()).issubset(
                    set(obj2.list_inputs()))
            except:
                raise Exception('Inputs of the class %s are different from base %s.  The missing input(s) of %s are: %s' % (
                    obj2.__class__.__name__, obj1.__class__.__name__, obj2.__class__.__name__, ', '.join(set(obj1.list_inputs()) - set(obj2.list_inputs()))))
            try:
                assert set(obj1.list_outputs()).issubset(obj2.list_outputs())
            except:
                raise Exception('Outputs of the class %s are different from base %s.  The missing output(s) of %s are: %s' % (
                    obj2.__class__.__name__, obj1.__class__.__name__, obj2.__class__.__name__, ', '.join(set(obj1.list_outputs()) - set(obj2.list_outputs()))))
        if self._debug:
            print '--> OK'
