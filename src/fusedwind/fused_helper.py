
from openmdao.main.api import Component, Assembly, VariableTree
from openmdao.main.driver import Driver
from openmdao.lib.drivers.api import CaseIteratorDriver
from openmdao.lib.datatypes.api import VarTree, Float, Instance, Slot, Array, List, Int, Str, Dict
base_keys = Assembly.__base_traits__.keys() + Driver.__base_traits__.keys() + \
    CaseIteratorDriver.__base_traits__.keys()

# from pygraphviz import AGraph # kld windows issues
from IPython.display import SVG
from collections import defaultdict
import json
from numpy import ndarray, array
import pandas


from openmdao.main.interfaces import Interface, implements
from zope.interface import implementer
from openmdao.main.api import Component, Assembly
from pprint import pprint
# FUSED Framework ----------------------------------


# Creating the svg representation for dot_graphs
def _repr_svg_(self):
    self.draw('star.svg', prog="dot")
    return SVG(filename='star.svg')

# AGraph.svg = property(lambda self: _repr_svg_(self)) # kld windows issues

add2key = lambda key, dico: dict(
    [(key + '.' + k, v) for k, v in dico.iteritems()])


def flatten(t):
    """Flatten a nested dictionary"""
    out = []
    for k, v in t.iteritems():
        if isinstance(v, dict):
            out += add2key(k, flatten(v)).items()
        else:
            out.append((k, v))
    return dict(out)

# Neat tree dictionary


class dictree(dict):

    """Transform a dictionary into a tree"""
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__

    # def __init__(self, *args, **kwargs):
    #    if len(args)>0:
    # Detecting if it's looking like a VariableTree (duck typing style!)
    #        if 'items' in dir(args[0]):
    # We initialise the instance using an OpenMDAO VariableTree
    #            super(dict, self).__init__(dict(args[0].items()))
    #        else:
    #            super(dict, self).__init__(*args, **kwargs)
    #    else:
    #        super(dict, self).__init__(*args, **kwargs)

    def VariableTree(self, cls):
        """ Creates an openMDAO VariableTree and fills it with the dic content
        """
        obj = cls()
        for k, v in self.iteritems():
            if k in obj.list_vars():
                if isinstance(getattr(self, k), dictree):
                    v = getattr(self, k).VariableTree(
                        getattr(obj, k).__class__)
                setattr(obj, k, v)
        return obj

    def serialize(self):
        new_dic = self.copy()
        for k, v in self.iteritems():
            if isinstance(v, dictree):
                new_dic[k] = v.serialize()
            elif isinstance(v, ndarray):
                new_dic[k] = v.tolist()
        return new_dic

    def _repr_json_(self):
        print json.dumps(self.serialize(), sort_keys=True, indent=2, separators=(',', ': '))

    @property
    def json(self):
        self._repr_json_()

    def flatten(self):
        return flatten(self)

    def df(self):
        """return a flatten pandas DataFrame of the dictree"""
        return pandas.DataFrame(self.flatten())


class defaultdictree(defaultdict, dictree):

    """Same as dictree, but with defaultdict as a base"""

    def __missing__(self, *args, **kwargs):
        # Avoid all kind of private function calls
        if not args[0][0] == '_':
            return defaultdict.__missing__(self, *args, **kwargs)

# Create an automatic tree generator
# >>> t = tree()
# >>> t.hello = 'world'
# >>> t.kitty.hello = 'world'
# >>> t.json
#
# Out[0]
#        {
#          "hello": "world",
#          "kitty": {
#            "hello": "world"
#          }
#        }
tree = lambda *args, **kwargs: defaultdictree(tree, *args, **kwargs)


def list_ios(self, iotype=None):
    """ Only list the I/Os that are not in the base Assembly class"""
    if not iotype:
        return [i for i in self.list_vars() if i not in base_keys]
    if iotype == 'in':
        if hasattr(self, 'list_inputs'):
            return [i for i in self.list_inputs() if i not in base_keys]
        else:
            return []
    if iotype == 'out':
        if hasattr(self, 'list_outputs'):
            return [i for i in self.list_outputs() if i not in base_keys]
        else:
            return []

black_list = ['gradient_options']


def my_tree(self, iotype=None):
    if hasattr(self, 'list_containers'):
        containers = [f for f in self.list_containers() if f not in black_list and any(
            [isinstance(getattr(self, f), o) for o in (Component, Driver, Assembly, VariableTree)])]
        return dictree([i for i in self.items() if i[0] in list_ios(self, iotype)] + [(c, my_tree(getattr(self, c), iotype)) for c in containers])
    elif isinstance(self, List):
        return [my_tree(s, iotype) for s in self]
    else:
        return self


def _repr_tree_(self):
    my_tree(self).json


