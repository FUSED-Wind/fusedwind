import os,glob,shutil

from openmdao.main.api import Component, Assembly, FileMetadata
from openmdao.lib.components.external_code import ExternalCode
from openmdao.main.datatypes.slot import Slot
from openmdao.main.datatypes.api import Array, Float, VarTree, Str

#from AeroelasticSE.runFAST import runFAST
#from AeroelasticSE.runTurbSim import runTurbSim
#from AeroelasticSE.mkgeom import makeGeometry
from runCase import GenericRunCase, RunCase, FASTRunCaseBuilder, FASTRunCase, RunResult, FASTRunResult

from fusedwind.runSuite.runCase import IECRunCaseBaseVT, IECOutputsBaseVT
# from fusedwind.lib.base import FUSEDAssembly



class FUSEDIECBase(Assembly):
    """base class for simulation codes running an IEC load basis"""

    inputs = VarTree(IECRunCaseBaseVT(), iotype='in', desc='')
    outputs = VarTree(IECOutputsBaseVT(), iotype='out', desc='')
    results_dir = Str('all_runs', iotype='in', desc='Directory for simulation results files')

    def __init__(self):
        super(FUSEDIECBase, self).__init__()

        self.results_dir = os.path.join(os.getcwd(), self.results_dir)
        try:
            os.mkdir(self.basedir)
        except:
            self._logger.warning('failed to make results dir all_runs; or it exists')



# Peter's code 
class openAeroCode(Assembly):
    """ base class for application that can run a DesignLoadCase """

    ## inputs and outputs are very generic:
    input = Slot(GenericRunCase, iotype='in')
    output = Slot(RunResult, iotype='out')  ## never used, never even set

    def __init__(self):
        super(openAeroCode, self).__init__()
        self.basedir = os.path.join(os.getcwd(),"all_runs")
        try:
            os.mkdir(self.basedir)
        except:
            print "failed to make base dir all_runs; or it exists"

    def getRunCaseBuilder(self):
        raise unimplementedError, "this is a \"virtual\" class!"

    def getResults(self, keys, results_dir):
        raise unimplementedError, "this is a \"virtual\" class!"

    def setOutput(self, output_params):
        raise unimplementedError, "this is a \"virtual\" class!"        
    

class openFAST(openAeroCode):
    def __init__(self, geom, atm, filedict):
        self.runfast = runFASText(geom, atm, filedict)
        super(openFAST, self).__init__()
        print "openFAST __init__"

    def getRunCaseBuilder(self):
        return FASTRunCaseBuilder()

    def configure(self):
        print "openFAST configure"
        self.add('runner', self.runfast)
        self.driver.workflow.add(['runner'])
        self.connect('input', 'runner.input')
        self.connect('runner.output', 'output')        

    def execute(self):
        print "openFAST.execute(), case = ", self.input
        run_case_builder = self.getRunCaseBuilder()
        dlc = self.input 
        self.input = run_case_builder.buildRunCase_x(dlc.x, dlc.param_names, dlc)
        super(openFAST, self).execute()

    def getResults(self, keys, results_dir, operation=max):
        myfast = self.runfast.rawfast        
        col = myfast.getOutputValues(keys, results_dir)
#        print "getting output for keys=", keys
        vals = []
        for i in range(len(col)):
            c = col[i]
            try:
                val = operation(c)
            except:
                val = None
            vals.append(val)
        return vals

    def setOutput(self, output_params):
        self.runfast.set_fast_outputs(output_params['output_keys'])
        print "set FAST output:", output_params['output_keys']

class designFAST(openFAST):        
    """ base class for cases where we have parametric design (e.g. dakota),
    corresponding to a driver that are for use within a Driver that "has_parameters" """
    x = Array(iotype='in')   ## exact size of this gets filled in study.setup_cases(), which call create_x, below
    f = Float(iotype='out')
    # need some mapping back and forth
    param_names = []

    def __init__(self,geom,atm,filedict):
        super(designFAST, self).__init__(geom,atm,filedict)

    def create_x(self, size):
        """ just needs to exist and be right size to use has_parameters stuff """
        self.x = [0 for i in range(size)]

    def dlc_from_params(self,x):
        print x, self.param_names, self.dlc.name
        case = FASTRunCaseBuilder.buildRunCase_x(x, self.param_names, self.dlc)
        print case.fst_params
        return case

    def execute(self):
        # build DLC from x, if we're using it
        print "in design code. execute()", self.x
        self.input = self.dlc_from_params(self.x)
        super(designFAST, self).execute()
        myfast = self.runfast.rawfast
        self.f = myfast.getMaxOutputValue('TwrBsMxt', directory=os.getcwd())

