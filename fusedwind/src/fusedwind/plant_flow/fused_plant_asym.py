# KLD: Modifications / additions made 6/14/2013 based on use of OpenWind and NREL cost models (noted by KLD:)
# Classes added:
#    GenericWindFarmTurbineLayout
#    GenericMultipleTurbineTypesWindFarm # KLD: REMOVED after discussions with Pierre
#    GenericAEP


# P-E 17/9: Changed all the Desc into VT for following the rest of fusedwind laguage 

from numpy import ndarray, array, loadtxt, log, zeros, cos, arccos, sin, nonzero, argsort, NaN, mean, ones, vstack, linspace, exp, arctan, arange
from numpy import pi, sqrt, dot
from numpy.linalg.linalg import norm
from openmdao.lib.datatypes.api import VarTree, Float, Slot, Array, List, Int, Str, Dict, Enum
#from openmdao.lib.drivers.api import CaseIteratorDriver # KLD: temporary version issues
from openmdao.main.api import Driver, Run_Once
from openmdao.main.api import Component, Assembly, VariableTree, Container  # , IOInterface
from openmdao.lib.casehandlers.api import ListCaseIterator
from openmdao.lib.drivers.api import CaseIteratorDriver

from openmdao.main.interfaces import implements, ICaseRecorder, ICaseIterator
from openmdao.main.case import Case


# KLD - 8/29/13 separated vt and assembly into separate file
from fused_plant_vt import GenericWindTurbineVT, GenericWindTurbinePowerCurveVT, ExtendedWindTurbinePowerCurveVT, GenericWindFarmTurbineLayout
from fused_plant_comp import GenericWSPosition, HubCenterWSPosition, GenericWakeSum, GenericHubWindSpeed, GenericFlowModel, GenericWakeModel, \
                             GenericInflowGenerator, WindTurbinePowerCurve, PostProcessWindRose, PlantFromWWH, \
                             WindRoseCaseGenerator, PostProcessSingleWindRose, PostProcessMultipleWindRoses

# ------------------------------------------------------------
# Assembly Base Classes

class GenericWindFarm(Assembly):

    # Inputs:
    wind_speed = Float(iotype='in', desc='Inflow wind speed at hub height')
    wind_direction = Float(iotype='in', desc='Inflow wind direction at hub height', my_metadata='hello')
# REPLACED 14/06 KLD: replaced wt_list and wt_positions
    wt_layout = VarTree(GenericWindFarmTurbineLayout(), iotype='in', desc='wind turbine properties and layout') 

    # Outputs:
    power = Float(iotype='out', desc='Total wind farm power production', unit='W')
    thrust = Float(iotype='out', desc='Total wind farm thrust', unit='N')
    wt_power = Array([], iotype='out', desc='The power production of each wind turbine')
    wt_thrust = Array([], iotype='out', desc='The thrust of each wind turbine')

# KLD: two assemblies now - one with a single turbine and one with a list
# REMOVED 17/06 KLD: not sure this is needed based on email with Pierre 6/17/2013
#class GenericMultipleTurbineTypesWindFarm(Assembly):

    # Inputs:
    #wind_speed = Float(iotype='in', desc='Inflow wind speed at hub height')
    #wind_direction = Float(iotype='in', desc='Inflow wind direction at hub height', my_metadata='hello')
    #wt_layout = VarTree(GenericWindTurbineLayout(), iotype='in', desc='properties for each wind turbine and layout') #KLD: replaced wt_list and wt_positions

    # Outputs:
    #power = Float(iotype='out', desc='Total wind farm power production', unit='W')
    #thrust = Float(iotype='out', desc='Total wind farm thrust', unit='N')
    #wt_power = Array([], iotype='out', desc='The power production of each wind turbine')
    #wt_thrust = Array([], iotype='out', desc='The thrust of each wind turbine')

# KLD: Added to specify output; two outputs critical - gross and net aep; capacity factor could be optional 
class GenericAEPModel(Assembly):

    # Inputs
    # P-E: No common inputs? How do you specify the local wind climate?
    # KLD: OpenWind and other GIS based models have a workbook already set up for a site with all the wind flow data necessary; but I like the idea of it as an extended class

    # Outputs
    gross_aep = Float(0.0, iotype='out', desc='Gross Annual Energy Production before availability and loss impacts', unit='kWh')
    net_aep = Float(0.0, iotype='out', desc='Net Annual Energy Production after availability and loss impacts', unit='kWh')
    capacity_factor = Float(0.0, iotype='out', desc='Capacity factor for wind plant') # ??? generic or specific? will be easy to calculate, # P-E: OK


# -------------------------------------------------------------
# Implementation Assemblies

