import numpy as np
from numpy import ndarray, array, loadtxt, log, zeros, cos, arccos, sin, nonzero
from numpy import argsort, NaN, mean, ones, vstack, linspace, exp, arctan, arange
from numpy import pi, sqrt, dot, diff, swapaxes, repeat, atleast_2d, radians
from numpy import einsum
from numpy.linalg.linalg import norm
from numpy.testing import assert_equal
from scipy.interpolate import interp1d
from scipy.integrate import quad
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

    # def df(self):
    #     """
    #     Create a pandas dataframe containing the power_curve and c_t_curve.
    #     If the power_curve and c_t_curve do not use the same wind_speed bins, they will be concatenated with NaN.
    #     See pandas.concat function for more info.
    #
    #     Returns
    #     -------
    #     df:     pandas.DataFrame
    #             wind_speed:          float
    #                                 The hub height wind speed [m/s]
    #
    #             power:               float
    #                                 The wind turbine power [W]
    #
    #             c_t:                 float
    #                                 The wind turbine thrust coefficient [-]
    #     """
    #     df = pd.DataFrame(self.power_curve, columns=['wind_speed', 'power'])
    #     df = df.join(pd.DataFrame(self.c_t_curve, columns=['wind_speed', 'c_t']), on='wind_speed', lsuffix='c_t')
    #     df = df.join(pd.DataFrame(self.c_p_curve, columns=['wind_speed', 'c_p']), on='wind_speed', lsuffix='c_p')
    #     return df

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