def disp(comp):
    """Display a Container"""
    return pprint(dict(comp.items()))

def my_call(self, **kwargs):
    """Partial function of the Component/Assembly
    Returns a tree dictionary containing the inputs, outputs and nested result dictionaries from the containers
    """
    for k, v in kwargs.iteritems():
        setattr(self, k, v)
    self.run()
    return self


def my_str(var, parent='', value=False):
    """String representation for generating graphs"""
    if isinstance(var, VariableTree):
        out = '{' + '<' + parent + '> ' + parent + '|{' + \
            '|'.join([my_str(v, k, value) for k, v in var.items()]) + '}}'
    else:
        if value:
            out = '<' + parent + '> ' + parent + '=' + str(var)
        else:
            out = '<' + parent + '> ' + parent
    # print out
    return out


def out_graph_component(self, graph, value=False):
    """Generate the dot_graph for a component

    parameters:
    -----------
    * graph: a pygraphviz AGraph instance
    * value: print the value (default False)
    """
    if not hasattr(self, 'name') or self.name == '':
        name = self.__class__.__name__
    else:
        name = self.name
    graph.add_node(name, label='%s|{{%s}|{%s}}' % (name,
                                                   '|'.join(
                                                       [my_str(getattr(self, n), n, value) for n in list_ios(self, 'in')]),
                                                   '|'.join([my_str(getattr(self, n), n, value) for n in list_ios(self, 'out')])), shape="record", style='rounded,filled', fillcolor='lightblue')


def out_graph_driver(self, graph, value=False):
    """Generate the dot_graph for a driver

    parameters:
    -----------
    * graph: a pygraphviz AGraph instance
    * value: print the value (default False)
    """
    c1 = graph.add_subgraph(
        name='cluster_' + self.name, label=self.name, color='orange', style='rounded')
    c1.add_node(self.name + '_in', label='Inputs|%s' %
                ('|'.join([my_str(getattr(self, n), n, value) for n in list_ios(self, 'in')])), style='rounded', shape="record")
    c1.add_node(self.name + '_out', label='Outputs|%s' %
                ('|'.join([my_str(getattr(self, n), n, value) for n in list_ios(self, 'out')])), style='rounded', shape="record")
    for c in self.workflow.get_names():
        getattr(self.parent, c).out_graph(c1, value)


def out_graph_assembly(self, graph, value=False):
    """Generate the dot_graph for an Assembly

    parameters:
    -----------
    * graph: a pygraphviz AGraph instance
    * value: print the value (default False)
    """
    if self.name == '':
        self.name = 'Assembly_' + self.__class__.__name__
    c1 = graph.add_subgraph(name='cluster_' + self.name, label=self.name)
    # Draw the inputs / outputs
    c1.add_node(self.name + '_in', label='Inputs|%s' %
                ('|'.join([my_str(getattr(self, n), n, value) for n in list_ios(self, 'in')])), style='rounded', shape="record")
    c1.add_node(self.name + '_out', label='Outputs|%s' %
                ('|'.join([my_str(getattr(self, n), n, value) for n in list_ios(self, 'out')])), style='rounded', shape="record")
    # Draw the drivers
    self.driver.out_graph(c1, value)
    # Draw the connections
    for e in self._depgraph.edges():
        if len(e[0].split('.')) > 2 or len(e[1].split('.')) > 2:
            continue
        if '.' in e[0] and '.' in e[1]:
            e00, e01 = e[0].split('.')
            e10, e11 = e[1].split('.')
            if all([e_ not in Assembly.__base_traits__ for e_ in [e00, e01, e10, e11]]):
                if isinstance(getattr(self, e00), Driver) or isinstance(getattr(self, e00), Assembly):
                    e00 = e00 + '_out'
                if isinstance(getattr(self, e10), Driver) or isinstance(getattr(self, e10), Assembly):
                    e10 = e10 + '_in'
                graph.add_edge(e00, e10, tailport=e01, headport=e11)
        if '.' not in e[0] and '.' in e[1]:
            e10, e11 = e[1].split('.')
            if all([e_ not in Assembly.__base_traits__ for e_ in [e[0], e10, e11]]):
                if e[0] in self.list_ios('in'):
                    graph.add_edge(
                        self.name + '_in', e10, tailport=e[0], headport=e11)
        if '.' in e[0] and '.' not in e[1]:
            e00, e01 = e[0].split('.')
            if all([e_ not in Assembly.__base_traits__ for e_ in [e00, e01, e[1]]]):
                if e[1] in self.list_ios('out'):
                    graph.add_edge(
                        e00, self.name + '_out', tailport=e01, headport=e[1])