class AEPSingleWindRose(GenericAEPModel): # KLD: modified to inerhit from generic AEP assembly class

    wf = Slot(GenericWindFarm, desc='A wind farm assembly or component')

    wind_speeds = Array([], iotype='in', desc='The different wind speeds to run [nWS]', unit='m/s')
    wind_directions = Array([], iotype='in', desc='The different wind directions to run [nWD]', unit='deg')
    wind_rose = Array([], iotype='in', desc='Probability distribution of wind speed, wind direction [nWS, nWD]')

    P = Float(0.0, iotype='in', desc='Place holder for the probability')

    #aep = Float(0.0, iotype='out', desc='Annual Energy Production', unit='kWh') # KLD: part of GenericAEP
    energies = Array([], iotype='out', desc='The energy production per sector', unit='kWh')

    def configure(self):
        super(AEP, self).configure()
        self.add('driver', Run_Once())
        self.add('wind_rose_driver', CaseIteratorDriver())
        self.add('postprocess_wind_rose', PostProcessWindRose())
        self.wind_rose_driver.workflow.add('wf')
        self.wind_rose_driver.printvars = ['wf.power', 'wf.wt_power', 'wf.wt_thrust']
        self.driver.workflow.add(['wind_rose_driver', 'postprocess_wind_rose'])
        self.connect('wind_rose_driver.evaluated', 'postprocess_wind_rose.cases')
        self.connect('postprocess_wind_rose.aep', 'array_aep') # KLD: changed to array aep but net aep may be appropriate - depends on if losses/availability included
        self.connect('postprocess_wind_rose.energies', 'energies')

    def generate_cases(self):
        cases = []
        for i, ws in enumerate(self.wind_speeds):
            for j, wd in enumerate(self.wind_directions):
                cases.append(Case(inputs=[('wf.wind_direction', wd), ('wf.wind_speed', ws), ('P', self.wind_rose[i, j])]))
        return cases

    def execute(self):
        self.wind_rose_driver.iterator = ListCaseIterator(self.generate_cases())
        super(AEP, self).execute()


class WWHAEP(GenericAEPModel):
    """Class that loads a wind farm position and wind roses from a .wwh WAsP file
    and perform an AEP calculation.
    """

    wf = Slot(GenericWindFarm, desc='A wind farm assembly or component')
    wwh = Slot(PlantFromWWH)
    case_generator = Slot(WindRoseCaseGenerator)

    filename = Str(iotype='in', desc='The .wwh file name')
    wind_speeds = Array([], iotype='in', desc='The different wind speeds to run [nWS]', unit='m/s')
    wind_directions = Array([], iotype='in', desc='The different wind directions to run [nWD]', unit='deg')

    i_ws = Float(iotype='in', desc='Place holder for recorders')
    i_wd = Float(iotype='in', desc='Place holder for recorders')

    energies = Array([], iotype='out', desc='The energy production per sector', unit='kWh') 
    
    wind_rose_type = Enum('single', ('single', 'multiple'), iotype='in', desc='Are we using only one wind rose for the whole wind farm, or a different wind rose for each turbine?')
    
    def configure(self):
        super(WWHAEP, self).configure()
        self.add('wf', GenericWindFarm())
        self.add('wwh', PlantFromWWH())
        self.add('case_generator', WindRoseCaseGenerator())
        self.add('driver', Run_Once())
        self.add('wind_rose_driver', CaseIteratorDriver())

        self.wind_rose_driver.workflow.add('wf')
        self.wind_rose_driver.printvars = ['wf.power', 'wf.wt_power', 'wf.wt_thrust']
        
        ### Wiring
        self.connect('wwh.wt_layout', 'wf.wt_layout')    
        self.connect('wind_speeds', 'case_generator.speeds')
        self.connect('wind_directions', 'case_generator.directions')
        self.connect('case_generator.cases', 'wind_rose_driver.iterator')
        self.connect('filename', 'wwh.filename')
        
        ### Configure the wind rose postprocessor:
        ### Are we using only one wind rose for the whole wind farm, or a 
        ### different wind rose for each turbine?
        if self.wind_rose_type == 'single':
            self.add('postprocess_wind_rose', PostProcessSingleWindRose())
            self.connect('wwh.wind_rose_array', 'postprocess_wind_rose.wind_rose_array')
        if self.wind_rose_type == 'multiple':
            self.add('postprocess_wind_rose', PostProcessMultipleWindRoses())
            self.connect('wwh.wt_layout', 'postprocess_wind_rose.wt_layout')

        ### Common wiring for the postprocessor
        self.connect('wind_rose_driver.evaluated', 'postprocess_wind_rose.cases')
        self.connect('postprocess_wind_rose.aep', 'net_aep') 
        self.connect('postprocess_wind_rose.energies', 'energies')        
        self.connect('wind_speeds', 'postprocess_wind_rose.speeds')
        self.connect('wind_directions', 'postprocess_wind_rose.directions')
        self.driver.workflow.add(['wwh', 'case_generator', 'wind_rose_driver', 'postprocess_wind_rose'])
        