def weibull2freq_array(wind_directions, wind_speeds, weibull_array, cut_in=4.0, cut_out=25.0):
    """Calculates the frequency_array using a weibull distribution

    Parameters
    ----------
    wind_directions = List(iotype='in', units='deg',
        desc='Direction sectors angles [n_wd]')
    wind_speeds = List(iotype='in', units='m/s',
        desc='wind speeds sectors [n_ws]')
    weibull_array = Array([], iotype='in', units='m/s',
        desc='Windrose array [wind_directions, frequency, weibull_A, weibull_k]')
    cut_in = Float(4.0, iotype='in',
        desc='The cut-in wind speed of the wind turbine')
    cut_out = Float(25.0, iotype='in',
        desc='The cut-out wind speed of the wind turbine')

    Returns
    -------
    wind_rose = frequency array [n_wd, n_ws]
    """

    # TODO: optimize this function. It's very slow.

    n_wd, n_ws = len(wind_directions), len(wind_speeds)

    # Calculate the new wind_rose"""
    if len(weibull_array) == 0:
        return

    #Test the consistency of the inputs. This will be optimized away in production"""
    assert len(weibull_array) > 0,\
        'wind_rose_array is empty: %r' % weibull_array
    assert len(wind_speeds) > 0,\
        'wind_speeds is empty: %r' % wind_speeds
    assert len(wind_directions) > 0,\
        'wind_directions is empty: %r' % wind_directions
    assert isinstance(weibull_array, ndarray),\
        'The wind rose array is a ndarray of 4 columns'
    assert weibull_array.shape[1] == 4,\
        'wind_rose_array = array([wind_directions, frequency, weibull_A, weibull_k])'
    assert mean(wind_directions) > 20.0,\
        'Wind direction should be given in degrees'
    assert weibull_array[:, 0].mean() > 20.0,\
        'The first column of wind_rose should be in degrees'
    assert 1.0 - sum(weibull_array[:, 1]) < 1.0E-3,\
        'The second column of wind_rose_array should sum to 1.0'


    _directions = weibull_array[:, 0]
    _direction_frequency = weibull_array[:, 1]
    _weibull_A = weibull_array[:, 2]
    _weibull_k = weibull_array[:, 3]

    # Creating the interpolation functions
    indis = range(weibull_array.shape[0])
    indis.extend([0])
    _d_wd = _directions[1] - _directions[0]
    diff_dir = _direction_frequency[indis] / _d_wd
    directions = _directions.tolist() + [360.0]

    def corr_dir(d):
        if d < 0.0:
            return d + 360.0
        if d >= 360.0:
            return d - 360.0
        return d
    pdf_wd = interp1d(directions, diff_dir, kind='linear')
    pdf_wd_ext = lambda d: pdf_wd(corr_dir(d))
    weibull_A = interp1d(directions, _weibull_A[indis], kind='linear')
    weibull_k = interp1d(directions, _weibull_k[indis], kind='linear')


    # Statistical functions
    pdf_ws = lambda A, k, u: k / A * \
        (u / A) ** (k - 1.0) * exp(-(u / A) ** k)
    #cdf_ws = lambda A,k,u, bin=1.0: exp(-(max(0.0, u-bin/2.0)/A)**k) - exp(-((u+bin/2.0)/A)**k)
    cdf_ws = lambda A, k, u0, u1: exp(-(u0 / A) ** k) - exp(-(u1 / A) ** k)
    # TODO: Fine tune this epsrel
    cdf_wd = lambda wd0, wd1: quad(pdf_wd_ext, wd0, wd1, epsrel=0.1)[0]

    # Create the array
    frequency_array = zeros([n_wd, n_ws])

    for iwd, wd in enumerate(wind_directions):

        A = weibull_A(wd)
        k = weibull_k(wd)

        # We include all the wind directions between each wind directions
        if iwd == 0:
            wd0 = 0.5 * (wind_directions[-1] + wd + 360)
        else:
            wd0 = 0.5 * (wind_directions[iwd - 1] + wd)
        if iwd == len(wind_directions) - 1:
            wd1 = 0.5 * (wind_directions[0] + wd + 360)
        else:
            wd1 = 0.5 * (wind_directions[iwd + 1] + wd)

        if wd0 > wd1:  # deal with the 360-0 issue
            p_dir = cdf_wd(wd0, 359.99) + cdf_wd(0.0, wd1)
        else:
            p_dir = cdf_wd(wd0, wd1)
        # print 'between', wd0, wd1, p_dir
        for iws, ws in enumerate(wind_speeds):
            if iws == 0:  # We include all the cases from cut_in
                ws0 = cut_in
            else:
                ws0 = 0.5 * (wind_speeds[iws - 1] + ws)
            if iws == len(wind_speeds) - 1:
                ws1 = cut_out
            else:
                ws1 = 0.5 * (wind_speeds[iws + 1] + ws)
            ws0 = min(cut_out, max(cut_in, ws0))
            ws1 = min(cut_out, max(cut_in, ws1))

            frequency_array[iwd, iws] = p_dir * cdf_ws(A, k, ws0, ws1)

    #Test the consistency of the outputs. This will be optimized away in production"""
    assert sum(frequency_array.flatten()) <= 1.0 + 1.0E-3, \
        'The frequency array should never reach 1.0, because there are some high wind speeds not considered in the array.'

    return frequency_array




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

    def __init__(self, wind_directions=None, wind_speeds=None, frequency_array=None, weibull_array=None):
        """
        Initialise the wind rose with frequency_array or a weibull distribution [optional]
        :param wind_directions: list[nwd]
        :param wind_speeds: list[nws]
        :param frequency_array: numpy.ndarray[nwd, nws]
        :param weibull_array: numpy.ndarray[nwd, 4]
                              The weibull distribution
        :return: self
        """
        super(GenericWindRoseVT, self).__init__()

        if weibull_array is not None:
            assert isinstance(weibull_array, np.ndarray), 'weibull_array should be a ndarray'
            assert weibull_array.shape[1] == 4, 'weibull_array.shape should be [nwd, 4]'
            self.weibull_array = weibull_array

        if wind_speeds is not None:
            assert isinstance(wind_speeds, list), 'wind_speed should be a list'
            self.wind_speeds = wind_speeds
        else:
            #default value = [4., 5., ...,25.]
            self.wind_speeds = np.linspace(4., 25., 22).tolist()

        if wind_directions is not None:
            assert isinstance(wind_directions, list), 'wind_directions should be a list'
            self.wind_directions = wind_directions
        elif weibull_array is not None:
            # Using the wind direction defined in the weibull array
            self.wind_directions = weibull_array[:,0].tolist()

        if frequency_array is not None:
            assert isinstance(frequency_array, np.ndarray), \
                    'frequency_array should be a ndarray'
            assert frequency_array.shape == [len(wind_directions), len(wind_speeds)], \
                    'frequency_array.shape should be [nwd, nws]'
            self.frequency_array = frequency_array

        if weibull_array is not None:
            self.change_resolution(self.wind_directions, self.wind_speeds, force=True)


    def change_resolution(self, wind_directions=None, wind_speeds=None, force=False):
        """
        Change the resolution of the wind rose on the basis of existing the weibull_array
        :param wind_directions: list[nwd], optional
        :param wind_speeds: list[nws], optional
        :param force: Bool, forces to change the resolution
        """
        changed = False
        if wind_directions is not None:
            if not np.array_equal(self.wind_directions, wind_directions):
                changed = True
            self.wind_directions = wind_directions

        if wind_speeds is not None:
            if not np.array_equal(self.wind_speeds, wind_speeds):
                changed = True
            self.wind_speeds = wind_speeds

        if changed or force:
            self.frequency_array = weibull2freq_array(self.wind_directions, self.wind_speeds, self.weibull_array)


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


