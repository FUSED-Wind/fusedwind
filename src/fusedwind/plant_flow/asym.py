from numpy import ndarray, array, loadtxt, log, zeros, cos, arccos, sin, nonzero, \
    argsort, NaN, mean, ones, vstack, linspace, exp, arctan, arange, \
    pi, sqrt, dot
from numpy.linalg.linalg import norm

from openmdao.lib.datatypes.api import VarTree, Float, Slot, Array, List, Int, Str, Dict, Enum
from openmdao.lib.drivers.api import CaseIteratorDriver
from openmdao.main.api import Driver
from openmdao.main.api import Component, Assembly, VariableTree, Container
from openmdao.main.interfaces import implements, ICaseRecorder, ICaseIterator
from openmdao.main.case import Case


from vt import *
from comp import *
from fusedwind.interface import base, implement_base, InterfaceSlot, \
    FUSEDAssembly, configure_base

from fusedwind.fused_helper import fused_autodoc

# ------------------------------------------------------------
# Assembly Base Classes


@base
class BaseAEPModel(Assembly):
    """
    Most basic AEP class which only provides key AEP outputs - flexible for use with any energy production model
    """

    # Outputs
    gross_aep = Float(0.0, iotype='out', units='kW*h',
        desc='Gross Annual Energy Production before availability and loss impacts')
    net_aep = Float(0.0, iotype='out', units='kW*h',
        desc='Net Annual Energy Production after availability and loss impacts')
    capacity_factor = Float(0.0, iotype='out',
        desc='Capacity factor for wind plant')

@implement_base(BaseAEPModel)
class BaseAEPModel_NoFlow(Assembly):
    """
    Basic AEP model that provides base outputs but also assumes no flow model is used so that loss factors and turbine number must be used to get full plant energy output
    """

    # parameters
    array_losses = Float(0.059, iotype='in', desc='energy losses due to turbine interactions - across entire plant')
    other_losses = Float(0.0, iotype='in', desc='energy losses due to blade soiling, electrical, etc')
    availability = Float(0.94, iotype='in', desc='average annual availbility of wind turbines at plant')
    turbine_number = Int(100, iotype='in', desc='total number of wind turbines at the plant')
    machine_rating = Float(5000.0, iotype='in', desc='machine rating of turbine')

    # Outputs
    gross_aep = Float(0.0, iotype='out', units='kW*h',
        desc='Gross Annual Energy Production before availability and loss impacts')
    net_aep = Float(0.0, iotype='out', units='kW*h',
        desc='Net Annual Energy Production after availability and loss impacts')
    capacity_factor = Float(0.0, iotype='out',
        desc='Capacity factor for wind plant')

# -------------------------------------------------------------
# Implementation Assemblies


@implement_base(BaseAEPModel)
class AEPWindRose(Assembly):

    """Base class to calculate Annual Energy Production (AEP) of a wind farm.
    Implement the same interface as `BaseAEPModel`
    """
    wf = InterfaceSlot(GenericWindFarm,
        desc='A wind farm assembly or component')
    postprocess_wind_rose = InterfaceSlot(GenericPostProcessWindRose,
        desc='The component taking care of postprocessing the wind rose')
    case_gen = InterfaceSlot(GenericWindRoseCaseGenerator,
        desc='Generate the cases from the inputs')

    # Inputs
    wind_speeds = List([], iotype='in', units='m/s',
        desc='The different wind speeds to run [nWS]')
    wind_directions = List([], iotype='in', units='deg',
        desc='The different wind directions to run [nWD]')

    # Outputs
    array_aep = Array([], iotype='out', units='kW*h',
        desc='The energy production per sector [nWD, nWS]')
    gross_aep = Float(iotype='out', units='kW*h',
        desc='Gross Annual Energy Production before availability and loss impacts')
    net_aep = Float(iotype='out', units='kW*h',
        desc='Net Annual Energy Production after availability and loss impacts')
    capacity_factor = Float(0.0, iotype='out',
        desc='Capacity factor for wind plant')

    # def configure(self):
    #    configure_AEPWindRose(self)