def make_graph(self, name='Graph', value=False):
    """Make the dot_graph of an OpenMDAO Component/Driver/Assembly instance"""
    g1 = AGraph(directed=True, strict=False, name=name, rankdir='LR')
    self.out_graph(g1, value)
    return g1


def draw_graph(self, name='Graph', value=False):
    """Draw the SVG dot_graph of an OpenMDAO Component/Driver/Assembly instance"""
    return self.make_graph(name, value).svg


from IPython.html.widgets import interact, interactive, fixed
from IPython.html import widgets
from IPython.display import clear_output, display, HTML


def interactive_graph(self):
    """Create an interative graph using Ipython widgets
    """
    basedict = self.__class__.__base_traits__
    inputs = dict([(c, (getattr(basedict[c], 'low'), getattr(basedict[c], 'high')))
                   for c in list_ios(self, 'in')])

    def f(**kwargs):
        my_call(self, **kwargs)
        display(self.draw_graph(value=True))
    return interact(f, **inputs)


def interactive_output(self):
    """Create an interative graph using Ipython widgets
    """
    basedict = self.__class__.__base_traits__
    inputs = dict([(c, (getattr(basedict[c], 'low'), getattr(basedict[c], 'high')))
                   for c in list_ios(self, 'in')])

    def f(**kwargs):
        my_call(self, **kwargs)
        display(my_tree(self).json)
    interact(f, **inputs)


def interactive_plot(self):
    """Create an interative plot using Ipython widgets
    """
    basedict = self.__class__.__base_traits__
    inputs = dict([(c, (getattr(basedict[c], 'low'), getattr(basedict[c], 'high')))
                   for c in list_ios(self, 'in')])

    def f(**kwargs):
        my_call(self, **kwargs)
        display(self.plot())
    interact(f, **inputs)

# Create a flat tree from a Component or Assembly
flatree = lambda a, iotype=None: my_tree(a, iotype).flatten()


class pandasMDAO(object):

    """Create a pandas memorizer to a component or an Assembly.
    Each time the memorizer is run, it will look in the DataFrame if the inputs are already there,
    if they are it will update the component or assembly with the corresponding outputs, otherwise
    it will run the component or assembly and append the results to the DataFrame
    """

    def __init__(self, a):
        self.create(a)

    def create(self, a):
        self.df = pandas.DataFrame(columns=flatree(a).keys())

    def append(self, a):
        self.df = self.df.append(flatree(a), ignore_index=True)

    def compare(self, k, v):
        if isinstance(v, list):
            return [i == v for i in self.df[k]]
        elif isinstance(v, ndarray):
            return [i.tolist() == v.tolist() for i in self.df[k]]
        else:
            return self.df[k] == v

    def bool_arr(self, a, iotype=None):
        return array([self.compare(k, v) for k, v in flatree(a, iotype).iteritems()])

    def exists(self, a, iotype=None):
        return self.bool_arr(a, iotype).all(0).any()

    def run(self, a, run_callback='run'):
        if self.exists(a, iotype='in'):
            print 'returning'
            state = {k: v for k, v in zip(
                self.df.keys(), self.df[self.bool_arr(a, iotype='in').all(0)].values[0])}
            for k in a.list_outputs():
                if k in state:
                    setattr(a, k, state[k])
            # return state
        else:
            print 'calculating'
            getattr(a, run_callback)()
            self.append(a)
            # return {k: v for k,v in zip(self.df.keys(),
            # self.df[self.bool_arr(a, iotype='in').all(0)].values[0])}

    def plot(self, *args, **kwargs):
        return self.df.plot(*args, **kwargs)


def pandas_memoized(cls):
    """Decorator to add a pandas memorizer to a component or an assembly
    """
    if not hasattr(cls, '_pmdao'):
        cls._pmdao = pandasMDAO(cls())
        # The usual run function is moved to _run
        cls._run = cls.run
        # The new run function is calling the pandas memoized object
        cls.run = lambda self: self._pmdao.run(self, '_run')
        cls.plot = cls._pmdao.plot
        cls.df = property(lambda self: self._pmdao.df)
    return cls


def lconnect(self, a, b):
    """
    lazy_connect function.
    try to connect the outputs of a to the inputs of b that have the same name.

    Parameters
    ----------

    self    Assembly
            The assembly containing the components to connect

    a       str
            The name of the component output a to connect.
            If a == '', then self.inputs is used

    b       str
            The name of the component inputs a to connect.
            If b == '', then self.outputs is used



    """
    black_set = set(Assembly().list_vars())
    if a == '':
        _a = self
        set_a = set(_a.list_inputs()) - black_set
        str_a = ''
    else:
        _a = getattr(self, a)
        set_a = set(_a.list_outputs()) - black_set
        str_a = a + '.'

    if b == '':
        _b = self
        set_b = set(_b.list_outputs()) - black_set
        str_b = ''
    else:
        _b = getattr(self, b)
        set_b = set(_b.list_inputs()) - black_set
        str_b = b + '.'

    print 'trying some lazy connection between "%s" and "%s" on' % (a, b), list(set_a.intersection(set_b))
    for v in set_a.intersection(set_b):
        try:
            self.connect(str_a + v, str_b + v)
            print str_a + v, '->', str_b + v
        except RuntimeError as e:
            # No crash when the connection is failing, just a warning printing
            # the error
            print str_a + v, '->', str_b + v, '(', e, ')'


