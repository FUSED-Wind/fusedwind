
from fusedwind.lib.base import FUSEDAssembly
from openmdao.main.api import Component, Case
from openmdao.main.interfaces import ICaseIterator
from openmdao.lib.datatypes.api import Bool, List, Instance
from openmdao.lib.drivers.api import ConnectableCaseIteratorDriver
from openmdao.lib.casehandlers.api import ListCaseRecorder, ListCaseIterator

class PostprocessCasesBase(Component):
    """
    Postprocess list of cases returned by a case recorder
    """

    cases = Instance(ICaseIterator, iotype='in')
    keep_dirs = Bool(False, desc='Flag to keep ObjServer directories for debugging purposes')


class FUSEDCaseIterator(FUSEDAssembly):
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

        self.add('runner', FUSEDAssembly())
        self.case_driver.workflow.add('runner')

        # Boolean for running sequentially or in parallel
        self.create_passthrough('case_driver.sequential')
        self.case_driver.recorders.append(ListCaseRecorder())

        # component for postprocessing results
        self.add('post', PostprocessCasesBase())
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
            self.runcases.append(Case(inputs= [('runner.inputs', case)], outputs=['runner.outputs']))

        self.case_driver.iterator = ListCaseIterator(self.runcases)

        # uncomment to keep simulation directories for debugging purposes
        # os.environ['OPENMDAO_KEEPDIRS'] = '1'