class runFASText(ExternalCode):
    """ 
        this is an ExternalCode class to take advantage of file copying stuff.
        then it finally calls the real (openMDAO-free) FAST wrapper 
    """
    input = Slot(RunCase, iotype='in')
    output = Slot(RunResult, iotype='out')  ## never used, never even set

    ## just a template, meant to be reset by caller
    fast_outputs = ['WindVxi','RotSpeed', 'RotPwr', 'GenPwr', 'RootMxc1', 'RootMyc1', 'LSSGagMya', 'LSSGagMza', 'YawBrMxp', 'YawBrMyp','TwrBsMxt',
                    'TwrBsMyt', 'Fair1Ten', 'Fair2Ten', 'Fair3Ten', 'Anch1Ten', 'Anch2Ten', 'Anch3Ten'] 

    def __init__(self, geom, atm, filedict):
        super(runFASText,self).__init__()
        self.rawfast = runFAST(geom, atm)
#        self.rawfast.write_blade_af = True

        print "runFASText init(), filedict = ", filedict

        # probably overridden by caller
        self.rawfast.setOutputs(self.fast_outputs)

        self.basedir = os.path.join(os.getcwd(),"all_runs")
        try:
            os.mkdir(self.basedir)
        except:
            print "failed to make base dir all_runs; or it exists"
        
        self.copyback_files = True
        
        if ("FAST_exe" in filedict):
            FAST_exe = filedict["FAST_exe"]
            ## hack straight in to set app
            self.rawfast.fastexe = FAST_exe

        FAST_model_path= 'ModelFiles'
        if ("FAST_model_path" in filedict):
            FAST_model_path = filedict["FAST_model_path"]
        self.rawfast.model_path = FAST_model_path

        FAST_template_path = "InputFilesToWrite"
        if ("FAST_template_path" in filedict):
            FAST_template_path = filedict["FAST_template_path"]
        self.rawfast.template_path = FAST_template_path

        TurbSim_template_path = "InputFilesToWrite"
        if ("TurbSim_template_path" in filedict):
            TurbSim_template_path = filedict["TurbSim_template_path"]

        self.rawfast.ptfm_file = "NREL5MW_Platform.ptfm"
        if ("FAST_ptfm_file" in filedict):
            FAST_ptfm_file = filedict["FAST_ptfm_file"]
            self.rawfast.ptfm_file = FAST_ptfm_file

        FAST_WAMIT_path = os.path.join("ModelFiles","WAMIT")
        if ("FAST_WAMIT_path" in filedict):
            FAST_WAMIT_path = filedict["FAST_WAMIT_path"]
        self.rawfast.wamit_path = os.path.join(FAST_WAMIT_path, "spar")

        FAST_fast_file = "NREL5MW_Monopile_Floating.fst"
        if ("FAST_fast_file" in filedict):
            FAST_fast_file = filedict["FAST_fast_file"]
        self.rawfast.setFastFile(FAST_fast_file)  # still needs to live in FAST_template_path

        FAST_noise_file = "Noise.v7.02.ipt"
        if ("FAST_noise_file" in filedict):
            FAST_noise_file = filedict["FAST_noise_file"]
        self.rawfast.noise_file = FAST_noise_file

        FAST_foundation_file = "NREL5MW_Monopile_Tower_RigFnd.dat"
        if ("FAST_foundation_file" in filedict):
            FAST_foundation_file = filedict["FAST_foundation_file"]
        self.rawfast.foundation_file = FAST_foundation_file

        TurbSim_template_file = "turbsim_template.inp"
        if ("TurbSim_template_file" in filedict):
            TurbSim_template_file = filedict["TurbSim_template_file"]

        FAST_ad_file = "NREL5MW.ad"
        if ("FAST_ad_file" in filedict):
            FAST_ad_file = filedict["FAST_ad_file"]
        self.rawfast.ad_file = FAST_ad_file

        FAST_blade_file = "NREL5MW_Blade.dat"
        if ("FAST_blade_file" in filedict):
            FAST_blade_file = filedict["FAST_blade_file"]
        self.rawfast.blade_file = FAST_blade_file

        FAST_ptfm_file = "NREL5MW_Platform.ptfm"
        if ("FAST_ptfm_file" in filedict):
            FAST_ptfm_file = filedict["FAST_ptfm_file"]
        self.rawfast.ptfm_file = FAST_ptfm_file

        self.appname = self.rawfast.getBin()
