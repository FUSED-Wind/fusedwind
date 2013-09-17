# KLD: Modifications / additions made 6/14/2013 based on use of OpenWind and NREL cost models (noted by KLD:)
# Classes added:
#    GenericWindFarmTurbineLayout
#    GenericMultipleTurbineTypesWindFarm # KLD: REMOVED after discussions with Pierre
#    GenericAEP


# P-E 17/9: Changed all the Desc into VT for following the rest of fusedwind laguage 

from numpy import ndarray, array, loadtxt, log, zeros, cos, arccos, sin, nonzero, argsort, NaN, mean, ones, vstack, linspace, exp, arctan, arange
from numpy import pi, sqrt, dot
from numpy.linalg.linalg import norm
from openmdao.lib.datatypes.api import VarTree, Float, Slot, Array, List, Int, Str, Dict
#from openmdao.lib.drivers.api import CaseIteratorDriver # KLD: temporary version issues
from openmdao.main.api import Driver, Run_Once
from openmdao.main.api import Component, Assembly, VariableTree, Container  # , IOInterface
from openmdao.lib.casehandlers.api import ListCaseIterator
from openmdao.main.interfaces import implements, ICaseRecorder, ICaseIterator
from openmdao.main.case import Case

# KLD - 8/29/13 separated vt and assembly into separate file
from fused_plant_vt import GenericWindTurbineVT, GenericWindTurbinePowerCurveVT, ExtendedWindTurbinePowerCurveVT, GenericWindFarmTurbineLayout
from fused_plant_comp import GenericWSPosition, HubCenterWSPosition, GenericWakeSum, GenericHubWindSpeed, GenericFlowModel, GenericWakeModel, /
                             GenericWakeModel, GenericInflowGenerator, WindTurbinePowerCurve, PostProcessWindRose

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

class AEP(GenericAEPModel): # KLD: modified to inerhit from generic AEP assembly class

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