# KLD: Modifications / additions made 6/14/2013 based on use of OpenWind and NREL cost models (noted by KLD:)
# Classes added:
#    GenericWindFarmTurbineLayout
#    GenericMultipleTurbineTypesWindFarm # KLD: REMOVED after discussions with Pierre
#    GenericAEP

# P-E 17/9: Changed all the Desc into VT for following the rest of fusedwind laguage
# P-E 5/5/14: Cleaning up, removing some comments, units were not defined properly (unit instead of units)

import numpy as np
from numpy import ndarray, array, loadtxt, log, zeros, cos, arccos, sin, nonzero, argsort, NaN, mean, ones, vstack, linspace, exp, arctan, arange
from numpy import pi, sqrt, dot, diff
from numpy.linalg.linalg import norm
from openmdao.lib.datatypes.api import  Bool, VarTree, Float, Slot, Array, List, Int, Str, Dict
from openmdao.main.api import Driver
from openmdao.main.api import Component, Assembly, VariableTree, Container  # , IOInterface
from openmdao.lib.casehandlers.api import ListCaseIterator
from openmdao.main.interfaces import implements, ICaseRecorder, ICaseIterator
from openmdao.main.case import Case

import matplotlib.pylab as plt

from fusedwind.interface import base, implement_base
import pandas as pd

# ---------------------------------------------------------
# Variable Tree Containers

@base
class GenericWindTurbineVT(VariableTree):
    hub_height = Float(desc='Machine hub height', units='m')
    rotor_diameter = Float(desc='Machine rotor diameter', units='m')
    power_rating = Float(desc='Machine power rating', units='W')

@implement_base(GenericWindTurbineVT)
class GenericWindTurbinePowerCurveVT(VariableTree):
    # GenericWindTurbineVT
    hub_height = Float(desc='Machine hub height', units='m')
    rotor_diameter = Float(desc='Machine rotor diameter', units='m')
    power_rating = Float(desc='Machine power rating', units='W')

    c_t_curve = Array(desc='Machine thrust coefficients by wind speed at hub')
    power_curve = Array(desc='Machine power output [W] by wind speed at hub')
    cut_in_wind_speed = Float(4., desc='The cut-in wind speed of the wind turbine', units='m/s')
    cut_out_wind_speed = Float(25., desc='The cut-out wind speed of the wind turbine', units='m/s')
    rated_wind_speed = Float(desc='The rated wind speed of the wind turbine', units='m/s')
    air_density = Float(desc='The air density the power curve are valid for', units='kg/(m*m*m)')

    def df(self):
        """
        Create a pandas dataframe containing the power_curve and c_t_curve.
        If the power_curve and c_t_curve do not use the same wind_speed bins, they will be concatenated with NaN.
        See pandas.concat function for more info.

        Returns
        -------
        df:     pandas.DataFrame
                wind_speed:          float
                                    The hub height wind speed [m/s]

                power:               float
                                    The wind turbine power [W]

                c_t:                 float
                                    The wind turbine thrust coefficient [-]
        """
        df = pd.DataFrame(self.power_curve, columns=['wind_speed', 'power'])
        df = df.join(pd.DataFrame(self.c_t_curve, columns=['wind_speed', 'c_t']), on='wind_speed')
        df = df.join(pd.DataFrame(self.c_p_curve, columns=['wind_speed', 'c_p']), on='wind_speed')
        return df

    @property
    def rotor_area(self):
        """The rotor area"""
        return pi * (self.rotor_diameter/2.) ** 2.

    @property
    def c_p_curve(self):
        return np.vstack([self.power_curve[:,0], self.power_curve[:,1]/(0.5 * self.air_density * self.rotor_area * self.power_curve[:,0]**3.)]).T

    def test_consistency(self):
        ## Test rotor hitting the ground
        assert self.rotor_diameter / 2. < self.hub_height
        ## Test hoover effect
        assert self.c_t_curve[:,1].max() < 1.
        ## Test power_rating
        np.testing.assert_almost_equal(self.power_curve[:,1].max(), self.power_rating)
        ## Test c_p under Betz limit

        try:
            assert self.c_p_curve[:,1].max() < 0.6
        except:
            raise Exception('Wind turbine power rating violates Betz law',self.c_p_curve)


@implement_base(GenericWindTurbineVT, GenericWindTurbinePowerCurveVT)
class ExtendedWindTurbinePowerCurveVT(VariableTree):
    # GenericWindTurbineVT
    hub_height = Float(desc='Machine hub height', units='m')
    rotor_diameter = Float(desc='Machine rotor diameter', units='m')
    power_rating = Float(desc='Machine power rating', units='W')

    # GenericWindTurbinePowerCurveVT
    c_t_curve = Array(desc='Machine thrust coefficients by wind speed at hub')
    power_curve = Array(desc='Machine power output [W] by wind speed at hub')
    cut_in_wind_speed = Float(desc='The cut-in wind speed of the wind turbine', units='m/s')
    cut_out_wind_speed = Float(desc='The cut-out wind speed of the wind turbine', units='m/s')
    rated_wind_speed = Float(desc='The rated wind speed of the wind turbine', units='m/s')
    air_density = Float(desc='The air density the power curve are valid for', units='kg/(m*m*m)')

    rpm_curve = Array(desc='Machine rpm [rpm] by wind speed at hub') # KLD: used by OpenWind but may not want to include it here
    pitch_curve = Array(desc='The wind turbine pitch curve', units='deg') # P-E: It goes hand in hand with RPM curve usually
    #dB_curve = Array(desc='Machine decibal output [dB] by wind speed at hub') # KLD: important but perhaps not for generic analysis #P-E: I have never seen these types of curves, but if you have these as data inputs, why not

