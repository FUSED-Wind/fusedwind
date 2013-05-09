
from StringIO import StringIO
from openmdao.main.api import VariableTree
# import ipdb

class FusedIOVariableTree(VariableTree):

    def __init__(self, iotype=''):
        super(FusedIOVariableTree, self).__init__()

    def print_vars(self, parent=None):

        attrs = {}
        attrs['type'] = type(self).__name__

        parameters = {}

        for name in self.list_vars():

            trait = self.get_trait(name)
            meta = self.get_metadata(name)
            value = getattr(self, name)
            ttype = trait.trait_type

            # Each variable type provides its own basic attributes
            attr, slot_attr = ttype.get_attribute(name, value, trait, meta)

            # Let the GUI know that this var is the top element of a
            # variable tree
            if attr.get('ttype') == 'vartree':
                vartable = self.get(name)
                if hasattr(vartable, 'print_vars'):
                    attr['vt'] = 'vt'

            # For variables trees only: recursively add the inputs and outputs
            # into this variable list
            if 'vt' in attr:
                vt_attrs = vartable.print_vars()
                parameters[name] = vt_attrs
            else:
                if meta['vartypename'] == 'Array':
                    parameters[name] = list(value)
                elif meta['vartypename'] == 'List':
                    for i, item in enumerate(value):
                        if isinstance(item, object):
                            value[i] = item.print_vars()
                    parameters[name] = value
                else:
                    parameters[name] = value
            # print 'name', name,trait, meta, ttype
            # ipdb.set_trace()

        attrs['parameters'] = parameters
        class_dict = {}
        if self.name is '':
            name = type(self).__name__
        else:
            name = self.name
        class_dict[name] = attrs
        return attrs
