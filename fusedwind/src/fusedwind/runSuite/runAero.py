import os,glob,shutil

from openmdao.main.api import Component, Assembly, FileMetadata
from openmdao.lib.components.external_code import ExternalCode
from openmdao.main.datatypes.slot import Slot
from openmdao.main.datatypes.instance import Instance
from openmdao.main.datatypes.api import Array, Float

from runCase import GenericRunCase, RunCase,  RunResult
#from fusedwind.runSuite.runCase import GenericRunCase, RunCase, RunResult


########### aerocode #####################
## generic aeroelastic analysis code (e.g. FAST, HAWC2,)
#class openAeroCode(Component):
class openAeroCode(Assembly):
    """ base class for application that can run a DesignLoadCase """

    ## inputs and outputs are very generic:
#    input = Slot(GenericRunCase, iotype='in')
#    output = Slot(RunResult, iotype='out')  ## never used, never even set
    input = Instance(GenericRunCase, iotype='in')
    output = Instance(RunResult, iotype='out')  ## never used, never even set

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
