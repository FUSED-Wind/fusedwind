
# 1 ---
from fusedwind.plant_flow.comp import GenericWindFarm
from numpy.random import random
class MyTestWindFarm(GenericWindFarm):
    """ A random generic wind farm, producing random power for testing purpose """
    def execute(self):
        self.wt_power = [random() * wt_desc.power_rating for wt_desc in self.wt_layout.wt_list]
        self.wt_thrust = [pow_ / (random() * self.wind_speed) for pow_ in self.wt_power]
        self.power = sum(self.wt_power)
        self.thrust = sum(self.wt_thrust)
# 1 ---

# 2 ---
from fusedwind.plant_flow.asym import AEPMultipleWindRoses
from fusedwind.plant_flow.generate_fake_vt import generate_random_wt_layout
import numpy as np

def my_aep_calculation(wind_farm_model):
    aep = AEPMultipleWindRoses()
    aep.add('wf', wind_farm_model())
    aep.configure()
    aep.connect('wt_layout', 'wf.wt_layout')
    # The wind speed/directions bins to consider in the AEP calculation
    aep.wind_speeds = np.linspace(4., 25., 10).tolist()
    aep.wind_directions = np.linspace(0., 360., 36)[:-1].tolist()
    # Number of wind turbines
    nwt = 5
    aep.wt_layout = generate_random_wt_layout(nwt=nwt)
    aep.run()
    return aep
# 2 ---

# Running the aep calculation
# 3 ---
aep = my_aep_calculation(MyTestWindFarm)
print 'Net AEP: ', aep.net_aep
print 'WT AEP:', aep.wt_aep
# 3 ---

# Plotting some wind turbine power curves

# 4 ---
import pylab as plt
f, (ax1, ax2) = plt.subplots(1, 2)
colors = ['tomato', 'violet', 'blue', 'green', 'yellow']
ax2.scatter(aep.wf.wt_layout.wt_positions[:,0],
            aep.wf.wt_layout.wt_positions[:,1], c=colors,
            s=aep.wf.wt_layout._wt_list('rotor_diameter'))
for wt, c in zip(aep.wf.wt_layout.wt_list, colors):
    ax1.plot(wt.power_curve[:,0],wt.power_curve[:,1]/1000.0, color=c,
             label='{name}: P={P:.1f}kW, D={D:.1f}m'.format(
                 name=wt.name, P=wt.power_rating/1000., D=wt.rotor_diameter))
    ax2.text(wt.position[0], wt.position[1], wt.name)
ax1.legend()
ax1.set_xlabel('Wind Speed [m/s]')
ax1.set_ylabel('Power [kW]')
ax2.axis('equal')

plt.show()
# 4 ---