class WeibullWindRoseVT(VariableTree):
    wind_directions = List(desc='Direction sectors angles [n_wd]', units='deg')
    k = List(desc='Weibull exponent k [n_wd]', units='deg')
    A = List(desc='Weibull parameter A [n_wd]', units='m/s')
    frequency = List(desc='Frequency of wind direction [n_wd]', units='deg')

    def df(self):
        """Returns a pandas.DataFrame object"""
        return pd.DataFrame(self.to_weibull_array(),
                            columns=['wind_direction', 'frequency', 'A', 'k'])

    def to_weibull_array(self):
        """Returns a weibull array [wind_direction, frequency, A, k]"""
        return np.vstack([self.wind_directions, self.frequency, self.A, self.k]).T

    ## TODO: Fix circular import issue with WeibullWindRose
    #def to_wind_rose(self, wind_directions=None, wind_speeds=None):
    #    if wind_speeds == None:
    #        wind_speeds = np.linspace(4., 25., 22)
    #    if wind_directions == None:
    #        wind_directions = self.wind_directions
    #    wwr = WeibullWindRose()
    #    return wwr(wind_directions=wind_directions,
    #               wind_speeds=wind_speeds,
    #               wind_rose_array=self.to_weibull_array()).wind_rose

class GenericWindRoseVT(VariableTree):
    wind_directions = List(desc='Direction sectors angles [n_wd]', units='deg')
    wind_speeds = List(desc='wind speeds sectors [n_ws]', units='m/s')
    frequency_array = Array(desc='Frequency by direction sectors and by wind speed sectors [n_wd, n_ws]')

    def contourf(self):
        """ Plot a contour of the wind rose """
        fig = plt.figure()
        ax = fig.add_subplot(111, polar=True)
        def mirror(d):
            out = 90.0 - d
            if out <0.0:
                return 360.0 + out
            return out
        ax.set_xticklabels([u'%d\xb0'%(mirror(d)) for d in linspace(0.0, 360.0,9)[:-1]])
        dirs = array(self.wind_directions+[360.0])
        freq = self.frequency_array[range(len(self.wind_directions))+[0],:]
        c=ax.contourf(pi/2.0-dirs* pi / 180.,
                    self.wind_speeds, freq.T, 100, cmap=plt.cm.gist_ncar_r)
        fig.colorbar(c)

    def flatten(self):
        """
        Flatten a wind rose and return an array containing the wind direction, wind speed and frequency

        Parameters
        ----------

        self        GenericWindRoseVT

        Returns
        -------
        flat_arr    numpy.ndarray([n_wd*n_ws,3])
                    array containing the [wind direction, wind speed, frequency]

        """
        return array([[wd, ws, self.frequency_array[iwd, iws]] for iwd, wd in enumerate(self.wind_direction)
                                                                for iws, ws in enumerate(self.wind_speed)])

    def df(self):
        """
        Returns a pandas.DataFrame containing the flatten array (using self.flatten() function)

        Parameters
        ----------

        self        GenericWindRoseVT

        Returns
        -------
        df          pandas.DataFrame([n_wd*n_ws,3])
                    dataframe containing the [wind direction, wind speed, frequency]
        """
        return pd.DataFrame(self.flatten(), columns=['wind_direction', 'wind_speed', 'frequency'])

