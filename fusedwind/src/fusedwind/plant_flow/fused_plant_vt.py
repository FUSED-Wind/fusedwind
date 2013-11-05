# KLD: Modifications / additions made 6/14/2013 based on use of OpenWind and NREL cost models (noted by KLD:)
# Classes added:
#    GenericWindFarmTurbineLayout
#    GenericMultipleTurbineTypesWindFarm # KLD: REMOVED after discussions with Pierre
#    GenericAEP

# P-E 17/9: Changed all the Desc into VT for following the rest of fusedwind laguage 


from numpy import ndarray, array, loadtxt, log, zeros, cos, arccos, sin, nonzero, argsort, NaN, mean, ones, vstack, linspace, exp, arctan, arange
from numpy import pi, sqrt, dot, diff
from numpy.linalg.linalg import norm
from openmdao.lib.datatypes.api import  Bool, VarTree, Float, Slot, Array, List, Int, Str, Dict
#from openmdao.lib.drivers.api import CaseIteratorDriver # KLD: temporary version issues
from openmdao.main.api import Driver, Run_Once
from openmdao.main.api import Component, Assembly, VariableTree, Container  # , IOInterface
from openmdao.lib.casehandlers.api import ListCaseIterator
from openmdao.main.interfaces import implements, ICaseRecorder, ICaseIterator
from openmdao.main.case import Case

import matplotlib.pylab as plt

# ---------------------------------------------------------
# Variable Tree Containers

class GenericWindTurbineVT(VariableTree):
    hub_height = Float(desc='Machine hub height', unit='m')
    rotor_diameter = Float(desc='Machine rotor diameter', unit='m')
# ADDED 14/06 KLD: added power rating, a key wind turbine variable used in a lot of analyses #P-E: good point, then we might also need the corresponding rated wind speeds? # KLD: we could but I'm not sure its necessary and probably wont be used by many models
    power_rating = Float(desc='Machine power rating', unit='W') # KLD: 
#REMOVED 17/06 P-E
    #hub_wind_speed = Float(desc='Machine hub wind speed', unit='m/s') # KLD: I don't believe a wind speed of any sort should be in the turbine description #P-E: You are right, let's remove it


class GenericWindTurbinePowerCurveVT(GenericWindTurbineVT):
    c_t_curve = Array(desc='Machine thrust coefficients by wind speed at hub')
    power_curve = Array(desc='Machine power output [W] by wind speed at hub')
# ADDED 17/06 P-E
# MOVED 17/06 KLD: If these are meant to associated witht the power curve, let's put them in this Variable Tree
    cut_in_wind_speed = Float(desc='The cut-in wind speed of the wind turbine', unit='m/s') # P-E: This might be needed to use the power-curves
    cut_out_wind_speed = Float(desc='The cut-out wind speed of the wind turbine', unit='m/s') # P-E: This might be needed to use the power-curves
    rated_wind_speed = Float(desc='The rated wind speed of the wind turbine', unit='m/s') # P-E: do we need this? # KLD: it may be useful to have the specific rated speed beyond the power curve (which may have coarse resolution)
    air_density = Float(desc='The air density the power curve are valid for', unit='kg/(m*m*m)') #P-E: # KLD: should arrays be tables with curves provided for specific air densities? This works - can have an array of Power Curves at multiple air densities


# P-E: Do we need maybe to define more complete one? In many cases these information are not needed / available; # KLD: makes sense - still not sure what to do about dB_curve
class ExtendedWindTurbinePowerCurveVT(GenericWindTurbinePowerCurveVT):
    rpm_curve = Array(desc='Machine rpm [rpm] by wind speed at hub') # KLD: used by OpenWind but may not want to include it here
    pitch_curve = Array(desc='The wind turbine pitch curve', unit='deg') # P-E: It goes hand in hand with RPM curve usually
    #dB_curve = Array(desc='Machine decibal output [dB] by wind speed at hub') # KLD: important but perhaps not for generic analysis #P-E: I have never seen these types of curves, but if you have these as data inputs, why not

class GenericWindRoseVT(VariableTree):
    directions = Array(desc='Direction sectors angles [n_wd]', unit='deg')
    speeds = Array(desc='wind speeds sectors [n_ws]', unit='m/s')
    frequency_array = Array(desc='Frequency by direction sectors and by wind speed sectors [n_wd, n_ws]', unit='')   

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
        dirs = array(self.directions.tolist()+[360])
        freq = self.frequency_array[range(len(self.directions))+[0],:]
        c=ax.contourf(pi/2.0-dirs* pi / 180.,
                    self.speeds, freq.T, 100, cmap=plt.cm.gist_ncar_r)
        fig.colorbar(c)

# KLD: added for both AEP and wind farm assemblies, P-E: OK!
class GenericWindFarmTurbineLayout(VariableTree):
# MODIFIED 17/06 KLD: only one farm layout class necessary if single turbine is a list of 1
    wt_list = List(GenericWindTurbinePowerCurveVT(), iotype='in', desc='The wind turbine list of descriptions') # KLD: shouldnt these include power curves?
    wt_positions = Array([], unit='m', iotype='in', desc='Array of wind turbines attached to particular positions') # KLD: no particular units? (lat, long)? # P-E: I would rather have the unit defined, otherwise we might introduce some bugs 
    wt_wind_roses = List(iotype='in', desc='wind rose for each wind turbine position')

#MODIFIED 19/06 P-E: Extending the class to handle single wind turbine farms as well
    single_wind_turbine = Bool(False, desc='Define if the layout has only one type of turbine or more')
    wind_turbine = VarTree(GenericWindTurbinePowerCurveVT(), iotype='in', desc='wind turbine power curve') 
        
    @property
    def n_wt(self):
        return self.wt_positions.shape[0]

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

# KLD: added for both AEP and wind farm assemblies
# KLD: removed to eliminate redundancy
#class GenericWindFarmMultipleTurbineLayout(VariableTree):
    #wt_list = List(GenericWindTurbinePowerCurveVT(), iotype='in', desc='The wind turbine list of descriptions') # KLD: shouldnt these include power curves?
    #wt_positions = Array([], unit='m', iotype='in', desc='Array of wind turbines attached to particular positions') # KLD: no particular units? (lat, long)? # P-E: I would rather have the unit defined, otherwise we might introduce some bugs 
