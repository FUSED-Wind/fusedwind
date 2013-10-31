# KLD: Modifications / additions made 6/14/2013 based on use of OpenWind and NREL cost models (noted by KLD:)
# Classes added:
#    GenericWindFarmTurbineLayout
#    GenericMultipleTurbineTypesWindFarm # KLD: REMOVED after discussions with Pierre
#    GenericAEP

# P-E 17/9: Changed all the Desc into VT for following the rest of fusedwind laguage 

from numpy import interp, ndarray, array, loadtxt, log, zeros, cos, arccos, sin, nonzero, argsort, NaN, mean, ones, vstack, linspace, exp, arctan, arange
from numpy import pi, sqrt, dot, hstack
from numpy.linalg.linalg import norm
from scipy.interpolate import interp1d
from scipy.integrate import quad

from openmdao.lib.datatypes.api import VarTree, Float, Slot, Array, List, Int, Str, Dict
#from openmdao.lib.drivers.api import CaseIteratorDriver # KLD: temporary version issues
from openmdao.main.api import Driver, Run_Once
from openmdao.main.api import Component, Assembly, VariableTree, Container  # , IOInterface
from openmdao.lib.casehandlers.api import ListCaseIterator
from openmdao.main.interfaces import implements, ICaseRecorder, ICaseIterator
from openmdao.main.case import Case

# KLD - 8/29/13 separated vt and assembly into separate file
from fused_plant_vt import GenericWindTurbineVT, GenericWindTurbinePowerCurveVT, \
     ExtendedWindTurbinePowerCurveVT, GenericWindFarmTurbineLayout, \
     GenericWindRoseVT


# ------------------------------------------------------------
# Components and Assembly Base Classes


class WeibullWindRose(Component):
    """Sub class of GenericWindRoseVT, that calculate the frequency_array using a weibull distribution"""

    #direction_frequency = Array(desc='Frequency by direction sectors [n_wd]', unit='')
    #weibull_A = Array(desc='Weibull scale A by direction sectors [n_wd]', unit='m/s')
    #weibull_k = Array(desc='Weibull parameter k by direction sectors [n_wd]', unit ='')

    directions = Array(iotype='in', desc='Direction sectors angles [n_wd]', unit='deg')
    speeds = Array(iotype='in', desc='wind speeds sectors [n_ws]', unit='m/s')
    wind_rose_array = Array(iotype='in', desc='Windrose array [directions, frequency, weibull_A, weibull_k]', unit='m/s')

    wind_rose = VarTree(GenericWindRoseVT(), iotype='out', desc='A wind rose VT')

    @property
    def n_wd(self):
        """Number of wind direction bins"""
        return self.directions.shape[0]
        
    @property
    def n_ws(self):
        """Number of wind speed bins"""
        return self.speeds.shape[0]

    @property
    def d_ws(self):
        return self.speeds[1] - self.speeds[0]

    @property
    def d_wd(self):
        return self.directions[1] - self.directions[0]

    def test_consistency(self):
        """Test the consistency of the variable tree"""
        ### We assume that the speeds and directions are equally spaced
        try:
            assert linalg.norm(diff(self.speeds)-self.d_ws*ones(self.n_ws-1)) < 1.0E-8
            assert linalg.norm(diff(self.directions)-self.d_wd*ones(self.n_wd-1)) < 1.0E-8
        except:
            AssertionError('self.speeds and self.directions should be equally spaced')


        try:
            assert self.directions.mean() > 20.0
        except:
            AssertionError('The first column of wind_rose should be in degrees')

        assert isinstance(self.wind_rose_array, ndarray)
        try: 
            assert 1.0 - sum(self.wind_rose_array[:,1]) < 1.0E-3
        except:
            AssertionError('The second column of self.wind_rose_array should sum to 1.0')

    def execute(self):
        """ Construct the variable tree
        """
        self._directions =  self.wind_rose_array[:,0]
        self._direction_frequency = self.wind_rose_array[:,1]
        self._weibull_A = self.wind_rose_array[:,2]
        self._weibull_k = self.wind_rose_array[:,3]

        ### Creating the interpolation functions
        indis = range(self.wind_rose_array.shape[0])
        indis.extend([0])
        _d_wd = self._directions[1] - self._directions[0] 
        diff_dir = self._direction_frequency[indis]/_d_wd 
        directions = self._directions.tolist()
        directions.append(360.0)
        directions2 = array(directions[:])+_d_wd/2.0
        def corr_dir(d):
            if d<0.0:
                return d + 360.0
            if d>=360.0:
                return d - 360.0
            return d
        pdf_wd = interp1d(directions, diff_dir, kind='linear')           
        pdf_wd_ext = lambda d: pdf_wd(corr_dir(d))
        weibull_A = interp1d(directions, self._weibull_A[indis], kind='linear')
        weibull_k = interp1d(directions, self._weibull_k[indis], kind='linear')
        self.wind_rose.directions = self.directions
        self.wind_rose.speeds = self.speeds            

        ### Statistical functions  
        pdf_ws = lambda A,k,u: k/A * (u/A)**(k-1.0) * exp(-(u/A)**k)
        cdf_ws = lambda A,k,u, bin=1.0: exp(-(max(0.0, u-bin/2.0)/A)**k) - exp(-((u+bin/2.0)/A)**k)
        cdf_wd = lambda d, bin: quad(pdf_wd_ext, d - bin/2.0, d + bin/2.0)[0]

        ### Create the array
        self.wind_rose.frequency_array = zeros([self.n_wd, self.n_ws])

        for iwd, wd in enumerate(self.directions):
            A = weibull_A(wd)
            k = weibull_k(wd)
            P_dir = cdf_wd(wd, self.d_wd)
            for iws, ws in enumerate(self.speeds):
                self.wind_rose.frequency_array[iwd, iws] = P_dir * cdf_ws(A, k, ws, self.d_ws)

        self.test_consistency()

        ### The frequency array should never reach 1.0, because there are some high wind speeds
        ### not considered in the array.
        assert sum(self.wind_rose.frequency_array.flatten()) <= 1.0 + 1.0E-3



    # def dir_freq(self, direction, bin):
    #     """Calculate the probability to have a wind direction within a wind direction sector

    #     inputs:
    #     -------
    #         direction: mean wind direction of the sector [deg]
    #         bin: sector width [deg]

    #     output:
    #     -------
    #         probability: [-]

    #     """
    #     hbin = bin/2.0
    #     d1 = direction - hbin
    #     d2 = direction + hbin
    #     if d1<0.0:
    #         d1 = 360.0 - hbin
    #     if d2>360.0:
    #         d2 = hbin
    #     return hbin * (self.pdf_dir(d1) + self.pdf_dir(d2))
      
    # def test_consistency(self):
    #     """Test the consistency of the variable tree"""
    #     try:
    #         assert 1.0 - sum(self.direction_frequency) < 1.0E-3
    #     except:
    #         AssertionError('The sum of all the direction frequencies should be reasonably close to 1.0')




