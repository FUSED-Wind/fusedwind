import os,glob,shutil

from openmdao.main.api import Component, Assembly, FileMetadata
from openmdao.lib.components.external_code import ExternalCode
from openmdao.main.datatypes.slot import Slot 

from twister.models.FAST.runFAST import runFAST
from twister.models.FAST import mkgeom

#from design_load_case import DesignLoadCase, DLCResult,  FASTRunCase, FASTDLCResult, NREL13_88_329Input, FASTRunCaseBuilder
from design_load_case import DesignLoadCase, DLCResult, FASTDLCResult,  FASTRunCaseBuilder

########### aerocode #####################
## generic aeroelastic analysis code (e.g. FAST, HAWC2,)
#class openAeroCode(Component):
class openAeroCode(Assembly):
    """ base class for application that can run a DesignLoadCase """

    ## inputs and outputs are very generic:
    input = Slot(DesignLoadCase, iotype='in')
    output = Slot(DLCResult, iotype='out')

    def __init__(self):
        super(openAeroCode, self).__init__()


class openFAST(openAeroCode):

    def __init__(self, geom, atm):
        self.runfast = runFASText(geom, atm)
        super(openFAST, self).__init__()
        print "openFAST __init__"

    def configure(self):
        print "openFAST configure"
        self.add('runner', self.runfast)
        self.driver.workflow.add(['runner'])
        self.connect('input', 'runner.input')
        self.connect('runner.output', 'output')        

    def execute(self):
        print "openFAST.execute(), case = ", self.input
        super(openFAST, self).execute()
 
    def genRunCases(self,case):
        """ from, e.g., 'DLC1.1', generate FAST specific RunCases """
#        mycases = FASTRunCaseBuilder.genRunCases(case, {"@WindSpeeds":["11,", "13"], "NumSeeds":"2", "NumWavePer":"3"})
        mycases = FASTRunCaseBuilder.genRunCases(case, case.params)
        return mycases

class runFASText(ExternalCode):
    """ 
        this is an ExternalCode class to take advantage of file copying stuff.
        then it finally calls the real (openMDAO-free) FAST wrapper 
    """
    input = Slot(DesignLoadCase, iotype='in')
    output = Slot(DLCResult, iotype='out')

    def __init__(self, geom, atm):
        super(runFASText,self).__init__()
        self.rawfast = runFAST(geom, atm)
        
        self.basedir = os.getcwd()
        self.copyback_files = True
        
        self.appname = self.rawfast.getBin()
#        template_dir = self.rawfast.getTemplateDir()
#        noiset = os.path.join(template_dir, self.rawfast.noise_template)
#        fastt = os.path.join(template_dir, self.rawfast.template_file)
        noiset = os.path.join("InputFilesToWrite", "Noise.v7.02.ipt")
        fastt = os.path.join("InputFilesToWrite", "NREL5MW_Monopile_Rigid.v7.02.fst")
        self.command = [self.appname, "test.fst"]
                
        self.external_files = [
            FileMetadata(path=noiset, binary=False),
            FileMetadata(path=fastt, binary=False)]
        for nm in self.rawfast.getafNames():  
            self.external_files.append(FileMetadata(path="%s" % nm, binary=False))
        
                
    def execute(self):
        # call runFast to just write the inputs
        case = self.input

        ### key moment:
        # transfer info from case to FAST object
        ws=case.ws
        if ('RotSpeed' in case.fst_params):
            rpm = case.fst_params['RotSpeed']
        else:
            rpm = 12.03
        self.rawfast.set_ws(ws)
        self.rawfast.set_rpm(rpm)
        # rest of input delivered by line-by-line dictionary case.fst_params in write_inputs()
        
#        self.rawfast.set_wind_file(case.windfile)  ## slows us down a lot, delete for testing; also,
        # overrides given wind speed; but this is what is in RunIEC.pl
        ### end of key moment!

        # let the FAST object write its inputs
        self.rawfast.write_inputs(case.fst_params)
        
        # execute fast via superclass' system call, command we already set up
        super(runFASText,self).execute()

        # gather output directly
        self.output = FASTDLCResult(self)
        self.rawfast.computeMaxPower()
        
        # also, copy all the output and input back "home"
        if (self.copyback_files):
            results_dir = os.path.join(self.basedir, case.name)
            try:
                os.mkdir(results_dir)
            except:
                # print 'error creating directory', results_dir
                # print 'it probably already exists, so no problem'
                pass

            # Is this supposed to do what we're doing by hand here?
            # self.copy_results_dirs(results_dir, '', overwrite=True)

            files = glob.glob('test' + '.*')  # TODO: "test" b/c coded into runFAST.py
            files.append('error.out')  #  TODO: other files we need ?
            
            for filename in files:
#                print "wanting to copy %s to %s" % (filename, results_dir) ## for debugging, don't clobber stuff you care about!
                shutil.copy(filename, results_dir)