# @base
# class old_GenericWindFarmTurbineLayout(VariableTree):
#     wt_list = List(GenericWindTurbinePowerCurveVT(), desc='The wind turbine list of descriptions [n_wt]')
#     wt_names = List(desc='The wind turbine list of names [n_wt]')
#     wt_positions = Array(units='m', desc='Array of wind turbines attached to particular positions [n_wt, 2]')
#     wt_wind_roses = List(desc='wind rose for each wind turbine position [n_wt]')
#     single_wind_turbine = Bool(False, desc='Define if the layout has only one type of turbine or more')
#     wind_turbine = VarTree(GenericWindTurbinePowerCurveVT(), desc='wind turbine power curve')
#
#     @property
#     def n_wt(self):
#         return self.wt_positions.shape[0]
#
#     def test_consistency(self):
#         if len(self.wt_list) > 0:
#             assert len(self.wt_list) == self.n_wt
#
#         if len(self.wt_names) > 0:
#             assert len(self.wt_names) == self.n_wt
#
#         if len(self.wt_wind_roses) > 0:
#             assert len(self.wt_wind_roses) == self.n_wt
#
#     def configure_single(self):
#         """
#         Modify the class to adapt for single wind turbine codes.
#         You can directly use self.wind_turbine instead of self.wt_list[0] .
#         Note that when this function has been run there is a link between
#         self.wind_turbine and self.wt_list[:]. So changing one will change
#         all the other ones.
#         In your code you can check if single_wind_turbine is set to True.
#         """
#
#         if len(self.wt_list) > 0:
#             self.wind_turbine = self.wt_list[0]
#         self.wt_list = [self.wind_turbine] * self.n_wt
#         self.single_wind_turbine = True
#
#     def create_dict(self, n):
#         """
#         Returns a dictionary containing the information of the n'th turbine
#
#         Parameters
#         ----------
#         n:   int [0, self.n_wt]
#             The index of the n'th turbine
#
#         Returns
#         -------
#         di:  dict
#             name:            str, optional
#                             the name of the turbine contained in wt_names
#
#             rotor_diameter:  GenericWindTurbinePowerCurveVT keys, optional
#             hub_height:      ...
#             ...
#
#             x:               float
#                             x position [m] from wt_positions
#
#             y:               float
#                             y position [m] from wt_positions
#
#             wind_rose:       GenericWindRoseVT, optional
#                             the wind rose of the turbine at hub height contained in wt_wind_roses
#         """
#         di = {}
#         if len(self.wt_names) > 0:
#             di['name'] = self.wt_names[n]
#         if len(self.wt_list) > 0:
#             for k,v in self.wt_list[n].items():
#                 di[k] = v
#         di['x'] = self.wt_positions[n,0]
#         di['y'] = self.wt_positions[n,1]
#         if len(self.wt_wind_roses) > 0:
#             di['wind_rose'] = self.wt_wind_roses[n]
#
#         return di
#
#     def df(self):
#         """
#         create a pandas dataframe containing all the information flatten, using the `create_dict` function
#
#         Example:
#         --------
#         >>> df = generate_random_wt_layout().df
#         >>> scatter(df.x, df.y, s=df.hub_height, c=df.power_rating)
#         >>> colorbar()
#         """
#
#         return pd.DataFrame([self.create_dict(n) for n in range(self.n_wt)])
#
# @implement_base(GenericWindFarmTurbineLayout)
# class ExtendedWindFarmTurbineLayout(GenericWindFarmTurbineLayout):
#     wt_list = List(ExtendedWindTurbinePowerCurveVT(), desc='The wind turbine list of descriptions [n_wt]')
#     wt_names = List(desc='The wind turbine list of names [n_wt]')
#     wt_positions = Array(units='m', desc='Array of wind turbines attached to particular positions [n_wt, 2]')
#     wt_wind_roses = List(desc='wind rose for each wind turbine position [n_wt]')
#     single_wind_turbine = Bool(False, desc='Define if the layout has only one type of turbine or more')
#     wind_turbine = VarTree(ExtendedWindTurbinePowerCurveVT(), desc='wind turbine power curve')


