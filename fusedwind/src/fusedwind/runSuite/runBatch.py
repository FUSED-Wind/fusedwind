""" Here we will construct a cleaner version of openruniec.py.  It will simply read a table of run cases and run them. """

# main python driver to run wind load cases in a variety of ways, uses openMDAO

import os, types
from math import pi
import numpy as np

from openmdao.main.api import Assembly, Component, FileMetadata
from openmdao.main.resource import ResourceAllocationManager as RAM
from openmdao.lib.components.external_code import ExternalCode
from openmdao.main.api import Case, Component
#from openmdao.lib.drivers.api import ConnectableCaseIteratorDriver
#from openmdao.lib.drivers.api import CaseIteratorDriver  ## brings in cobyla driver, which has bug on Peter's intel mac
from openmdao.lib.drivers.caseiterdriver import ConnectableCaseIteratorDriver

from openmdao.lib.casehandlers.api import ListCaseRecorder, ListCaseIterator, CSVCaseRecorder
from openmdao.lib.datatypes.api import Str, Int, List, Bool, Slot, Instance
from openmdao.main.interfaces import ICaseIterator
from openmdao.main.pbs import PBS_Allocator as PBS
from openmdao.main.resource import ResourceAllocationManager as RAM
from openmdao.util.testutil import find_python

from PeregrineClusterAllocator import ClusterAllocator


import logging
logging.getLogger().setLevel(logging.DEBUG)
#from openmdao.main.api import enable_console
#enable_console()

# run case stuff
# run case stuff
from fusedwind.runSuite.runCase import GenericRunCaseTable
#from runCase import GenericRunCaseTable
### bug in openmdao somewhere: using "from runCase import GenericRunCaseTable" (instead of "full dotted path") gives error in ~"instance.validate" (within
### openmdao) concerning GenericRunCase vs runcase.GenericRunCase (not the same).  no idea really why.
from fusedwind.lib.base import FUSEDAssembly
from fusedwind.runSuite.runCase import IECRunCaseBaseVT, IECOutputsBaseVT
from fusedwind.runSuite.runAero import FUSEDIECBase, openAeroCode


class PostprocessIECCasesBase(Component):
    """
    Postprocess list of cases returned by a case recorder
    """

    cases = Instance(ICaseIterator, iotype='in')
    keep_dirs = Bool(False, desc='Flag to keep ObjServer directories for debugging purposes')

    def execute(self):

        for case in self.cases:
            inputs = case.get_input('runner.inputs')
            print 'processing case %s' % inputs.case_name

# frza: can't get the inheritance from FUSEDCaseIterator to work, so commented for now
# class FUSEDIECCaseIterator(FUSEDCaseIterator):

#     def configure(self):

#         super(FUSEDIECCaseIterator, self).configure()
#         # self.replace('inputs', IECRunCaseBaseVT())
#         # self.replace('outputs', IECOutputsBaseVT())
#         self.replace('runner', FUSEDIECBase())

        # self.replace()


class FUSEDIECCaseIterator(FUSEDAssembly):
    """ main driver of whole show, after input is read  wraps an openmdao CaseIteratorDriver,
    which has an openAeroCode assembly in its workflow, and whose cases are perhaps
    aero-code specific Case() objects that are sent into the aerocode via a slot variable
    """

    cases = List(iotype='in', desc='List of cases to run')

    def configure(self):
        """Configures an assembly for running with the CaseIteratorDriver"""

        self._logger.info("configuring dispatcher")

        self.add('case_driver', ConnectableCaseIteratorDriver())
        self.driver.workflow.add(['case_driver'])

        self.add('runner', FUSEDIECBase())