class GenericWSPosition(Component):
    """Calculate the positions where we should calculate the wind speed on the rotor"""
    wt_desc = VarTree(GenericWindTurbineVT(), iotype='in')
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
    wt_desc = VarTree(GenericWindTurbineVT(), iotype='in', desc='the geometrical description of the current turbine')
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

class GenericWindTurbine(Component):
    wt_desc = Slot(iotype='in')
    hub_wind_speed = Float(iotype='in')
    power = Float(0.0, iotype='out', desc='The wind turbine power')
    thrust = Float(0.0, iotype='out', desc='The wind turbine thrust')
    c_t = Float(0.0, iotype='out', desc='The wind turbine thrust coefficient')    


class WindTurbinePowerCurve(GenericWindTurbine):
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


class PostProcessWindRose(Component):
    cases = Slot(ICaseIterator, iotype='in')
    aep = Float(0.0, iotype='out', desc='Annual Energy Production', unit='kWh')
    energies = Array([], iotype='out', desc='The energy production per sector', unit='kWh')

class PostProcessSingleWindRose(PostProcessWindRose):
    wind_rose_array = Array([], iotype='in', desc='the wind rose')
    speeds = Array(iotype='in', desc='The different wind speeds to run [nWS]', unit='m/s')
    directions = Array(iotype='in', desc='The different wind directions to run [nWD]', unit='deg')  
    def execute(self):
        wr = WeibullWindRose()(directions=self.directions, speeds=self.speeds,
                               wind_rose_array=self.wind_rose_array).wind_rose            

        self.energies = [wr.frequency_array[c['i_wd'], c['i_ws']] \
                            * c['wf.power'] * 24 * 365 for c in self.cases]
        self.aep = sum(self.energies)

class PostProcessMultipleWindRoses(PostProcessWindRose):
    """Use a different wind rose for each wind turbine"""
    wt_layout = VarTree(GenericWindFarmTurbineLayout(), iotype='in', desc='the wind farm layout')
    speeds = Array(iotype='in', desc='The different wind speeds to run [nWS]', unit='m/s')
    directions = Array(iotype='in', desc='The different wind directions to run [nWD]', unit='deg')  

    def execute(self):
        self.aep = 0.0
        self.energies = zeros(len(self.cases))
        for i_wt in range(self.wt_layout.n_wt): 
            wr = WeibullWindRose()(directions=self.directions, speeds=self.speeds,
                                   wind_rose_array=self.wt_layout.wt_wind_roses[i_wt]).wind_rose            
            for i_c, c in enumerate(self.cases):
                i_ws = c['i_ws']
                i_wd = c['i_wd']              
                wt_aep = wr.frequency_array[i_wd, i_ws] * c['wf.wt_power'][i_wt] * 24 * 365
                self.aep += wt_aep
                self.energies[i_c] += wt_aep