#        template_dir = self.rawfast.getTemplateDir()
#        noiset = os.path.join(template_dir, self.rawfast.noise_template)
#        fastt = os.path.join(template_dir, self.rawfast.template_file)
        noiset = os.path.join(FAST_template_path, FAST_noise_file)
        adt = os.path.join(FAST_template_path, FAST_ad_file)
        bladet = os.path.join(FAST_template_path, FAST_blade_file)
        ptfmt = os.path.join(FAST_template_path, FAST_ptfm_file)
        foundationt = os.path.join(FAST_model_path, FAST_foundation_file)
        spar1 = os.path.join(FAST_WAMIT_path,"spar.1")
        spar3 = os.path.join(FAST_WAMIT_path,"spar.3")
        sparhst = os.path.join(FAST_WAMIT_path,"spar.hst")

#        fastt = os.path.join("InputFilesToWrite", "NREL5MW_Monopile_Rigid.v7.02.fst")
        fastt = os.path.join(FAST_template_path,  self.rawfast.fast_file)
        tst = os.path.join(TurbSim_template_path, TurbSim_template_file)
        self.full_turbsim_template_path = tst
        self.command = [self.appname, "test.fst"]
                
        self.rawfast.readAD()

        self.external_files = [
            FileMetadata(path=noiset, binary=False),
            FileMetadata(path=adt, binary=False),
            FileMetadata(path=bladet, binary=False),
            FileMetadata(path=ptfmt, binary=False),
            FileMetadata(path=spar1, binary=False),
            FileMetadata(path=spar3, binary=False),
            FileMetadata(path=sparhst, binary=False),
            FileMetadata(path=foundationt, binary=False), 
            FileMetadata(path=tst, binary=False),
            FileMetadata(path=fastt, binary=False)]
        for nm in self.rawfast.getafNames():  
            print "adding af name:", nm
            self.external_files.append(FileMetadata(path="%s" % nm, binary=False))

    def set_fast_outputs(self,fst_out):
        self.fast_outputs = fst_out
        self.rawfast.setOutputs(self.fast_outputs)
                
    def execute(self):
        # call runFast to just write the inputs
        case = self.input

        ### key moment:
        # transfer info from case to FAST object
        ws=case.fst_params['Vhub']
        if ('RotSpeed' in case.fst_params):
            rpm = case.fst_params['RotSpeed']
        else:
            rpm = 12.03
        self.rawfast.set_ws(ws)
        self.rawfast.set_rpm(rpm)
        ##### rest of input delivered by line-by-line dictionary case.fst_params in write_inputs() ####
        ### SHOULD ALL BE DONE THIS WAY, no special cases  TODO ###
        
#        self.rawfast.set_wind_file(case.windfile)  ## slows us down a lot, delete for testing; also,
        # overrides given wind speed; but this is what is in RunIEC.pl
        ### end of key moment!

        tmax = 2  ## should not be hard default ##
        if ('TMax' in case.fst_params):  ## Note, this gets set via "AnalTime" in input files--FAST peculiarity ? ##
            tmax = case.fst_params['TMax']

        # run TurbSim to generate the wind:        
        ### Turbsim: this should be higher up the chain in the "assembly": TODO
        ts = runTurbSim()
        ts.template_file = self.full_turbsim_template_path
        ts.set_dict({"URef": ws, "AnalysisTime":tmax, "UsableTime":tmax})
        ts.execute() ## cheating to not use assembly ##
        self.rawfast.set_wind_file("turbsim_test.wnd")
        ### but look how easy it is just to stick it here ?!

        # let the FAST object write its inputs
        self.rawfast.write_inputs(case.fst_params)
        
        ### actually execute FAST (!!) via superclass' system call, command we already set up
        super(runFASText,self).execute()
        ###

        # gather output directly
        self.output = FASTRunResult(self)
#        self.rawfast.computeMaxPower()
        
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



def run_test():
    geometry, atm = makeGeometry()
    w = designFAST(geometry, atm)

    ## sort of hacks to save this info
    w.param_names = ['Vhub']
    w.dlc = FASTRunCase("runAero-testcase", {}, None)
    print "set aerocode dlc"
    ##

    res = []
    for x in range(10,16,2):
        w.x = [x]
        w.execute()
        res.append([ w.dlc.name, w.param_names, w.x, w.f])
    for r in res:
        print r

if __name__=="__main__":
    run_test()