#        self.add('runner', openAeroCode())
#       self.add('runner', FUSEDAssembly())
        self.case_driver.workflow.add('runner')

        # Boolean for running sequentially or in parallel
        self.create_passthrough('case_driver.sequential')
        self.case_driver.recorders.append(ListCaseRecorder())

        # component for postprocessing results
        self.add('post', PostprocessIECCasesBase())
        self.driver.workflow.add('post')
        self.connect('case_driver.evaluated', 'post.cases')

        self._logger.info("dispatcher configured")

    def setup_cases(self):
        """
        setup the cases to run
        
        This method has to be called after instantiation of the class, once the ``cases``
        list has been set.
        """

        self.runcases = []
        for case in self.cases:
            self._logger.info('Adding case %s'% case.case_name)
            self.runcases.append(Case(inputs= [('runner.inputs', case)], outputs=['runner.outputs']))

        self.case_driver.iterator = ListCaseIterator(self.runcases)



## orchestrate process with CaseIteratorDriver
class CaseAnalyzer(Assembly):
    """ main driver of whole show, after input is read  wraps an openmdao CaseIteratorDriver,
    which has an openAeroCode assembly in its workflow, and whose cases are perhaps
    aero-code specific Case() objects that are sent into the aerocode via a slot variable
    """
    def __init__(self, params):
        super(CaseAnalyzer, self).__init__()
        self.run_parallel = False
        if ('parallel' in params):
            self.run_parallel = params['parallel']

    def presetup_workflow(self, aerocode, cases):
        self.aerocode = aerocode
        self.studycases = cases

    def configure(self):
        print "configuring dispatcher:"
        super(CaseAnalyzer, self).configure()

#        driver = CaseIteratorDriver()
        driver = ConnectableCaseIteratorDriver()
        self.add('ws_driver', driver)
        self.driver.workflow.add(['ws_driver'])

        self.add('runner', self.aerocode )
#        self.add('runner', MyCode() )   # for testing
        self.ws_driver.workflow.add('runner')

        self.setup_cases()

        # comment this line out to run sequentially
        self.ws_driver.sequential = not self.run_parallel
        # uncomment to keep simulation directories for debugging purposes
#        os.environ['OPENMDAO_KEEPDIRS'] = '1'

        print "dispatcher configured\n-------------------------------------------\n"
    
    def setup_cases(self):
        """ setup the cases """
        self.runcases = []
#        run_case_builder = self.aerocode.getRunCaseBuilder()
        for dlc in self.studycases:
            self.runcases.append(Case(inputs= [('runner.inputs', dlc)]))
            print "building dlc for: ", dlc.x
#            runcase = run_case_builder.buildRunCase_x(dlc.x, dlc.param_names, dlc)
#            self.runcases.append(Case(inputs= [('runner.input', runcase)]))

        self.ws_driver.iterator = ListCaseIterator(self.runcases)
        # note NO output; collecting it by hand from file system
        
    def collect_output(self, output_params):
        print "RUNS ARE DONE:"
        print "collecting output from copied-back files (not from case recorder), see %s" % output_params['main_output_file']
        fout = file(output_params['main_output_file'], "w")
        acase = self.runcases[0]._inputs['runner.inputs'] ## any easier way to get this back?
        print "processing case", acase
        parms = acase.sample.keys()
        for p in parms:
            fout.write("%s " % p)
        fout.write("   ")
        if "output_operations" not in output_params:
            output_ops = ["max"]
        else:
            output_ops = output_params['output_operations']
            if isinstance(output_ops, types.StringTypes):  ## hack to adjust if we actually did not get a list
                output_ops = [output_ops]
        outnames = output_params['output_keys']
        for op in output_ops:
            if (":" in op):
                op = op.split(":")[1]
            for p in outnames:
                fout.write("%s_%s " % (op,p))
        fout.write("\n")
        for fullcase in self.runcases:
            case = fullcase._inputs['runner.inputs']
            for p in parms:
                val = case.sample[p]
                fout.write("%.16e " % val)
            fout.write("   ")
            results_dir = os.path.join(self.aerocode.basedir, case.case_name)
            for opstr in output_ops:                
                ## we have a system where the function we do the postprocessing with can be specified in the control
                ## input file via: "output_operations" tag.
                try:
                    if (":" in opstr):
                        mod = opstr.split(":")[0]
                        opstr2 = opstr.split(":")[1]
                        op =getattr( __import__(mod, globals(), locals(), [opstr2], -1), opstr2)
                    else:
                        op = eval(opstr)  ## this gives us the "python function object" described by opstr (e.g. string "np.std"  something we can call)
                   # op is called  as op(col):R^n -> R. i.e. gets passed an array (output vs time) and produces a scalar.
                except:
                    print "ERROR: Failed to find use specified postprocessing function ", opstr

                result = self.aerocode.getResults(output_params['output_keys'], results_dir, operation=op)
                for val in result:
                    if (val == None):
                        fout.write("nan ")
                    else:
                        fout.write("%.16e " % val)
            fout.write("\n")
        fout.close()

