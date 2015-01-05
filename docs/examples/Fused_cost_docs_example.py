# Example of FUSED framework for cost analysis
# KLD 11/14/2013

# --- 1 -----
from fusedwind.examples.fused_cost_example import BaseTurbineCostModel_Example, ExtendedTurbineCostModel_Example, FullTurbineCostModel_Example, \
                                 BaseBOSCostModel_Example, ExtendedBOSCostModel_Example, FullBOSCostModel_Example, \
                                 BaseOPEXModel_Example, ExtendedOPEXModel_Example, \
                                 BaseFinancialModel_Example, BaseFinancialAnalysis_Example, ExtendedFinancialAnalysis_Example
# --- 1 -----
# --- 2 -----

# Base Turbine Capital Cost Model uses a simple aggregator
baseTCC = BaseTurbineCostModel_Example()

baseTCC.run()

print "Turbine capital cost is: ${0:.0f} USD".format(baseTCC.turbine_cost)

# --- 2 -----
# --- 3 -----

# Extended Turbine Capital Cost Model uses a simple aggregator along with separate models for rotor, nacelle and tower costs and all sub-components
extendedTCC = ExtendedTurbineCostModel_Example()

extendedTCC.run()
extendedTCC.rotorCC.bcc.run(True)
extendedTCC.nacelleCC.bcc.run(True)
extendedTCC.towerCC.bcc.run(True)

extendedTCC.run()

print
print "Turbine capital cost is: ${0:.0f} USD".format(extendedTCC.turbine_cost)
print "Rotor capital cost is: ${0:.0f} USD".format(extendedTCC.rotorCC.cost)
print "Nacelle capital cost is: ${0:.0f} USD".format(extendedTCC.nacelleCC.cost)
print "Tower capital cost is: ${0:.0f} USD".format(extendedTCC.towerCC.cost)

# --- 3 -----
# --- 4 -----

# Full Turbine Capital Cost Model uses a simple aggregator along with separate models for rotor, nacelle and tower costs and all sub-components
fullTCC = FullTurbineCostModel_Example()

fullTCC.run()
fullTCC.rotorCC.bladeCC.run(True)
fullTCC.rotorCC.hubCC.run(True)
fullTCC.rotorCC.pitchSysCC.run(True)
fullTCC.rotorCC.spinnerCC.run(True)
fullTCC.nacelleCC.lssCC.run(True)
fullTCC.nacelleCC.bearingsCC.run(True)
fullTCC.nacelleCC.gearboxCC.run(True)
fullTCC.nacelleCC.hssCC.run(True)
fullTCC.nacelleCC.generatorCC.run(True)
fullTCC.nacelleCC.bedplateCC.run(True)
fullTCC.nacelleCC.yawSysCC.run(True)
fullTCC.towerCC.towerCC.run(True)

fullTCC.run()

print
print "Turbine capital cost is: ${0:.0f} USD".format(fullTCC.turbine_cost)
print
print "Rotor capital cost is: ${0:.0f} USD".format(fullTCC.rotorCC.cost)
print "Blade capital cost is: ${0:.0f} USD".format(fullTCC.rotorCC.bladeCC.cost)
print "Hub capital cost is: ${0:.0f} USD".format(fullTCC.rotorCC.hubCC.cost)
print "Pitch System capital cost is: ${0:.0f} USD".format(fullTCC.rotorCC.pitchSysCC.cost)
print "Spinner capital cost is: ${0:.0f} USD".format(fullTCC.rotorCC.spinnerCC.cost)
print
print "Nacelle capital cost is: ${0:.0f} USD".format(fullTCC.nacelleCC.cost)
print "Low speed shaft capital cost is: ${0:.0f} USD".format(fullTCC.nacelleCC.lssCC.cost)     
print "Bearings shaft capital cost is: ${0:.0f} USD".format(fullTCC.nacelleCC.bearingsCC.cost)
print "Gearbox shaft capital cost is: ${0:.0f} USD".format(fullTCC.nacelleCC.gearboxCC.cost)
print "Generator capital cost is: ${0:.0f} USD".format(fullTCC.nacelleCC.generatorCC.cost)     
print "High speed shaft capital cost is: ${0:.0f} USD".format(fullTCC.nacelleCC.hssCC.cost)
print "Bedplate shaft capital cost is: ${0:.0f} USD".format(fullTCC.nacelleCC.bedplateCC.cost)
print "Yaw System shaft capital cost is: ${0:.0f} USD".format(fullTCC.nacelleCC.yawSysCC.cost)
print
print "Tower capital cost is: ${0:.0f} USD".format(fullTCC.towerCC.cost)

# --- 4 -----
# --- 5 -----

# Base Balance of Station Cost Model uses a simple aggregator
baseBOS = BaseBOSCostModel_Example()

baseBOS.run()

print
print "Balance of station cost is: ${0:.0f} USD".format(baseBOS.bos_costs)

# --- 5 -----
# --- 6 -----

# Extended Balance of Station Cost Model uses a simple aggregator
extendedBOS = ExtendedBOSCostModel_Example()

extendedBOS.run()

