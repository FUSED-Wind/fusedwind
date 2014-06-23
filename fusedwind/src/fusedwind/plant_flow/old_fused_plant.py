# KLD: Modifications / additions made 6/14/2013 based on use of OpenWind and NREL cost models (noted by KLD:)
# Classes added:
#    GenericWindFarmTurbineLayout
#    GenericMultipleTurbineTypesWindFarm # KLD: REMOVED after discussions with Pierre
#    GenericAEP

# P-E: Additional Modifications / additions made 6/17/2013
# Classes added:
#   ExtendedWindTurbinePowerCurveDesc


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
from fused_plant_vt import GenericWindTurbineDesc, GenericWindTurbinePowerCurveDesc, ExtendedWindTurbinePowerCurveDesc, GenericWindFarmTurbineLayout

# ------------------------------------------------------------
# Components and Assembly Base Classes

class GenericWSPosition(Component):
    """Calculate the positions where we should calculate the wind speed on the rotor"""
    wt_desc = VarTree(GenericWindTurbineDesc(), iotype='in')
    ws_positions = Array([], iotype='out', desc='the position [n,3] of the ws_array', unit='m')
    wt_xy = List([0.0, 0.0], iotype='in', desc='The x,y position of the wind turbine', unit='m')


class HubCenterWSPosition(GenericWSPosition):
    """
    Generate the positions at the center of the wind turbine rotor
    """
    def execute(self):
        self.ws_positions = array([[self.wt_xy[0], self.wt_xy[1], self.wt_desc.hub_height]])


class GenericWakeSum(Component):
    """
    Generic class for calculating the wake accumulation
    """
    wakes = List([], iotype='in', desc='wake contributions to rotor wind speed [nwake][n]')
    ws_array_inflow = Array([], iotype='in', desc='inflow contributions to rotor wind speed [n]', unit='m/s')

    ws_array = Array([], iotype='out', desc='the rotor wind speed [n]', unit='m/s')


class GenericHubWindSpeed(Component):
    """
    Generic class for calculating the wind turbine hub wind speed. 
    Typically used as an input to a wind turbine power curve / thrust coefficient curve.
    """
    ws_array = Array([], iotype='in', desc='an array of wind speed on the rotor', unit='m/s')

    hub_wind_speed = Float(0.0, iotype='out', desc='hub wind speed', unit='m/s')


class GenericFlowModel(Component):
    """
    Framework for a flow model
    """
    ws_positions = Array([], iotype='in', desc='the positions of the wind speeds in the global frame of reference [n,3] (x,y,z)')
    ws_array = Array([], iotype='out', desc='an array of wind speed to find wind speed')


class GenericWakeModel(GenericFlowModel):
    """
    Framework for a wake model
    """
    wt_desc = VarTree(GenericWindTurbineDesc(), iotype='in', desc='the geometrical description of the current turbine')
    wt_xy = List([0.0, 0.0], iotype='in', desc='The x,y position of the current wind turbine', unit='m')
    c_t = Float(0.0, iotype='in', desc='the thrust coefficient of the wind turbine')
    ws_array_inflow = Array([], iotype='in', desc='The inflow velocity at the ws_positions', unit='m/s')
    wind_direction = Float(0.0, iotype='in', desc='The inflow wind direction', unit='deg')
    du_array = Array([], iotype='out', desc='The deficit in m/s. Empty if only zeros', unit='m/s')
  

class GenericInflowGenerator(GenericFlowModel):
    """
    Framework for an inflow model
    """
    wind_speed = Float(0.0, iotype='in', desc='the reference wind speed')


class WindTurbinePowerCurve(Component):
    """
    wt_desc needs to contain:
        - power_curve
        - c_t_curve
        - rotor_diameter
    """
    wt_desc = Slot(iotype='in', desc='The wind turbine description')
    hub_wind_speed = Float(0.0, iotype='in', desc='Wind Speed at hub height')
    density = Float(1.225, iotype='in', desc='Air density')

    power = Float(0.0, iotype='out', desc='The wind turbine power')
    thrust = Float(0.0, iotype='out', desc='The wind turbine thrust')
    c_t = Float(0.0, iotype='out', desc='The wind turbine thrust coefficient')
    a = Float(0.0, iotype='out', desc='The wind turbine induction factor')

    def execute(self):
        #super(WindTurbinePowerCurve, self).execute()

        self.power = interp(self.hub_wind_speed, self.wt_desc.power_curve[:, 0], self.wt_desc.power_curve[:, 1])
        self.c_t = interp(self.hub_wind_speed, self.wt_desc.c_t_curve[:, 0], self.wt_desc.c_t_curve[:, 1])

        if self.hub_wind_speed < self.wt_desc.c_t_curve[:, 0].min():
            self.power = 0.0
            self.c_t = 0.0
        self._set_a()
        self._set_thrust()

    def _set_a(self):
        """
        Set the induced velocity based on the thrust coefficient
        """
        self.a = 0.5 * (1.0 - sqrt(1.0 - self.c_t))

    def _set_thrust(self):
        """
        Set the thrust based on the thrust coefficient
        """
        self.thrust = self.c_t * self.density * self.hub_wind_speed ** 2.0 * \
            self.wt_desc.rotor_diameter ** 2.0 * pi / 4.0


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


class PostProcessWindRose(Component):
    cases = Slot(ICaseIterator, iotype='in')
    aep = Float(0.0, iotype='out', desc='Annual Energy Production', unit='kWh')
    energies = Array([], iotype='out', desc='The energy production per sector', unit='kWh')

    def execute(self):
        self.energies = [c['P'] * c['wf.power'] * 24 * 365 for c in self.cases]
        self.aep = sum(self.energies)


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

# KLD: Added for Openwind
class OpenWindAEP(GenericAEPModel):

    # Inputs
    # P-E: Shouldn't it be GenericWindFarmTurbineLayout ? # KLD: irrelevant now, but we are working on this with AWS Truepower
    wt_layout = VarTree(GenericWindFarmTurbineLayout(), iotype='in', desc='properties for each wind turbine and layout')
    #losses = Float(0.0, iotype='in', desc='total plant losses from soiling, plant electrical infrastructure, etc') # KLD: TODO should be a variable tree
    #availability = Float(0.0, iotype='in', desc='plant availability') # KLD: TODO should be variable tree or collection


# KLD: version issue with caseiteratordriver
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