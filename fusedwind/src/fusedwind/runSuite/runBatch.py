""" Here we will construct a cleaner version of openruniec.py.  It will simply read a table of run cases and run them. """

# main python driver to run wind load cases in a variety of ways, uses openMDAO
# Copyright NREL, 2013
# George Scott, Peter Graf, Katherined Dykes, Andrew Ning, NWTC SE team

import os
from math import pi
import numpy as np

from openmdao.main.api import Assembly, Component, FileMetadata
from openmdao.main.resource import ResourceAllocationManager as RAM
from openmdao.lib.components.external_code import ExternalCode
from openmdao.main.case import Case
from openmdao.main.datatypes.slot import Slot 
#from openmdao.lib.drivers.api import CaseIteratorDriver  ## brings in cobyla driver, which has bug on Peter's intel mac
from openmdao.lib.drivers.caseiterdriver import CaseIteratorDriver
from openmdao.lib.casehandlers.api import ListCaseRecorder, ListCaseIterator, CSVCaseRecorder
from openmdao.lib.datatypes.api import Str, Int

from openmdao.main.pbs import PBS_Allocator as PBS
from openmdao.main.resource import ResourceAllocationManager as RAM
from openmdao.util.testutil import find_python
from PeregrineClusterAllocator import ClusterAllocator


### For NREL insiders:
from twister.models.FAST.mkgeom import makeGeometry
### For the rest
#from twister_mkgeom import makeGeometry


from runAero import openFAST, designFAST
from runCase import GenericRunCaseTable

#import logging
#logging.getLogger().setLevel(logging.DEBUG)
#from openmdao.main.api import enable_console
#enable_console()

"""
The ingredients

RunCase-- description for single run of unerlying aerocode assembly (RunCases come from LoadCases in a separate step)
FASTRunCase
GenericRunCase
RunResult -- results for a single case -- so far no need for openMDAO
Turbine -- the turbine to run against -- will use "world object", generic turbine variable tree
AeroCode -- application that will run a RunCase--subclass of Assembly, represents generic aerocode, including any input building
Dispatcher/CaseAnalyzer -- sets up DLC/App sets to run in different ways (serial, parallel-cluster, parallel-grid, etc.)--wraps openMDAO CaseIterDriver
"""

#----------------------------------------------
############ Turbine -- to be fleshed out #############
## will have vartree, etc., parsable from various input files
## and different aerodcode wrappers know how to produce correct input, given
## this object
class Turbine(object):
    """ base class for turbine
    will use generic turbine variable tree under development
    For simplest, first, FAST case, we will read from a template input file"""
    def __init__(self):
        pass

#-----------------------------------------------

##############################################
class MyCode(ExternalCode):  ### for testing
    input = Int(iotype = 'in')
    def __init__(self):
        super(MyCode,self).__init__()
	self.appname = os.path.join(os.path.dirname(os.path.realpath(__file__)),'genoutfile.py')
        self.external_files = [
            FileMetadata(path="myfile.txt" , input=True, binary=False, desc='a test file')]
        self.command = ["%s" % self.appname]
        
    def execute(self):
        print "I am working on case %d" % self.input
        super(MyCode,self).execute()
        print "case %d is done\n" % self.input
################################################