########### 
## rest of code is options handling, input file handling.  Maybe generic enough for fusedwind.

def get_options():
    from optparse import OptionParser
    parser = OptionParser()    
    parser.add_option("-i", "--input", dest="main_input",  type="string", default="runbatch-cases.txt",
                                    help="main input file describing cases to run")
    parser.add_option("-f", "--files", dest="file_locs",  type="string", default="runbatch-control.txt",
                                    help="main input file describing locations of template files, and output fields/files to write")
    parser.add_option("-p", "--parallel", dest="run_parallel", help="run in parallel", action="store_true", default=False)
    parser.add_option("-c", "--cluster", dest="cluster_allocator", help="run using cluster allocator", action="store_true", default=False)
    parser.add_option("-n", "--norun", dest="norun", help="just process results", action="store_true", default=False)
    parser.add_option("-s", "--start_at", dest="start_at", help="index of sample to start at", type="int", default=0)
            
    (options, args) = parser.parse_args()
    return options, args

def read_file_string(tag, fname):
    lns = file(fname).readlines()
    for ln in lns:
        ln = ln.strip()
        if ln == "" or ln[0] == "#":
            pass
        else:
            ln = ln.split("=")
            if ln[0].strip() == tag:
                val = ln[1].strip().strip("\"").strip("\'")
                return val
    return None

def read_file_string_list(tag, fname):
    ln = read_file_string(tag, fname)
    if (ln == None):
        raise ValueError, "key %s not found in %s" % (tag, fname)
    ln = ln.strip()
    val = ln.split()
    if (len(val) == 1):
        return val[0]  # it's not a list, so just return the value
    else:
        return val  # otherwise we want the list

def parse_key_val_file_all(fname):
    """ parse key/value file, some entries might be _lists_ of strings """

    output = {}

    lns = file(fname).readlines()
    for ln in lns:
        ln = ln.strip()
        if ln != "" and ln[0] != "#":
            ln = ln.split("=")
            if (len(ln) > 1):
                tag = ln[0].strip()
                val = ln[1].strip()
                val = val.split("#")[0]
                val = val.strip().strip("\"").strip("\'")
                val2 = val.split()
                if (len(val2) > 1):
                    output[tag] = [v.strip().strip("\"").strip("\'") for v in val2]
                else:
                    output[tag] = val

#    output['main_output_file'] = read_file_string("main_output_file", fname)
#    output['output_keys'] = read_file_string_list("output_keys", fname)
#    output['output_operations'] = read_file_string_list("output_operations", fname)

    return output


##### dealing with input(?) --- probably overkill
class RunControlInput(object):
    """ class to modularize the input"""
    def __init__(self):
    ## For now assume these are all just dictionaries
        self.cases = {}
        self.aerocode = {}
        self.dispatcher = {}
        self.paths = {}
        self.output = {}


def parse_input(options):
    """ input comes in a lot of categories, roughly broken into:
    -- the turbine to simulate (formerly a FAST template file)
    -- the design load cases to simulate
    -- the wind code to use
    -- the manner in which to simulate them
    -- where to find the inputs and 
    -- what to put in the outputs
    """

    ctrl = RunControlInput()
    ctrl.cases['source_file'] = options.main_input        

    if (options.run_parallel):
        ## turns on openmdao concurrent execution stuff
        print "parallel run"
        ctrl.dispatcher['parallel'] = True

    ## input is raw cases

    # read file locations
    ctrl.output = parse_key_val_file_all(options.file_locs)

    return ctrl



