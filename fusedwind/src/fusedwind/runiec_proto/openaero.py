import os,glob,shutil

from openmdao.main.api import Component, Assembly, FileMetadata
from openmdao.lib.components.external_code import ExternalCode
from openmdao.main.datatypes.slot import Slot 

### For NREL insiders
from twister.models.FAST.runFAST import runFAST
### for others
#from twister_runFAST import runFAST

#from design_load_case import DesignLoadCase, DLCResult,  FASTRunCase, FASTDLCResult, NREL13_88_329Input, FASTRunCaseBuilder
from design_load_case import DesignLoadCase, DLCResult, FASTDLCResult,  FASTRunCaseBuilder, GenericFASTRunCaseBuilder

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
        self.basedir = os.path.join(os.getcwd(),"all_runs")
        try:
            os.mkdir(self.basedir)
        except:
            print "failed to make base dir all_runs; or it exists"
        

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
#        mycases = FASTRunCaseBuilder.genRunCases(case, case.params)
        mycases = GenericFASTRunCaseBuilder.genRunCases(case)
        return mycases

class runFASText(ExternalCode):
    """ 
        this is an ExternalCode class to take advantage of file copying stuff.
        then it finally calls the real (openMDAO-free) FAST wrapper 
    """
    input = Slot(DesignLoadCase, iotype='in')
    output = Slot(DLCResult, iotype='out')

#    fast_outputs = ['WindVxi', 'Azimuth', 'RotSpeed',  'BldPitch1',  'RotTorq', 'RotPwr',  'RotThrust', 'GenPwr' , 'GenTq' , 'OoPDefl1',
#                    'IPDefl1', 'TwstDefl1', 'RootMxc1']
    fast_outputs = ['WindVxi','RotSpeed', 'RotPwr', 'GenPwr', 'RootMxc1', 'RootMyc1', 'LSSGagMya', 'LSSGagMza', 'YawBrMxp', 'YawBrMyp','TwrBsMxt',
                    'Fair1Ten', 'Fair2Ten', 'Fair3Ten', 'Anch1Ten', 'Anch2Ten', 'Anch3Ten']
    def __init__(self, geom, atm):
        super(runFASText,self).__init__()
        self.rawfast = runFAST(geom, atm)
#        self.rawfast.setFastFile("MyFastInputTemplate.fst")  # still needs to live in "InputFilesToWrite/"
        self.rawfast.model_path = 'ModelFiles/'
        self.rawfast.template_path = "InputFilesToWrite/"
        self.rawfast.ptfm_file = "NREL5MW_Platform.ptfm"
        self.rawfast.wamit_path = "ModelFiles/WAMIT/spar"
        self.rawfast.setFastFile("NREL5MW_Monopile_Floating.fst")  # still needs to live in "InputFilesToWrite/"
        self.rawfast.setOutputs(self.fast_outputs)

#        self.stderr = "error.out"
#        self.stdout = "mystdout"

        self.basedir = os.path.join(os.getcwd(),"all_runs")
        try:
            os.mkdir(self.basedir)
        except:
            print "failed to make base dir all_runs; or it exists"
        
        self.copyback_files = True
        
        self.appname = self.rawfast.getBin()
#        template_dir = self.rawfast.getTemplateDir()
#        noiset = os.path.join(template_dir, self.rawfast.noise_template)
#        fastt = os.path.join(template_dir, self.rawfast.template_file)
        noiset = os.path.join("InputFilesToWrite", "Noise.v7.02.ipt")
        adt = os.path.join("InputFilesToWrite", "NREL5MW.ad")
        bladet = os.path.join("InputFilesToWrite", "NREL5MW_Blade.dat")
        ptfmt = os.path.join("InputFilesToWrite", "NREL5MW_Platform.ptfm")
        foundationt = os.path.join("ModelFiles", "NREL5MW_Monopile_Tower_RigFnd.dat")
        spar1 = os.path.join("ModelFiles", os.path.join("WAMIT", "spar.1"))
        spar3 = os.path.join("ModelFiles", os.path.join("WAMIT", "spar.3"))
        sparhst = os.path.join("ModelFiles", os.path.join("WAMIT", "spar.hst"))
#        fastt = os.path.join("InputFilesToWrite", "NREL5MW_Monopile_Rigid.v7.02.fst")
        fastt = os.path.join("InputFilesToWrite",  self.rawfast.fast_file)
        self.command = [self.appname, "test.fst"]
                
        self.external_files = [
            FileMetadata(path=noiset, binary=False),
            FileMetadata(path=adt, binary=False),
            FileMetadata(path=bladet, binary=False),
            FileMetadata(path=ptfmt, binary=False),
            FileMetadata(path=spar1, binary=False),
            FileMetadata(path=spar3, binary=False),
            FileMetadata(path=sparhst, binary=False),
            FileMetadata(path=foundationt, binary=False),
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
            self.results_dir = os.path.join(self.basedir, case.name)
            try:
                os.mkdir(self.results_dir)
            except:
                # print 'error creating directory', results_dir
                # print 'it probably already exists, so no problem'
                pass

            # Is this supposed to do what we're doing by hand here?
            # self.copy_results_dirs(results_dir, '', overwrite=True)

            files = glob.glob('test' + '.*')  # TODO: "test" b/c coded into runFAST.py
            for f in glob.glob('NREL' + '*.*'):  # TODO: "NREL" b/c name of template file
                files.append(f)
            files.append('error.out')  #  TODO: other files we need ?
            
            for filename in files:
#                print "wanting to copy %s to %s" % (filename, results_dir) ## for debugging, don't clobber stuff you care about!
                shutil.copy(filename, self.results_dir)

