# main python driver to run wind load cases in a variety of ways, uses openMDAO
# Copyright NREL, 2013
# George Scott, Peter Graf, Katherined Dykes, Andrew Ning, NWTC SE team

import os

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

from openaero import openFAST
from design_load_case import  NREL13_88_329Input, NREL13_88_329FromDistn

#import logging
#logging.getLogger().setLevel(logging.DEBUG)
#from openmdao.main.api import enable_console
#enable_console()


"""
The ingredients

IECDesignLoadCase (e.g. DLC1.1) --- design load case (implies multiple runs of single code)-- so far no need for openMDAO
DLCRunCase-- description for single run of unerlying aerocode assembly
DLC output -- results for a single case -- so far no need for openMDAO
Turbine -- the turbine to run against -- will use "world object", generic turbine variable tree
App/AeroCode -- application that will run a RunCase--subclass of Assembly, represents generic aerocode, including any input building
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
        self.add('ws_driver', CaseIteratorDriver())
        self.driver.workflow.add(['ws_driver'])

        self.add('runner', self.aerocode )
#        self.add('runner', MyCode() )   # for testing
        self.ws_driver.workflow.add('runner')
        #self.runner.force_execute = True

        self.setup_cases()

        # comment this line out to run sequentially
        self.ws_driver.sequential = not self.run_parallel
        # uncomment to keep simulation directories for debugging purposes
        os.environ['OPENMDAO_KEEPDIRS'] = '1'

        print "dispatcher configured\n-------------------------------------------\n"
    
    def setup_cases(self):
        """ setup the cases """
        self.runcases = []
        ## cases should be list of DesignLoadCases
        casenum = 0
        for dlc in self.studycases:
            print 'Generating run cases for study case %s' % dlc.name
            # ask aero code to produce runcass for this study case
            allruns = self.aerocode.genRunCases(dlc)
            for runcase in allruns:
                print 'Adding Case for run case %s' % runcase.name
                # create the case
#                self.runcases.append(Case(inputs= [('runner.input', runcase)],   
#                                          outputs=['runner.output', 'runner.input']))
                self.runcases.append(Case(inputs= [('runner.input', runcase)]))
#                self.runcases.append(Case(inputs= [('runner.input', casenum)]))

                           ## vars used here need to exist in relevant (sub)-objects
                           ##(ie aerocode.input needs to exist--eg in openAeroCode) , else openMDAO throws exception
                           ## This will result in aerocode.execute() being called with self.input = runcase = relevant RunCase
                casenum += 1

        self.ws_driver.iterator = ListCaseIterator(self.runcases)
#        self.ws_driver.recorders = [ListCaseRecorder()]
#        self.ws_driver.recorders = [CSVCaseRecorder()]
#        self.ws_driver.case_outputs = ['runner.output']  ## I think the above "outputs=" in Case constructor takes care of this

        
    def collect_output(self, output_params):
        print "RUNS ARE DONE:"
        print "collecting output from copied-back files (not from case recorder)"

        fout = file(output_params['main_output_file'], "w")
        fout.write( "#Results summary: \n")
        fout.write( "#Vs Hs Tp WaveDir, TwrBsMxt \n")

        for fullcase in self.runcases:
            case = fullcase._inputs['runner.input']
            results_dir = os.path.join(self.aerocode.basedir, case.name)
            myfast = self.aerocode.runfast.rawfast
            fout.write( "%.2f %.2f %.2f %.2f   %.2f\n" % (case.ws, case.fst_params['WaveHs'], case.fst_params['WaveTp'],case.fst_params['WaveDir'], myfast.getMaxOutputValue('TwrBsMxt', directory=results_dir)))  ### this may not exist, just an example
        return

#######################################
        

#----------------------------------------------
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
    

def get_options():
    from optparse import OptionParser
    parser = OptionParser()    
#    parser.add_option("-i", "--input", dest="main_input",  type="string", default="pgcases.txt",
#                                    help="main input file")
#    parser.add_option("-j", "--input_type", dest="input_type",  type="string", default="generic_88-329",
#                                    help="input file type: one of:old_perl, generic_88-329, list. default:generic_88-329")
    parser.add_option("-i", "--input", dest="main_input",  type="string", default="dlcproto-cases.txt",
                                    help="main input file describing cases to run")
    parser.add_option("-f", "--files", dest="file_locs",  type="string", default="dlcproto-files.txt",
                                    help="main input file describing locations of template files, and output files to write")
    parser.add_option("-j", "--input_type", dest="input_type",  type="string", default="generic_88-329-distn",
                                    help="input file type: one of:old_perl, generic_88-329, list. default:generic_88-329")
    parser.add_option("-p", "--parallel", dest="run_parallel", help="run in parallel", action="store_true", default=False)
    
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

def parse_input(infile, options):
    """ input comes in a lot of categories, roughly broken into:
    -- the turbine to simulate (formerly a FAST template file)
    -- the design load cases to simulate
    -- the wind code to use
    -- the manner in which to simulate them
    -- where to find the inputs and 
    -- what to put in the outputs
    """

    ctrl = RunControlInput()
    if (options.input_type == "old_perl"):
        #  some code that parser input file from perl script into blocks corresponding
        # roughly to cases.  For first tests/exploring, perhaps support of legacy format
        # for old users
        ctrl.cases['source_type'] = "old_perl"
        ctrl.cases['source_file'] = infile
    elif (options.input_type == "generic_88-329-csv"):
        # this evolving into a csv-format that could potentially be exported form excel.
        # each row represents a single DLC from 88_329 standard
        ctrl.cases['source_type'] = "generic_88-329-csv"
        ctrl.cases['source_file'] = infile        
    elif (options.input_type == "generic_88-329-distn"):
        # this evolving into a csv-format that could potentially be exported form excel.
        # each row represents a single DLC from 88_329 standard
        ctrl.cases['source_type'] = "generic_88-329-distn"
        ctrl.cases['source_file'] = infile        
    else:
        ## strictly for testing the dispatcher 
        ctrl.cases['source_type'] = "list"
        ctrl.cases['case_list'] = [1,2,3] ## testing

    if (options.run_parallel):
        ## turns on openmdao concurrent execution stuff
        print "parallel run"
        ctrl.dispatcher['parallel'] = True

    # read file locations
    ctrl.output['main_output_file'] = read_file_string("main_output_file", options.file_locs)

    return ctrl


###########################################################################
### "Factories" for making the appropriate objects, given the input. This is inevitable and
### separated out here.
def create_load_cases(case_params):
    """ create load cases """
    if (case_params['source_type'] == "old_perl"):
        obj = PerlRuniecInput()
    #    obj.initFromLines(lns)
        obj.initFromFile(case_params['source_file'], verbose=True)
        print "found %d DLCs" % (len(obj.cases))
        for case in obj.cases:
            print "subcases to be run for %s" % case.name
            for subcase in case.subcases:
                print subcase.ws, subcase.randomseed
        cases = obj.cases
    elif (case_params['source_type'] == "generic_88-329-csv"):
        obj = NREL13_88_329Input()
        obj.initFromFile(case_params['source_file'], verbose=True)
    elif (case_params['source_type'] == "generic_88-329-distn"):
        obj = NREL13_88_329FromDistn()
        obj.initFromFile(case_params['source_file'], verbose=True)
    elif (case_params['source_type'] == "list"):
        case_list = ctrl.cases['case_list']  ## testing    
        ncases = len(case_list)  
        cases = []
        for i in range(ncases):
            case = case_list[i]
            dlc = DesignLoadCase(case)
            cases.append(dlc)  
    else:
        raise ValueError, "unknown case param source"
    
    return obj.cases

def create_turbine(turbine_params):
    """ create turbine object """
    t = Turbine()
    return t

def create_aerocode_wrapper(aerocode_params):
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
    
    cluster=ClusterAllocator()
    RAM.insert_allocator(0,cluster)

    options, arg = get_options()
    ctrl = parse_input(options.main_input, options)
    # ctrl will be just the input, but broken up into separate categories, e.g.
    # ctrl.cases, ctrl.app, ctrl.dispatch, ...
            
    ###  using "factory" functions to create specific subclasses (e.g. distinguish between FAST and HAWC2)
    # Then we use these to create the cases...
    cases = create_load_cases(ctrl.cases)
    # and a turbine
    turbine = create_turbine(ctrl.turbine)
    # and the appropriate wind code wrapper...
    aerocode = create_aerocode_wrapper(ctrl.aerocode)
    # and the appropriate dispatcher...
    dispatcher = create_dlc_dispatcher(ctrl.dispatcher)
    ### After this point everything should be generic, all appropriate subclass object created

    dispatcher.presetup_workflow(aerocode, turbine, cases)  # just makes sure parts are there when configure() is called
    # Now tell the dispatcher to (setup and ) run the cases using the aerocode on the turbine.
    # calling configure() is done inside run().

    dispatcher.run()

    # TODO:  more complexity will be needed for difference between "run now" and "run later" cases.
    dispatcher.collect_output(ctrl.output)
    

if __name__=="__main__":
    rundlcs()
    
