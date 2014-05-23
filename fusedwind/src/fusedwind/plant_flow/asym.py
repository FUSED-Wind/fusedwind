from numpy import ndarray, array, loadtxt, log, zeros, cos, arccos, sin, nonzero, \
                    argsort, NaN, mean, ones, vstack, linspace, exp, arctan, arange, \
                    pi, sqrt, dot
from numpy.linalg.linalg import norm

from openmdao.lib.datatypes.api import VarTree, Float, Slot, Array, List, Int, Str, Dict, Enum
from openmdao.lib.drivers.api import CaseIteratorDriver
from openmdao.main.api import Driver
from openmdao.main.api import Component, Assembly, VariableTree, Container  # , IOInterface
from openmdao.main.interfaces import implements, ICaseRecorder, ICaseIterator
from openmdao.main.case import Case


from vt import *
from comp import *
from fusedwind.interface import base, implement_base, InterfaceSlot

# ------------------------------------------------------------
# Assembly Base Classes

# -------------------------------------------------------------
# Implementation Assemblies
@implement_base(GenericAEPModel)
class AEPWindRose(Assembly):
    """Base class to calculate Annual Energy Production (AEP) of a wind farm.
    Implement the same interface as `GenericAEPModel`
    """
    wf = InterfaceSlot(GenericWindFarm, desc='A wind farm assembly or component')
    postprocess_wind_rose = InterfaceSlot(GenericPostProcessWindRose, desc='The component taking care of postprocessing the wind rose')
    case_gen = InterfaceSlot(GenericWindRoseCaseGenerator, desc='Generate the cases from the inputs')

    #Inputs
    wind_speeds = List([], iotype='in', desc='The different wind speeds to run [nWS]', units='m/s')
    wind_directions = List([], iotype='in', desc='The different wind directions to run [nWD]', units='deg')

    #Outputs
    array_aep = Array([], iotype='out', desc='The energy production per sector [nWD, nWS]', units='kW*h')
    gross_aep = Float(iotype='out', desc='Gross Annual Energy Production before availability and loss impacts', units='kW*h')
    net_aep = Float(iotype='out', desc='Net Annual Energy Production after availability and loss impacts', units='kW*h')

    #def configure(self):
    #    configure_AEPWindRose(self)


def configure_AEPWindRose(self):
    """Generic configure method for AEPSingleWindRose and AEPMultipleWindRoses.
    After this configure method is called, some connections are hanging loose:
        - if wind_rose_type == 'single':
            - case_gen.wind_rose
        - if wind_rose_type == 'multiple':
            - case_gen.wt_layout        

    Examples
    --------

    ### In a single wind rose case:
            def configure(self):
            configure_AEPWindRose(self)
            self.replace('case_gen', SingleWindRoseCaseGenerator())
            self.replace('postprocess_wind_rose', PostProcessSingleWindRose())
            self.connect('wind_rose', 'case_gen.wind_rose')

    ### In a multiple wind rose case:
        def configure(self):
            configure_AEPWindRose(self)
            self.replace('case_gen', MultipleWindRosesCaseGenerator())
            self.replace('postprocess_wind_rose', PostProcessMultipleWindRoses())
            self.connect('wt_layout', 'case_gen.wt_layout')

    """
    self.add('driver', Driver())

    self.add('wind_rose_driver', CaseIteratorDriver())
    self.add('wf', GenericWindFarm())
    self.add('case_gen', GenericWindRoseCaseGenerator())
    self.wind_rose_driver.workflow.add('wf')
    self.wind_rose_driver.add_parameter('wf.wind_speed')
    self.wind_rose_driver.add_parameter('wf.wind_direction')
    self.wind_rose_driver.add_responses(['wf.power', 'wf.wt_power', 'wf.wt_thrust'])
    #self.wind_rose_driver.printvars = ['wf.power', 'wf.wt_power', 'wf.wt_thrust']

    self.add('postprocess_wind_rose', GenericPostProcessWindRose())


    self.driver.workflow.add(['case_gen','wind_rose_driver', 'postprocess_wind_rose'])

    #wiring
    self.connect('wind_speeds',['case_gen.wind_speeds', 'postprocess_wind_rose.wind_speeds'])
    self.connect('wind_directions',['case_gen.wind_directions', 'postprocess_wind_rose.wind_directions'])
    self.connect('case_gen.all_wind_speeds', 'wind_rose_driver.case_inputs.wf.wind_speed')
    self.connect('case_gen.all_wind_directions', 'wind_rose_driver.case_inputs.wf.wind_direction')
    self.connect('case_gen.all_frequencies', 'postprocess_wind_rose.frequencies')
    self.connect('wind_rose_driver.case_outputs.wf.power', 'postprocess_wind_rose.powers')
    self.connect('postprocess_wind_rose.net_aep', 'net_aep')
    self.connect('postprocess_wind_rose.array_aep', 'array_aep')