def init_container(self, **kwargs):
    """Initialise a container with a dictionary of inputs
    """
    for k, v in kwargs.iteritems():
        try:
            setattr(self, k, v)
        except Exception as e:
            # Deal with the array -> list issue
            if isinstance(getattr(self, k), list) and isinstance(v, ndarray):
                setattr(self, k, v.tolist())

    return self


def fused_autodoc(cls):
    """Decorator to automatically document the inputs and outputs of an Assembly / Component

    """
    clsname = cls.__name__
    if not cls.__doc__:
        cls.__doc__ = '**TODO**: fill in this doc\n\n'
    white_list = ['VarTree', 'Float', 'Slot', 'Array', 'List', 'Int', 'Str', 'Dict', 'Enum']
    inputs = [k for k, v in cls.__class_traits__.iteritems() if v.iotype == 'in'
              and k not in Component.__class_traits__
              and k not in Assembly.__class_traits__
              and k.find('_items') == -1]
    outputs = [k for k, v in cls.__class_traits__.iteritems() if v.iotype == 'out'
              and k not in Component.__class_traits__
              and k not in Assembly.__class_traits__
              and k.find('_items') == -1]

    variables = [k for k, v in cls.__class_traits__.iteritems()
                    if k not in VariableTree.__class_traits__
                    and k.find('_items') == -1]
    #print inputs
    el = '\n    '
    def addl(x=''):
        cls.__doc__+=x+el
    addl()
    addl()
    addl('Parameters')
    addl('----------')
    if issubclass(cls, Component):
        addl(el.join([i + ':    ' + cls.__class_traits__[i].trait_type.__class__.__name__ +
                          ', default=' + cls.__class_traits__[i].default.__str__() +
                          ', [%s]'%(cls.__class_traits__[i].units) +
                          el+'   ' + cls.__class_traits__[i].desc.__str__()+'.'+el
                          for i in inputs]))

    if issubclass(cls, VariableTree):
        addl(el.join([i + ':    ' + cls.__class_traits__[i].trait_type.__class__.__name__ +
                          ', default=' + cls.__class_traits__[i].default.__str__() +
                          ', [%s]'%(cls.__class_traits__[i].units) +
                          el+'   ' + cls.__class_traits__[i].desc.__str__()+'.'+el
                          for i in variables]))

    addl('')

    if issubclass(cls, Component):
        addl('Returns')
        addl('-------')
        addl(el.join([i + ':    ' + cls.__class_traits__[i].trait_type.__class__.__name__ +
                          ', [%s]'%(cls.__class_traits__[i].units) +
                          el+'   ' + cls.__class_traits__[i].desc.__str__()+'.'+el
                          for i in outputs]))

    addl('Notes')
    addl('-------')

    # Check if the class has some base:
    if hasattr(cls, '_fused_base'):
        addl('``%s``'%(clsname) + ' implements the following interfaces: ' + ', '.join(['``%s``'%(c.__name__) for c in cls._fused_base]))
        addl()


    return cls

def _register(cls):
    if cls.__name__ == 'Component':
        cls.out_graph = out_graph_component
    elif cls.__name__ == 'Assembly':
        cls.out_graph = out_graph_assembly
        cls.lconnect = lconnect
    elif cls.__name__ == 'VariableTree':
        cls.tree = property(my_tree)
        cls._repr_json_ = _repr_tree_
        cls.init = init_container
    elif cls.__name__ == 'Driver':
        cls.out_graph = out_graph_driver
        cls.init = init_container
    if any([cls.__name__ == e for e in ['Component', 'Driver', 'Assembly']]):
        cls.tree = property(my_tree)
        cls.make_graph = make_graph
        cls.draw_graph = draw_graph
        cls.__call__ = my_call
        cls.list_ios = list_ios
        cls.interactive_graph = interactive_graph
        cls.interactive_output = interactive_output
        cls.interactive_plot = interactive_plot
        cls._repr_json_ = _repr_tree_
        cls.init = init_container


def register(list_cls):
    if isinstance(list_cls, list):
        for cls in list_cls:
            _register(cls)
    else:
        _register(cls)


# Registering some extra functions to base classes
register([Component, Assembly, Driver, VariableTree])