implement_base(GenericWindTurbineVT, GenericWindTurbinePowerCurveVT)
class WTPC(GenericWindTurbinePowerCurveVT):
    """ A GenericWindTurbinePowerCurveVT with a name, position and wind rose
    """
    # GenericWindTurbineVT
    hub_height = Float(desc='Machine hub height', units='m')
    rotor_diameter = Float(desc='Machine rotor diameter', units='m')
    power_rating = Float(desc='Machine power rating', units='W')

    # GenericWindTurbinePowerCurveVT
    c_t_curve = Array(desc='Machine thrust coefficients by wind speed at hub')
    power_curve = Array(desc='Machine power output [W] by wind speed at hub')
    cut_in_wind_speed = Float(4., desc='The cut-in wind speed of the wind turbine', units='m/s')
    cut_out_wind_speed = Float(25., desc='The cut-out wind speed of the wind turbine', units='m/s')
    rated_wind_speed = Float(desc='The rated wind speed of the wind turbine', units='m/s')
    air_density = Float(desc='The air density the power curve are valid for', units='kg/(m*m*m)')

    # WTPC
    name = Str(desc='The wind turbine name')
    position = Array(shape=(2,), desc='The UTM position of the turbine', units='m')
    wind_rose = VarTree(GenericWindRoseVT(), desc='The wind turbine wind rose')

    def __init__(self, **kwargs):
        """Initialise the variable tree with the right inputs"""
        super(WTPC, self).__init__()
        for k,v in kwargs.iteritems():
            if k in self.list_vars():
                setattr(self, k, v)