from py4we.wasp import WWF, WTG, WWH
class WTDescFromWTG(Component):
    """Create a wt_desc from a .wtg WAsP file"""
    ### Inputs
    filename = Str(iotype='in', desc='The .wtg file name') 

    ### Outputs
    wt_desc = Slot(GenericWindTurbinePowerCurveVT(), iotype='out', desc='The wind turbine power curve')

    def execute(self):
        ### Reading the .wtg file
        wtg = WTG(self.filename)

        ### Filling up the VT
        self.wt_desc.power_curve = wtg.data[:,:2]
        self.wt_desc.c_t_curve = hstack([wtg.data[:,0], wtg.data[:,2]])
        self.wt_desc.cut_in_wind_speed = wtg.data[0,0]
        self.wt_desc.cut_out_wind_speed = wtg.data[-1,0]
        self.wt_desc.air_density = wtg.density

class PlantFromWWF(Component):
    """Create a Plant information from a .wwf WAsP file"""
    ### Inputs
    filename = Str(iotype='in', desc='The .wwf file name')
    wt_desc = Slot(GenericWindTurbinePowerCurveVT(), iotype='in', desc='The wind turbine power curve')

    ### Outputs
    wt_layout = VarTree(GenericWindFarmTurbineLayout(), iotype='out', desc='wind turbine properties and layout')
    wind_rose_array = Array(iotype='out', desc='Windrose array [directions, frequency, weibull_A, weibull_k]', unit='m/s')


    def execute(self):
        ### Reading the .wwf file
        wwf = WWF(self.filename)
        self.wt_layout.wt_list.append(self.wt_desc)
        # self.wt_layout.wt_wind_roses.frequency_array = 
        self.wt_layout.configure_single()

        for wt, wr in self.wwf.windroses.iteritems():
            self.wt_layout.wt_positions[i,:] = self.wwf.data[wt][:2]
            self.wt_layout.wt_wind_roses.append(wr)
            i += 1

        self.wt_layout.configure_single()
        # For practical reason we also output the first wind rose array outside the wt_layout
        self.wind_rose_array = self.wt_layout.wt_wind_roses[0]

class PlantFromWWH(Component):
    """Create a Plant information from a .wwh WAsP file"""
    ### Inputs
    filename = Str(iotype='in', desc='The .wwh file name')
    
    ### Outputs
    wt_layout = VarTree(GenericWindFarmTurbineLayout(), iotype='out', desc='wind turbine properties and layout')
    wind_rose_array = Array(iotype='out', desc='Windrose array [directions, frequency, weibull_A, weibull_k]', unit='m/s')

    def execute(self):
        ### Reading the .wwf file
        wwh = WWH(self.filename)

        self.wt_layout.wt_list = []
        self.wt_layout.wt_wind_roses = []
        self.wt_layout.wt_positions = zeros([len(wwh.windroses), 2])
        i=0
        for wt, wr in wwh.windroses.iteritems():
            self.wt_layout.wt_positions[i,:] = wwh.data[wt][:2]
            self.wt_layout.wt_wind_roses.append(wr)

            wt_desc = GenericWindTurbinePowerCurveVT()
            wt_desc.power_curve = wwh.turbine['data'][:,:2]
            wt_desc.c_t_curve = wwh.turbine['data'][:,[0,2]]
            wt_desc.cut_in_wind_speed = wwh.turbine['data'][0,0]
            wt_desc.cut_out_wind_speed = wwh.turbine['data'][-1,0]
            wt_desc.air_density = wwh.turbine['density']
            wt_desc.rotor_diameter = wwh.turbine['rotor_diameter']

            ### Note here that this allows for variable wind turbine heights
            wt_desc.hub_height = wwh.data[wt][2]
            self.wt_layout.wt_list.append(wt_desc)
            i += 1

        self.single_wind_turbine = True
        #self.wt_layout.configure_single()

        # For practical reason we also output the first wind rose array outside the wt_layout
        self.wind_rose_array = self.wt_layout.wt_wind_roses[0]


class WindRoseCaseGenerator(Component):
    speeds = Array(iotype='in', desc='The different wind speeds to run [nWS]', unit='m/s')
    directions = Array(iotype='in', desc='The different wind directions to run [nWD]', unit='deg')
    
    cases = Slot(ICaseIterator, iotype='out')
    
    ### Change this to reflect the assembly structure
    speeds_str = Str('wf.wind_speed', iotype='in')
    directions_str = Str('wf.wind_direction', iotype='in')

    def execute(self):
        cases = []
        for i_ws, ws in enumerate(self.speeds):
            for i_wd, wd in enumerate(self.directions):
                cases.append(Case(
                    inputs=[(self.directions_str, wd), 
                            (self.speeds_str, ws), 
                            ('i_ws', i_ws), ('i_wd', i_ws)]))
                
        self.cases = ListCaseIterator(cases)