print
print "Balance of station cost is: ${0:.0f} USD".format(extendedBOS.bos_costs)
print "Balance of station development cost is: ${0:.0f} USD".format(extendedBOS.bos_breakdown.development_costs)
print "Balance of station preparation and staging cost is: ${0:.0f} USD".format(extendedBOS.bos_breakdown.preparation_and_staging_costs)
print "Balance of station transportation cost is: ${0:.0f} USD".format(extendedBOS.bos_breakdown.transportation_costs)
print "Balance of station foundation and substructure cost is: ${0:.0f} USD".format(extendedBOS.bos_breakdown.foundation_and_substructure_costs)
print "Balance of station electrical cost is: ${0:.0f} USD".format(extendedBOS.bos_breakdown.electrical_costs)
print "Balance of station assemlby and installation cost is: ${0:.0f} USD".format(extendedBOS.bos_breakdown.assembly_and_installation_costs)
print "Balance of station soft cost is: ${0:.0f} USD".format(extendedBOS.bos_breakdown.soft_costs)
print "Balance of station other cost is: ${0:.0f} USD".format(extendedBOS.bos_breakdown.other_costs)

# --- 6 -----
# --- 7 -----

# Full Balance of Station Cost Model uses a simple aggregator
fullBOS = FullBOSCostModel_Example()

fullBOS.run()

print
print "Balance of station cost is: ${0:.0f} USD".format(fullBOS.bos_costs)
print "Balance of station cost is: ${0:.0f} USD".format(fullBOS.bos_breakdown.management_costs)
print "Balance of station cost is: ${0:.0f} USD".format(fullBOS.bos_breakdown.development_costs)
print "Balance of station cost is: ${0:.0f} USD".format(fullBOS.bos_breakdown.preparation_and_staging_costs)
print "Balance of station cost is: ${0:.0f} USD".format(fullBOS.bos_breakdown.transportation_costs)
print "Balance of station cost is: ${0:.0f} USD".format(fullBOS.bos_breakdown.foundation_and_substructure_costs)
print "Balance of station cost is: ${0:.0f} USD".format(fullBOS.bos_breakdown.collection_and_substation_costs)
print "Balance of station cost is: ${0:.0f} USD".format(fullBOS.bos_breakdown.transmission_and_interconnection_costs)
print "Balance of station cost is: ${0:.0f} USD".format(fullBOS.bos_breakdown.assembly_and_installation_costs)
print "Balance of station cost is: ${0:.0f} USD".format(fullBOS.bos_breakdown.contingencies_and_insurance_costs)
print "Balance of station cost is: ${0:.0f} USD".format(fullBOS.bos_breakdown.decommissioning_costs)
print "Balance of station cost is: ${0:.0f} USD".format(fullBOS.bos_breakdown.construction_financing_costs)
print "Balance of station cost is: ${0:.0f} USD".format(fullBOS.bos_breakdown.other_costs)
print "Balance of station cost is: ${0:.0f} USD".format(fullBOS.bos_breakdown.developer_profits)

# --- 7 -----
# --- 8 -----

# Base Operational Expenditures Model uses a simple aggregator
baseOPEX = BaseOPEXModel_Example()

baseOPEX.run()

print
print "Operational expenditures is: ${0:.0f} USD".format(baseOPEX.avg_annual_opex)

# --- 8 -----
# --- 9 -----

# Extended Operational Expenditures Model uses a simple aggregator
extendedOPEX = ExtendedOPEXModel_Example()

extendedOPEX.run()

print
print "Operational expenditures is: ${0:.0f} USD".format(extendedOPEX.avg_annual_opex)
print "Preventative operational expenditures is: ${0:.0f} USD".format(extendedOPEX.opex_breakdown.preventative_opex)
print "Corrective operational expenditures is: ${0:.0f} USD".format(extendedOPEX.opex_breakdown.corrective_opex)
print "Lease operational expenditures is: ${0:.0f} USD".format(extendedOPEX.opex_breakdown.lease_opex)
print "Other operational expenditures is: ${0:.0f} USD".format(extendedOPEX.opex_breakdown.other_opex)

# --- 9 -----
# --- 10 -----

# Base Financial Model uses a simple aggregator
baseCOE = BaseFinancialModel_Example()

baseCOE.turbine_cost = 9000000.0 #Float(iotype='in', desc = 'A Wind Turbine Capital _cost')
baseCOE.turbine_number = 100 #Int(iotype = 'in', desc = 'number of turbines at plant')
baseCOE.bos_costs = 1800000000.0 #Float(iotype='in', desc='A Wind Plant Balance of Station _cost Model')
baseCOE.avg_annual_opex = 50000000.0 #Float(iotype='in', desc='A Wind Plant Operations Expenditures Model')
baseCOE.net_aep = 1752000000.0 #Float(iotype='in', desc='A Wind Plant Annual Energy Production Model', units='kW*h')
baseCOE.run()

print
print "Financial analysis COE result is: ${0:.4f}/kWh".format(baseCOE.coe)

# --- 10 -----
# --- 11 -----

# Base Financial Analysis model integrates base models of underlying cost sub-assemblies
baseFinance = BaseFinancialAnalysis_Example()
baseFinance.turbine_number = 100

baseFinance.run()

print    
print "Financial analysis COE result is: ${0:.4f}/kWh".format(baseFinance.coe)

# --- 11 -----
# --- 12 -----

# Extended financial model integrates base models for turbine, aep and finance with the extended bos and opex models
extendedFinance = ExtendedFinancialAnalysis_Example()
extendedFinance.turbine_number = 100

extendedFinance.run()

print    
print "Financial analysis COE result is: ${0:.4f}/kWh".format(extendedFinance.coe)

# --- 12 -----