#### below here can all be considered "testing code" now.  Driver app we really use is assembled in custom way from above parts (and others).
# See AeroelasticSE/iecApp.py
####

###########################################################################
### "Factories" for making the appropriate objects, given the input. This is inevitable and
### separated out here.
def create_run_cases(case_params, options):
    obj = GenericRunCaseTable()
    obj.initFromFile(case_params['source_file'], verbose=True, start_at = options.start_at)
    return obj.cases

def create_turbine(turbine_params):
    """ create turbine object """
    t = None
    return t

def create_aerocode_wrapper(aerocode_params, output_params, options):
    """ create  wind code wrapper"""
    
    solver = 'FAST'
#    solver = 'HAWC2'

    if solver=='FAST':
        ## TODO, changed when we have a real turbine
        # aero code stuff: for constructors
        from AeroelasticSE.FusedFAST import openFAST 
        w = openFAST(output_params)  ## need better name than output_params
#        w = openFAST(None, atm, output_params)  ## need better name than output_params
        w.setOutput(output_params)
    elif solver == 'HAWC2':
        w = openHAWC2(None)
        raise NotImplementedError, "HAWC2 aeroecode wrapper not implemented in runBatch.py yet"
    else:
        raise ValueError, "unknown aerocode: %s" % solver
    return w

# dispatcher is a little more generic, for far only one of them. will _use_ different true
# dispatchers, i.e. parallel interfaces to different systems.
def create_dlc_dispatcher(dispatch_params):
    """ create dispatcher
    dispatcher originally meant to signify role as handling _how_ the computations are done
    E.g., we could have a parallel dispatcher, etc. For now this just handled by a flag, all the work is done
    in openmdao, ie ## so far there is actually only one type of dispatcher. 
    """
    d = CaseAnalyzer(dispatch_params)
    return d
##
###########################################

def rf(col):
    ## mv this and
    from rainflow import rain_one
    # wrapper for rainflow algorithm
    val = rain_one(col, 5)
    return val

## main function that opens input, runs cases, writes output, ie. whole thing.
def rundlcs():
    """ 
    run the whole process, including startup and shutdown
    to do:
    parse input
    create load cases
    create app assembly
    create dispatcher
    send cases and app to dispatcher
    run cases
    collect and save output
    """
    

    options, arg = get_options()
    ctrl = parse_input(options)
    # ctrl will be just the input, but broken up into separate categories, e.g.
    # ctrl.cases, ctrl.app, ctrl.dispatch, ...

    # work in progress; running efficiently at NREL.
    if (options.cluster_allocator):
        cluster=ClusterAllocator()
        RAM.insert_allocator(0,cluster)
            
    ###  using "factory" functions to create specific subclasses (e.g. distinguish between FAST and HAWC2)
    # Then we use these to create the cases...
    cases = create_run_cases(ctrl.cases, options)
    # and a turbine---never used this "stub"
#    turbine = create_turbine(ctrl.turbine)
    # and the appropriate wind code wrapper...
    aerocode = create_aerocode_wrapper(ctrl.aerocode, ctrl.output, options)
    # and the appropriate dispatcher...
    dispatcher = create_dlc_dispatcher(ctrl.dispatcher)
    ### After this point everything should be generic, all appropriate subclass object created
    # # # # # # # # # # #

    dispatcher.presetup_workflow(aerocode, cases)  # just makes sure parts are there when configure() is called
    dispatcher.configure()
    # Now tell the dispatcher to (setup and ) run the cases using the aerocode on the turbine.
    # calling configure() is done inside run(). but now it is done already (above), too.
    
    # norun does not write directories, but it does set us up to process them if they already exist
    if (not options.norun):
        dispatcher.run()

    # TODO:  more complexity will be needed for difference between "run now" and "run later" cases.
    dispatcher.collect_output(ctrl.output)
    

if __name__=="__main__":
    rundlcs()

