# 1 ---------

# A simple test of the basic_aep model
from fusedwind.plant_flow.basic_aep import aep_weibull_assembly
import numpy as np

aep = aep_weibull_assembly()


# 1 ---------
# 2 ---------

# Set input parameters

aep.wind_curve = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, \
                           11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0, 21.0, 22.0, 23.0, 24.0, 25.0, 26.0])
aep.power_curve = np.array([0.0, 0.0, 0.0, 187.0, 350.0, 658.30, 1087.4, 1658.3, 2391.5, 3307.0, 4415.70, \
                          5000.0, 5000.0, 5000.0, 5000.0, 5000.0, 5000.0, 5000.0, 5000.0, 5000.0, 5000.0, 5000.0, 5000.0, \
                          5000.0, 5000.0, 0.0])
aep.A = 8.35
aep.k = 2.15
aep.array_losses = 0.059
aep.other_losses = 0.0
aep.availability = 0.94
aep.turbine_number = 100

# 2 ---------
# 3 ---------

aep.run()

# 3 ---------
# 4 --------- 

print "Annual energy production for an offshore wind plant with 100 NREL 5 MW reference turbines."
print "AEP gross output (before losses): {0:.1f} kWh".format(aep.gross_aep)
print "AEP net output (after losses): {0:.1f} kWh".format(aep.net_aep)
print

# 4 ----------