#TODO: Pierre I think we need to move the configure stuff elsewhere or figure out another approach
@base
class GenericWindFarmTurbineLayout(VariableTree):
    wt_list = List(GenericWindTurbinePowerCurveVT(), desc='The wind turbine list of descriptions [n_wt]')
    wt_names = List(desc='The wind turbine list of names [n_wt]')
    wt_positions = Array(units='m', desc='Array of wind turbines attached to particular positions [n_wt, 2]')
    wt_wind_roses = List(desc='wind rose for each wind turbine position [n_wt]')
    single_wind_turbine = Bool(False, desc='Define if the layout has only one type of turbine or more')
    wind_turbine = VarTree(GenericWindTurbinePowerCurveVT(), desc='wind turbine power curve')

    @property
    def n_wt(self):
        return self.wt_positions.shape[0]

    def test_consistency(self):
        if len(self.wt_list) > 0:
            assert len(self.wt_list) == self.n_wt

        if len(self.wt_names) > 0:
            assert len(self.wt_names) == self.n_wt

        if len(self.wt_wind_roses) > 0:
            assert len(self.wt_wind_roses) == self.n_wt

    def configure_single(self):
        """
        Modify the class to adapt for single wind turbine codes.
        You can directly use self.wind_turbine instead of self.wt_list[0] .
        Note that when this function has been run there is a link between
        self.wind_turbine and self.wt_list[:]. So changing one will change
        all the other ones.
        In your code you can check if single_wind_turbine is set to True.
        """

        if len(self.wt_list) > 0:
            self.wind_turbine = self.wt_list[0]
        self.wt_list = [self.wind_turbine] * self.n_wt
        self.single_wind_turbine = True

    def create_dict(self, n):
        """
        Returns a dictionary containing the information of the n'th turbine

        Parameters
        ----------
        n:   int [0, self.n_wt]
            The index of the n'th turbine

        Returns
        -------
        di:  dict
            name:            str, optional
                            the name of the turbine contained in wt_names

            rotor_diameter:  GenericWindTurbinePowerCurveVT keys, optional
            hub_height:      ...
            ...

            x:               float
                            x position [m] from wt_positions

            y:               float
                            y position [m] from wt_positions

            wind_rose:       GenericWindRoseVT, optional
                            the wind rose of the turbine at hub height contained in wt_wind_roses
        """
        di = {}
        if len(self.wt_names) > 0:
            di['name'] = self.wt_names[n]
        if len(self.wt_list) > 0:
            for k,v in self.wt_list[n].items():
                di[k] = v
        di['x'] = self.wt_positions[n,0]
        di['y'] = self.wt_positions[n,1]
        if len(self.wt_wind_roses) > 0:
            di['wind_rose'] = self.wt_wind_roses[n]

        return di

    def df(self):
        """
        create a pandas dataframe containing all the information flatten, using the `create_dict` function

        Example:
        --------
        >>> df = generate_random_wt_layout().df()
        >>> scatter(df.x, df.y, s=df.hub_height, c=df.power_rating)
        >>> colorbar()
        """

        return pd.DataFrame([self.create_dict(n) for n in range(self.n_wt)])

@implement_base(GenericWindFarmTurbineLayout)
class ExtendedWindFarmTurbineLayout(VariableTree):
    wt_list = List(ExtendedWindTurbinePowerCurveVT(), desc='The wind turbine list of descriptions [n_wt]')
    wt_names = List(desc='The wind turbine list of names [n_wt]')
    wt_positions = Array(units='m', desc='Array of wind turbines attached to particular positions [n_wt, 2]')
    wt_wind_roses = List(desc='wind rose for each wind turbine position [n_wt]')
    single_wind_turbine = Bool(False, desc='Define if the layout has only one type of turbine or more')
    wind_turbine = VarTree(ExtendedWindTurbinePowerCurveVT(), desc='wind turbine power curve')

    @property
    def n_wt(self):
        return self.wt_positions.shape[0]

    def test_consistency(self):
        if len(self.wt_list) > 0:
            assert len(self.wt_list) == self.n_wt

        if len(self.wt_names) > 0:
            assert len(self.wt_names) == self.n_wt

        if len(self.wt_wind_roses) > 0:
            assert len(self.wt_wind_roses) == self.n_wt

    def configure_single(self):
        """
        Modify the class to adapt for single wind turbine codes.
        You can directly use self.wind_turbine instead of self.wt_list[0] .
        Note that when this function has been run there is a link between
        self.wind_turbine and self.wt_list[:]. So changing one will change
        all the other ones.
        In your code you can check if single_wind_turbine is set to True.
        """

        if len(self.wt_list) > 0:
            self.wind_turbine = self.wt_list[0]
        self.wt_list = [self.wind_turbine] * self.n_wt
        self.single_wind_turbine = True

    def create_dict(self, n):
        """
        Returns a dictionary containing the information of the n'th turbine

        Parameters
        ----------
        n   int [0, self.n_wt]
            The index of the n'th turbine

        Returns
        -------
        di  dict
            name            str, optional
                            the name of the turbine contained in wt_names

            rotor_diameter  GenericWindTurbinePowerCurveVT keys, optional
            hub_height      ...
            ...

            x               float
                            x position [m] from wt_positions

            y               float
                            y position [m] from wt_positions

            wind_rose       GenericWindRoseVT, optional
                            the wind rose of the turbine at hub height contained in wt_wind_roses
        """
        di = {}
        if len(self.wt_names) > 0:
            di['name'] = self.wt_names[n]
        if len(self.wt_list) > 0:
            for k,v in self.wt_list[n].items():
                di[k] = v
        di['x'] = self.wt_positions[n,0]
        di['y'] = self.wt_positions[n,1]
        if len(self.wt_wind_roses) > 0:
            di['wind_rose'] = self.wt_wind_roses[n]

        return di

    def df(self):
        """
        create a pandas dataframe containing all the information flatten, using the `create_dict` function

        Example:
        --------
        >>> df = generate_random_wt_layout().df()
        >>> scatter(df.x, df.y, s=df.hub_height, c=df.power_rating)
        >>> colorbar()
        """

        return pd.DataFrame([self.create_dict(n) for n in range(self.n_wt)])