@base
class GenericWindFarmTurbineLayout(VariableTree):
    wt_names = List([], desc='The wind turbine list of names [n_wt]')

    def __init__(self, wt_list=[]):
        """Initialise the leafes of the GenericWindFarmTurbineLayout based on the wt_list
        Parameters
        ----------
            wt_list:    list(WTPC)
                        list of Wind turbine object
        """
        super(GenericWindFarmTurbineLayout, self).__init__()
        for wt in wt_list:
            self.add_wt(wt)

    def add_wt(self, wt):
        """ Add a turbine to the layout tree, append the name at the end of wt_names
        Parameters
        ----------
            wt: WTPC
                Wind turbine object
        """
        wt.name = wt.name.replace('-','_')
        self.add(wt.name, VarTree(wt))
        self.wt_names.append(wt.name)

    def _wt_list(self, attr=None):
        """ Get a list of leafs
        Parameters
        ----------
            attr:   str, default=None
                    The attribute of the leaf to list
        Returns
        -------
        list
        """
        if attr:
            return [getattr(getattr(self, wtn), attr) for wtn in self.wt_names]
        else:
            return [getattr(self, wtn) for wtn in self.wt_names]

    @property
    def wt_list(self):
        """backward compatibility access to wt_list
        :returns a list of wind turbine object
        """
        return self._wt_list()

    def wt_array(self, attr=None):
        """ Get an array of attributes of the leafs
        Parameters
        ----------
            attr:   str, default=None
                    The attribute of the leaf to list
        Returns
        -------
         numpy.ndarray
        """
        return np.array(self._wt_list(attr))


    @property
    def n_wt(self):
        return len(self.wt_names)

    @property
    def wt_positions(self):
        """backward compatibility access to wt_positions """
        return self.wt_array(attr='position')

    @wt_positions.setter
    def wt_positions(self, value):
        """backward compatibility access to wt_positions
        update the position of the wind farm layout
        :param value: ndarray([nwt, 2])
        :return: nothing
        """
        assert_equal(value.shape, [self.n_wt, 2])
        for iwt, wt in enumerate(self.wt_list):
            wt.position = value[iwt,:]

    @property
    def wt_wind_roses(self):
        """backward compatibility access to wt_wind_roses: wind rose for each wind turbine position list[n_wt]"""
        return self._wt_list(attr='wind_rose')


    # def test_consistency(self):
    #     if len(self.wt_list) > 0:
    #         assert len(self.wt_list()) == self.n_wt
    #
    #     if len(self.wt_names) > 0:
    #         assert len(self.wt_names) == self.n_wt
    #
    #     if len(self.wt_wind_roses) > 0:
    #         assert len(self.wt_wind_roses) == self.n_wt

    # def configure_single(self):
    #     """
    #     Modify the class to adapt for single wind turbine codes.
    #     You can directly use self.wind_turbine instead of self.wt_list[0] .
    #     Note that when this function has been run there is a link between
    #     self.wind_turbine and self.wt_list[:]. So changing one will change
    #     all the other ones.
    #     In your code you can check if single_wind_turbine is set to True.
    #     """
    #
    #     if len(self.wt_list) > 0:
    #         self.wind_turbine = self.wt_list[0]
    #     self.wt_list = [self.wind_turbine] * self.n_wt
    #     self.single_wind_turbine = True

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
        if self.n_wt > 0:
            for k,v in self.wt_list[n].items():
                di[k] = v
        di['x'] = self.wt_positions[n,0]
        di['y'] = self.wt_positions[n,1]
        if len(self.wt_wind_roses) > 0:
            di['wind_rose'] = self.wt_wind_roses[n]

        return di

    @property
    def df(self):
        """
        create a pandas dataframe containing all the information flatten, using the `create_dict` function

        :rtype : pandas.DataFrame

        Example:
        --------
        >>> df = generate_random_wt_layout().df
        >>> scatter(df.x, df.y, s=df.hub_height, c=df.power_rating)
        >>> colorbar()
        """

        return pd.DataFrame([self.create_dict(n) for n in range(self.n_wt)])

    def turbineDistance(self,wd):
        """
        Computes the WT to WT distance in flow coordinates
        ranks the WT starting from the most upstream turbine

        Inputs
        ----------
        wd (float): Wind direction in degrees

        Outputs
        ----------
        distFlowCoord: Vector from iWT to jWT: self.vectWTtoWT[:,i,j]
        idWT (int np.array): turbine index array
        """

        # 2D Vector from iWT to jWT: self.vectWTtoWT[:,i,j]   [2,n_wt,n_wt]
        vectWTtoWT = swapaxes([self.wt_positions.T-repeat(atleast_2d \
                     (self.wt_positions.T[:,i]).T,self.n_wt,axis=1) \
                     for i in range(self.n_wt)],0,1)

        angle = radians(270.-wd)
        ROT = array([[cos(angle), sin(angle)], \
                    [-sin(angle), cos(angle)]])
        distFlowCoord = einsum('ij,jkl->ikl',ROT,vectWTtoWT)

        nDownstream = [(distFlowCoord[0,i,:]<0).sum() for i in range(self.n_wt)]
        idWT = array(nDownstream).argsort().argsort()
        return distFlowCoord, nDownstream, idWT

    def plot(self,wd=0.):
        x = self.wt_positions.T[0,:]/1000
        y = self.wt_positions.T[1,:]/1000
        dist,nDownstream, idWT = self.turbineDistance(wd)
        fig, ax = plt.subplots()
        ax.scatter(x,y,c='black')
        for i in range(self.n_wt):
            ax.annotate(idWT[i], (x[i],y[i]))
        ax.set_xlabel('x [km]')
        ax.set_ylabel('y [km]')
        return fig

if __name__ == '__main__':

    from fusedwind.plant_flow.generate_fake_vt import *

    WindPlant = generate_random_wt_layout(nwt=10)
    fig = WindPlant.plot(wd=270.)
    plt.show()
