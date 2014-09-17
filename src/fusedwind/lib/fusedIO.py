
import json
# import ipdb
import copy
import numpy as np
from openmdao.main.api import Component, VariableTree
from openmdao.lib.datatypes.api import Str, Slot
from fusedwind.vartrees import api


class FUSEDWindIO(Component):
    """
    Master IO class for reading and writing JSON formatted files.

    For writing an input file the class relies on the modified VariableTree
    class FusedVariableTree that has the method print_vars()
    which returns its parameters in a nicely printed nested dictionary
    containing only keys and variables.

    To read an input file each section in the file has to have
    a key named "type" which is the name of the VarTree
    to be instantiated and set with the entries in the input section.
    """

    master_input_file = Str('fusedwind_master.json',desc='')
    master_output_file = Str('fusedwind_master_out.json',desc='')
    vtrees_in = Slot(iotype='out')
    vtrees_out = Slot(iotype='in')

    def load_master(self):

        f = open(self.master_input_file,'r')
        loaded = json.load(f)
        
        self.add('vtrees_in',Component())

        for name, comp in loaded.iteritems():
            decoded = self.decode_json(comp)
            print 'loading', name
            vt = self.load_vartree(decoded)
            self.vtrees_in.add(name, vt)

    def write_master(self):
        """serialize and write object hierarchy to a JSON file"""

        f = open(self.master_output_file,'wb')
        master = {}
        master[self.vtrees_out.name] = self.print_vars(self.vtrees_out)
        # for comp in self.vtrees_out.list_vars():
        #     obj = getattr(self.vtrees_out, comp)
        #     # obj = copy.deepcopy(obj)
        #     if isinstance(obj, VariableTree):
        #         print 'dumping', comp
        #         master[comp] = self.print_vars(obj)
        self._master = master
        # ipdb.set_trace()
        json.dump(master, f, indent = 4)

    def print_vars(self, obj, parent=None):

        attrs = {}
        attrs['type'] = type(obj).__name__

        parameters = {}

        for name in obj.list_vars():

            trait = obj.get_trait(name)
            meta = obj.get_metadata(name)
            value = getattr(obj, name)
            ttype = trait.trait_type


            # Each variable type provides its own basic attributes
            attr, slot_attr = ttype.get_attribute(name, value, trait, meta)
            # Let the GUI know that this var is the top element of a
            # variable tree
            if attr.get('ttype') in ['vartree', 'slot']:
                vartable = obj.get(name)
                # if hasattr(vartable, 'print_vars'):
                attr['vt'] = 'vt'

            # For variables trees only: recursively add the inputs and outputs
            # into this variable list
            if 'vt' in attr:
                vt_attrs = self.print_vars(vartable)
                parameters[name] = vt_attrs
            else:
                if meta['vartypename'] == 'Array':
                    parameters[name] = value.tolist()
                elif meta['vartypename'] == 'List':
                    newvalues = []
                    for i, item in enumerate(value):
                        if isinstance(item, VariableTree):
                            newvalues.append(self.print_vars(item))
                        elif isinstance(item, np.ndarray):
                            newvalues.append(item.tolist())
                        else:
                            newvalues.append(item)
                    parameters[name] = newvalues
                else:
                    parameters[name] = value
            # ipdb.set_trace()

        attrs['parameters'] = parameters
        class_dict = {}
        if obj.name is '':
            name = type(obj).__name__
        else:
            name = obj.name
        class_dict[name] = attrs
        return attrs


    def decode_json(self, vartree):
        """decode unicode keys to ascii strings"""

        outtree = {}

        for key, val in vartree.iteritems():
            key = key.encode('ascii')
            if isinstance(val, dict):
                outtree[key] = self.decode_json(val)
            else:
                if type(val) == unicode:
                    outtree[key] = val.encode('ascii')
                else:
                    outtree[key] = val

        return outtree

    def load_vartree(self, vartree):
        """convert an input dictionary to a FusedIOVariableTree"""

        obj = None

        if 'type' in vartree:
            name = vartree['type']
            try:
                klass = getattr(api, name)
                obj = klass()
            except:
                raise RuntimeError('unknown variable tree type %s'%name)
            

        for key, val in vartree['parameters'].iteritems():
            if key == 'type':
                pass
            if isinstance(val, dict):
                print 'loading', key
                child = self.load_vartree(val)
                setattr(obj, key, child)
            elif isinstance(val, list):
                for i, item in enumerate(val):
                    if isinstance(item, dict):
                        child = self.load_vartree(item)
                        val[i] = child
                setattr(obj, key, val)
            else:
                if hasattr(obj,key):
                    meta = obj.get_metadata(key)
                    if meta['vartypename'] == 'Array':
                        val = np.array(val)
                    setattr(obj,key,val)
        return obj