@implement_base(GenericAEPModel, AEPWindRose)
class AEPSingleWindRose(Assembly):
    """Base class to calculate Annual Energy Production (AEP) of a wind farm.
    Implement the same interface as `GenericAEPModel`
    """
    wf = InterfaceSlot(GenericWindFarm, desc='A wind farm assembly or component')
    postprocess_wind_rose = InterfaceSlot(GenericPostProcessWindRose, desc='The component taking care of postprocessing the wind rose')
    case_gen = InterfaceSlot(GenericWindRoseCaseGenerator, desc='Generate the cases from the inputs')


    #Inputs
    wind_speeds = List([], iotype='in', desc='The different wind speeds to run [nWS]', units='m/s')
    wind_directions = List([], iotype='in', desc='The different wind directions to run [nWD]', units='deg')
    wind_rose = Array([], iotype='in', desc='Probability distribution of wind speed, wind direction [nWD, nWS]')

    #Outputs
    array_aep = Array([], iotype='out', desc='The energy production per sector [nWD, nWS]', units='kW*h')
    gross_aep = Float(iotype='out', desc='Gross Annual Energy Production before availability and loss impacts', units='kW*h')
    net_aep = Float(iotype='out', desc='Net Annual Energy Production after availability and loss impacts', units='kW*h')

    def configure(self):
        configure_AEPWindRose(self)
        self.replace('case_gen', SingleWindRoseCaseGenerator())
        self.replace('postprocess_wind_rose', PostProcessSingleWindRose())
        self.connect('wind_rose', 'case_gen.wind_rose')

@implement_base(GenericAEPModel, AEPWindRose)
class AEPMultipleWindRoses(Assembly):
    """Base class to calculate Annual Energy Production (AEP) of a wind farm.
    Implement the same interface as `GenericAEPModel` and `AEPWindRose`
    """
    wf = InterfaceSlot(GenericWindFarm, desc='A wind farm assembly or component')
    postprocess_wind_rose = InterfaceSlot(GenericPostProcessWindRose, desc='The component taking care of postprocessing the wind rose')
    case_gen = InterfaceSlot(GenericWindRoseCaseGenerator, desc='Generate the cases from the inputs')


    #Inputs
    wind_speeds = List([], iotype='in', desc='The different wind speeds to run [nWS]', units='m/s')
    wind_directions = List([], iotype='in', desc='The different wind directions to run [nWD]', units='deg')
    wt_layout = VarTree(GenericWindFarmTurbineLayout(), iotype='in', desc='wind turbine properties and layout')

    #Outputs
    array_aep = Array([], iotype='out', desc='The energy production per sector [nWD, nWS]', units='kW*h')
    gross_aep = Float(iotype='out', desc='Gross Annual Energy Production before availability and loss impacts', units='kW*h')
    net_aep = Float(iotype='out', desc='Net Annual Energy Production after availability and loss impacts', units='kW*h')

    def configure(self):
        configure_AEPWindRose(self)
        self.replace('case_gen', MultipleWindRosesCaseGenerator())
        self.replace('postprocess_wind_rose', PostProcessMultipleWindRoses())
        self.connect('wt_layout', 'case_gen.wt_layout')

@implement_base(GenericAEPModel, AEPWindRose)
class WWHAEP(Assembly):
    """Class that loads a wind farm position and wind roses from a .wwh WAsP file
    and perform an AEP calculation.
    """

    wind_rose_type = Enum('single', ('single', 'multiple'), desc='Are we using only one wind rose for the whole wind farm, or a different wind rose for each turbine?')    

    
    # Slots
    wwh = Slot(PlantFromWWH)   

    # Interface Slots (using the @implement_base)
    wf = InterfaceSlot(GenericWindFarm, desc='A wind farm assembly or component')
    postprocess_wind_rose = InterfaceSlot(GenericPostProcessWindRose, desc='The component taking care of postprocessing the wind rose')
    case_gen = InterfaceSlot(GenericWindRoseCaseGenerator, desc='Generate the cases from the inputs')

    #Inputs
    filename = Str(iotype='in', desc='The .wwh file name')
    wind_speeds = List([], iotype='in', desc='The different wind speeds to run [nWS]', units='m/s')
    wind_directions = List([], iotype='in', desc='The different wind directions to run [nWD]', units='deg')

    #Outputs
    array_aep = Array([], iotype='out', desc='The energy production per sector [nWD, nWS]', units='kW*h')
    gross_aep = Float(iotype='out', desc='Gross Annual Energy Production before availability and loss impacts', units='kW*h')
    net_aep = Float(iotype='out', desc='Net Annual Energy Production after availability and loss impacts', units='kW*h')

    
    def configure(self):
        configure_AEPWindRose(self)
        self.add('wwh', PlantFromWWH())
        
        ### Wiring
        self.connect('wwh.wt_layout', 'wf.wt_layout')    
        self.connect('filename', 'wwh.filename')
        
        ### Configure the wind rose postprocessor:
        ### Are we using only one wind rose for the whole wind farm, or a 
        ### different wind rose for each turbine?
        if self.wind_rose_type == 'single':
            self.replace('case_gen', SingleWindRoseCaseGenerator())
            self.replace('postprocess_wind_rose', PostProcessSingleWindRose())
            self.connect('wwh.wind_rose', 'case_gen.wind_rose')
        if self.wind_rose_type == 'multiple':
            self.add('postprocess_wind_rose', PostProcessMultipleWindRoses())
            self.replace('case_gen', MultipleWindRosesCaseGenerator())
            self.connect('wwh.wt_layout', 'case_gen.wt_layout')

        ### Re-organizing the workflow
        self.driver.workflow.add(['wwh', 'case_generator', 'wind_rose_driver', 'postprocess_wind_rose'])
        