@configure_base(AEPWindRose)
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
            self.add('case_gen', SingleWindRoseCaseGenerator())
            self.add('postprocess_wind_rose', PostProcessSingleWindRose())
            configure_AEPWindRose(self)
            self.connect('wind_rose', 'case_gen.wind_rose')

    ### In a multiple wind rose case:
        def configure(self):
            self.add('case_gen', MultipleWindRosesCaseGenerator())
            self.add('postprocess_wind_rose', PostProcessMultipleWindRoses())
            configure_AEPWindRose(self)
            self.connect('wt_layout', 'case_gen.wt_layout')

    """
    # Adding
    self.add('driver', Driver())
    self.add('wind_rose_driver', CaseIteratorDriver())

    self.add_default('wf', GenericWindFarm())
    self.add_default('case_gen', GenericWindRoseCaseGenerator())
    self.add_default('postprocess_wind_rose', GenericPostProcessWindRose())

    # Drivers configuration
    self.wind_rose_driver.workflow.add('wf')
    self.wind_rose_driver.add_parameter('wf.wind_speed')
    self.wind_rose_driver.add_parameter('wf.wind_direction')
    self.wind_rose_driver.add_responses(['wf.power', 'wf.wt_power',
                                         'wf.wt_thrust'])

    self.driver.workflow.add(['case_gen', 'wind_rose_driver',
                              'postprocess_wind_rose'])

    # wiring
    self.connect('wind_speeds', [
                 'case_gen.wind_speeds',
                 'postprocess_wind_rose.wind_speeds'])
    self.connect('wind_directions', [
                 'case_gen.wind_directions',
                 'postprocess_wind_rose.wind_directions'])
    self.connect('case_gen.all_wind_speeds',
                 'wind_rose_driver.case_inputs.wf.wind_speed')
    self.connect('case_gen.all_wind_directions',
                 'wind_rose_driver.case_inputs.wf.wind_direction')
    self.connect('case_gen.all_frequencies',
                 'postprocess_wind_rose.frequencies')
    self.connect('wind_rose_driver.case_outputs.wf.power',
                 'postprocess_wind_rose.powers')
    self.connect('postprocess_wind_rose.net_aep', 'net_aep')
    self.connect('postprocess_wind_rose.array_aep', 'array_aep')


@implement_base(BaseAEPModel, AEPWindRose)
class AEPSingleWindRose(FUSEDAssembly):

    """Base class to calculate Annual Energy Production (AEP) of a wind farm.
    Implement the same interface as `BaseAEPModel`
    """
    wf = InterfaceSlot(GenericWindFarm,
        desc='A wind farm assembly or component')
    postprocess_wind_rose = InterfaceSlot(GenericPostProcessWindRose,
        desc='The component taking care of postprocessing the wind rose')
    case_gen = InterfaceSlot(GenericWindRoseCaseGenerator,
        desc='Generate the cases from the inputs')

    # Inputs
    wind_speeds = List([], iotype='in', units='m/s',
        desc='The different wind speeds to run [nWS]')
    wind_directions = List([], iotype='in', units='deg',
        desc='The different wind directions to run [nWD]')
    wind_rose = Array([], iotype='in',
        desc='Probability distribution of wind speed, wind direction [nWD, nWS]')

    # Outputs
    array_aep = Array([], iotype='out', units='kW*h',
        desc='The energy production per sector [nWD, nWS]')
    gross_aep = Float(iotype='out', units='kW*h',
        desc='Gross Annual Energy Production before availability and loss impacts')
    net_aep = Float(iotype='out', units='kW*h',
        desc='Net Annual Energy Production after availability and loss impacts')
    capacity_factor = Float(0.0, iotype='out',
        desc='Capacity factor for wind plant')

    def configure(self):
        self.add('case_gen', SingleWindRoseCaseGenerator())
        self.add('postprocess_wind_rose', PostProcessSingleWindRose())
        configure_AEPWindRose(self)
        self.connect('wind_rose', 'case_gen.wind_rose')




@implement_base(BaseAEPModel, AEPWindRose)
class AEPMultipleWindRoses(FUSEDAssembly):

    """Base class to calculate Annual Energy Production (AEP) of a wind farm.
    Implement the same interface as `BaseAEPModel` and `AEPWindRose`
    """
    wf = InterfaceSlot(GenericWindFarm,
        desc='A wind farm assembly or component')
    postprocess_wind_rose = InterfaceSlot(GenericPostProcessWindRose,
        desc='The component taking care of postprocessing the wind rose')
    case_gen = InterfaceSlot(GenericWindRoseCaseGenerator,
        desc='Generate the cases from the inputs')

    # Inputs
    wind_speeds = List([], iotype='in', units='m/s',
        desc='The different wind speeds to run [nWS]')
    wind_directions = List([], iotype='in', units='deg',
        desc='The different wind directions to run [nWD]')
    wt_layout = VarTree(GenericWindFarmTurbineLayout(), iotype='in',
        desc='wind turbine properties and layout')

    # Outputs
    array_aep = Array([], iotype='out', units='kW*h',
        desc='The energy production per sector [nWD, nWS]')
    gross_aep = Float(iotype='out', units='kW*h',
        desc='Gross Annual Energy Production before availability and loss impacts')
    net_aep = Float(iotype='out', units='kW*h',
        desc='Net Annual Energy Production after availability and loss impacts')
    capacity_factor = Float(0.0, iotype='out',
        desc='Capacity factor for wind plant')
    wt_aep = Array([], iotype='out', units='kW*h',
        desc='The energy production per turbine [nWT]')

    def configure(self):
        self.add('case_gen', MultipleWindRosesCaseGenerator())
        self.add('postprocess_wind_rose', PostProcessMultipleWindRoses())
        configure_AEPWindRose(self)
        self.connect('wt_layout', 'case_gen.wt_layout')
        self.disconnect('wind_rose_driver.case_outputs.wf.power',
                     'postprocess_wind_rose.powers')
        self.connect('wind_rose_driver.case_outputs.wf.wt_power',
                     'postprocess_wind_rose.powers')
        self.connect('postprocess_wind_rose.wt_aep', 'wt_aep')