###############################################
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

    def presetup_workflow(self, aerocode, turbine, cases):
        self.aerocode = aerocode
        self.turbine = turbine
        self.studycases = cases

    def configure(self):
        print "configuring dispatcher:"
        super(CaseAnalyzer, self).configure()

        driver = CaseIteratorDriver()
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
        run_case_builder = self.aerocode.getRunCaseBuilder()
        for dlc in self.studycases:
            print "building dlc for: ", dlc.x
            runcase = run_case_builder.buildRunCase_x(dlc.x, dlc.param_names, dlc)
            self.runcases.append(Case(inputs= [('runner.input', runcase)]))

        self.ws_driver.iterator = ListCaseIterator(self.runcases)
        # note NO output; collecting it by hand from file system
        
    def collect_output(self, output_params):
        print "RUNS ARE DONE:"
        print "collecting output from copied-back files (not from case recorder), see %s" % output_params['main_output_file']
        fout = file(output_params['main_output_file'], "w")
        acase = self.runcases[0]._inputs['runner.input'] ## any easier way to get this back?
        parms = acase.sample.keys()
        for p in parms:
            fout.write("%s " % p)
        fout.write("   ")
        if "output_operations" not in output_params:
            output_ops = ["max"]
        else:
            output_ops = output_params['output_operations']
        outnames = output_params['output_keys']
        for op in output_ops:
            for p in outnames:
                fout.write("%s_%s " % (op,p))
        fout.write("\n")
        for fullcase in self.runcases:
            case = fullcase._inputs['runner.input']
            for p in parms:
                val = case.sample[p]
                fout.write("%.16e " % val)
            fout.write("   ")
            results_dir = os.path.join(self.aerocode.basedir, case.name)
            for opstr in output_ops:                
                op = eval(opstr)
                result = self.aerocode.getResults(output_params['output_keys'], results_dir, operation=op)
                for val in result:
                    if (val == None):
                        fout.write("nan ")
                    else:
                        fout.write("%.16e " % val)
            fout.write("\n")
        fout.close()



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
    print os.getcwd()
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
    return val

##### dealing with input, suggestive code, playing with ideas
class RunControlInput(object):
    """ class to modularize the input"""
    def __init__(self):
    ## For now assume these are all just dictionaries
        self.turbine = {}
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
    ctrl.output['main_output_file'] = read_file_string("main_output_file", options.file_locs)
    ctrl.output['output_keys'] = read_file_string_list("output_keys", options.file_locs)
    ctrl.output['output_operations'] = read_file_string_list("output_operations", options.file_locs)

    return ctrl


###########################################################################
### "Factories" for making the appropriate objects, given the input. This is inevitable and
### separated out here.
def create_run_cases(case_params, options):
    obj = GenericRunCaseTable()
    obj.initFromFile(case_params['source_file'], verbose=True, start_at = options.start_at)
    return obj.cases

def create_turbine(turbine_params):
    """ create turbine object """
    t = Turbine()
    return t

def create_aerocode_wrapper(aerocode_params, options):
    """ create  wind code wrapper"""
    
    solver = 'FAST'
#    solver = 'HAWC2'

    if solver=='FAST':
        ## TODO, changed when we have a real turbine
        geometry, atm = makeGeometry()
        w = openFAST(geometry, atm)
    elif solver == 'HAWC2':
        w = openHAWC2(None)
        #raise NotImplementedError, "HAWC2 aeroecode wrapper not implemented in runIeC context yet"
    else:
        raise ValueError, "unknown aerocode: %s" % solver
    return w
##########

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

    if (options.cluster_allocator):
        cluster=ClusterAllocator()
        RAM.insert_allocator(0,cluster)
            
    ###  using "factory" functions to create specific subclasses (e.g. distinguish between FAST and HAWC2)
    # Then we use these to create the cases...
    cases = create_run_cases(ctrl.cases, options)
    # and a turbine
    turbine = create_turbine(ctrl.turbine)
    # and the appropriate wind code wrapper...
    aerocode = create_aerocode_wrapper(ctrl.aerocode, options)
    # and the appropriate dispatcher...
    dispatcher = create_dlc_dispatcher(ctrl.dispatcher)
    ### After this point everything should be generic, all appropriate subclass object created
    
    dispatcher.presetup_workflow(aerocode, turbine, cases)  # just makes sure parts are there when configure() is called
    dispatcher.configure()
    # Now tell the dispatcher to (setup and ) run the cases using the aerocode on the turbine.
    # calling configure() is done inside run().
    
    if (not options.norun):
        dispatcher.run()

    # TODO:  more complexity will be needed for difference between "run now" and "run later" cases.
    dispatcher.collect_output(ctrl.output)
    

if __name__=="__main__":
    rundlcs()

