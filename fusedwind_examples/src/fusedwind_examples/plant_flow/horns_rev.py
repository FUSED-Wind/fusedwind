## FUSED-Wake imports
from fusedwind.plant_flow.fused_plant_asym import WWHAEP
from fusedwind.plant_flow.wake.noj import NOJWindFarmWake

### Single wind rose type
hrAEP = WWHAEP()
hrAEP.configure()
hrAEP.replace('wf', NOJWindFarmWake())
hrAEP.filename = 'wind_farms/horns_rev/hornsrev1_turbine_nodescription.wwh'
hrAEP.wind_directions = [0., 90., 180., 270.]#linspace(0.0, 360.0, 3)[:-1]
hrAEP.wind_speeds = [8., 12., 24.]#linspace(4.0, 25.0, 3)
hrAEP.execute()
print hrAEP.net_aep

### Multiple wind rose type
hrAEP = WWHAEP()
hrAEP.wind_rose_type = 'multiple'
hrAEP.configure()
hrAEP.replace('wf', NOJWindFarmWake())
hrAEP.filename = 'wind_farms/horns_rev/hornsrev1_turbine_nodescription.wwh'
hrAEP.wind_directions = [0., 90., 180., 270.]#linspace(0.0, 360.0, 3)[:-1]
hrAEP.wind_speeds = [8., 12., 24.]#linspace(4.0, 25.0, 3)
hrAEP.execute()
print hrAEP.net_aep



# from fusedwind.plant_flow.wake.wake import GenericWakeModel, GenericWindFarmWake, \
#     GenericWSPosition, GenericHubWindSpeed, RotX, RotY, RotZ, \
#     wake_length_dist, c2c_dist, NeutralLogLawInflowGenerator, GenericEngineeringWakeModel, \
#     GaussWSPosition, GaussHubWS

# ## DTU-FUSED-Wake imports
# from dtu_fused_wake.ainslie import AinslieWakeModel, AinslieWindFarmWake
# from dtu_fused_wake.gcl import GCLWindFarmWake, GCLWakeModel
# from fused_wake.noj import NOJWindFarmWake, NOJWakeModel, MozaicTileWindFarmWake
# from fused_wake.frandsen import FrandsenWakeModel, FrandsenWindFarmWake
    
# ## Moved to FUSED-Wind plugin
# #from fused_wake.io import GenericWindTurbineVT
# #from fused_wake.windturbine import WindTurbinePowerCurve

# ## FUSED-Wind imports
# from fusedwind.plant_flow.fused_plant_vt import GenericWindTurbineVT
# from fusedwind.plant_flow.fused_plant_comp import WindTurbinePowerCurve, PlantFromWWF

# from openmdao.lib.datatypes.api import VarTree, Float, Array, Int
# from openmdao.main.api import set_as_top

# from numpy import array, zeros, cos, sin, pi, sqrt, dot, ndarray, loadtxt, log, nonzero, argsort, NaN, mean, ones, vstack, linspace, exp, arctan
# from scipy.integrate import odeint
# from scipy.interpolate import interp1d

# import matplotlib.pylab as plt

# ref_power = np.loadtxt(file_power)
# wt_desc = generate_v80()
# hr_inputs = dict(
#     wt_list = [wt_desc]*80,
#     wind_speed = 8.0, #20.0 * rand() + 4.0,
#     wind_direction = 270.0, #360.0*rand(),
#     z_0 = 1.0000e-04,
#     TI = 0.07,
#     z_ref = wt_desc.hub_height,
#     wt_positions = np.loadtxt(file_Positions), 
# )

# #wfm = set_as_top(AinslieWindFarmWake())
# #for wfModel in [NOJWindFarmWake, MozaicTileWindFarmWake, FrandsenWindFarmWake, QuAnslie, AinslieWindFarmWake, GCLWindFarmWake]:
# for wfModel in [NOJWindFarmWake, MozaicTileWindFarmWake, FrandsenWindFarmWake]:
#     wfm = set_as_top(wfModel())
#     if wfm.name == '':
#         wfm.name = wfm.__class__.__name__.split('WindFarmWake')[0]
#     wfm.set_inputs(hr_inputs)
#     #wfm.upstream_wake_driver.sequential = False

#     wfm.run()
#     plt.plot(range(80),wfm.wt_power, label=wfm.name)


# plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
# plt.title('HR case: ws={wind_speed:.1f}m/s, wd={wind_direction:.1f}, TI={TI}'.format(**hr_inputs))
