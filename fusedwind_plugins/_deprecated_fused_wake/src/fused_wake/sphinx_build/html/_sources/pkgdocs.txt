
================
Package Metadata
================

- **author:** Pierre-Elouan Rethore, DTU Wind Energy

- **author-email:** pire@dtu.dk

- **classifier**:: 

    Intended Audience :: Science/Research
    Topic :: Scientific/Engineering

- **description-file:** README.txt

- **download-url:** https://github.com/FUSED-Wind/FUSED-Wind/tree/develop/fusedwind_plugins/fused_wake

- **entry_points**:: 

    [openmdao.component]
    fused_wake.wake.WakeDriver=fused_wake.wake:WakeDriver
    fusedwind.plant_flow.fused_plant_comp.GenericWakeModel=fusedwind.plant_flow.fused_plant_comp:GenericWakeModel
    fused_wake.wake.UpstreamWakeDriver=fused_wake.wake:UpstreamWakeDriver
    fusedwind.plant_flow.fused_plant_comp.HubCenterWSPosition=fusedwind.plant_flow.fused_plant_comp:HubCenterWSPosition
    fused_wake.wake.NeutralLogLawInflowGenerator=fused_wake.wake:NeutralLogLawInflowGenerator
    fused_wake.wake.WakeReader=fused_wake.wake:WakeReader
    fused_wake.wake.WTStreamwiseSorting=fused_wake.wake:WTStreamwiseSorting
    fusedwind.plant_flow.fused_plant_comp.GenericWSPosition=fusedwind.plant_flow.fused_plant_comp:GenericWSPosition
    fused_wake.wake.WTID=fused_wake.wake:WTID
    fused_wake.wake.PostProcessWTCases=fused_wake.wake:PostProcessWTCases
    fused_wake.wake.GenericWindFarmWake=fused_wake.wake:GenericWindFarmWake
    fusedwind.plant_flow.fused_plant_comp.GenericFlowModel=fusedwind.plant_flow.fused_plant_comp:GenericFlowModel
    fused_wake.wake.QuadraticWakeSum=fused_wake.wake:QuadraticWakeSum
    fusedwind.plant_flow.fused_plant_comp.GenericWindTurbine=fusedwind.plant_flow.fused_plant_comp:GenericWindTurbine
    fusedwind.plant_flow.fused_plant_comp.GenericHubWindSpeed=fusedwind.plant_flow.fused_plant_comp:GenericHubWindSpeed
    fusedwind.plant_flow.fused_plant_comp.WindTurbinePowerCurve=fusedwind.plant_flow.fused_plant_comp:WindTurbinePowerCurve
    fused_wake.wake.PostProcessWindRose=fused_wake.wake:PostProcessWindRose
    fused_wake.wake.HubCenterWS=fused_wake.wake:HubCenterWS
    fused_wake.wake.HomogeneousInflowGenerator=fused_wake.wake:HomogeneousInflowGenerator
    fused_wake.wake.GenericEngineeringWakeModel=fused_wake.wake:GenericEngineeringWakeModel
    fusedwind.plant_flow.fused_plant_comp.GenericInflowGenerator=fusedwind.plant_flow.fused_plant_comp:GenericInflowGenerator
    fused_wake.wake.GenericWindFarm=fused_wake.wake:GenericWindFarm
    fused_wake.wake.GenericInflowGenerator=fused_wake.wake:GenericInflowGenerator
    fused_wake.wake.GenericAEP=fused_wake.wake:GenericAEP
    fusedwind.plant_flow.fused_plant_comp.GenericWakeSum=fusedwind.plant_flow.fused_plant_comp:GenericWakeSum
    fused_wake.wake.AEP=fused_wake.wake:AEP
    fused_wake.wake.LinearWakeSum=fused_wake.wake:LinearWakeSum
    fusedwind.plant_flow.fused_plant_comp.PostProcessWindRose=fusedwind.plant_flow.fused_plant_comp:PostProcessWindRose
    [openmdao.driver]
    fused_wake.wake.WakeDriver=fused_wake.wake:WakeDriver
    fused_wake.wake.UpstreamWakeDriver=fused_wake.wake:UpstreamWakeDriver
    [openmdao.container]
    fused_wake.wake.WakeDriver=fused_wake.wake:WakeDriver
    fusedwind.plant_flow.fused_plant_comp.GenericWakeModel=fusedwind.plant_flow.fused_plant_comp:GenericWakeModel
    fused_wake.wake.UpstreamWakeDriver=fused_wake.wake:UpstreamWakeDriver
    fusedwind.plant_flow.fused_plant_comp.HubCenterWSPosition=fusedwind.plant_flow.fused_plant_comp:HubCenterWSPosition
    fused_wake.wake.NeutralLogLawInflowGenerator=fused_wake.wake:NeutralLogLawInflowGenerator
    fused_wake.wake.WakeReader=fused_wake.wake:WakeReader
    fused_wake.wake.WTStreamwiseSorting=fused_wake.wake:WTStreamwiseSorting
    fused_wake.wake.WTID=fused_wake.wake:WTID
    fused_wake.wake.PostProcessWTCases=fused_wake.wake:PostProcessWTCases
    fused_wake.wake.GenericWindFarmWake=fused_wake.wake:GenericWindFarmWake
    fusedwind.plant_flow.fused_plant_comp.GenericFlowModel=fusedwind.plant_flow.fused_plant_comp:GenericFlowModel
    fusedwind.plant_flow.fused_plant_comp.GenericWSPosition=fusedwind.plant_flow.fused_plant_comp:GenericWSPosition
    fused_wake.wake.QuadraticWakeSum=fused_wake.wake:QuadraticWakeSum
    fusedwind.plant_flow.fused_plant_comp.GenericWindTurbine=fusedwind.plant_flow.fused_plant_comp:GenericWindTurbine
    fusedwind.plant_flow.fused_plant_comp.GenericHubWindSpeed=fusedwind.plant_flow.fused_plant_comp:GenericHubWindSpeed
    fusedwind.plant_flow.fused_plant_comp.WindTurbinePowerCurve=fusedwind.plant_flow.fused_plant_comp:WindTurbinePowerCurve
    fused_wake.wake.PostProcessWindRose=fused_wake.wake:PostProcessWindRose
    fused_wake.wake.HubCenterWS=fused_wake.wake:HubCenterWS
    fused_wake.wake.HomogeneousInflowGenerator=fused_wake.wake:HomogeneousInflowGenerator
    fused_wake.wake.GenericEngineeringWakeModel=fused_wake.wake:GenericEngineeringWakeModel
    fusedwind.plant_flow.fused_plant_comp.GenericInflowGenerator=fusedwind.plant_flow.fused_plant_comp:GenericInflowGenerator
    fused_wake.wake.GenericWindFarm=fused_wake.wake:GenericWindFarm
    fused_wake.wake.GenericInflowGenerator=fused_wake.wake:GenericInflowGenerator
    fused_wake.wake.GenericAEP=fused_wake.wake:GenericAEP
    fusedwind.plant_flow.fused_plant_comp.GenericWakeSum=fusedwind.plant_flow.fused_plant_comp:GenericWakeSum
    fused_wake.wake.AEP=fused_wake.wake:AEP
    fused_wake.wake.LinearWakeSum=fused_wake.wake:LinearWakeSum
    fusedwind.plant_flow.fused_plant_comp.PostProcessWindRose=fusedwind.plant_flow.fused_plant_comp:PostProcessWindRose

- **home-page:** https://github.com/FUSED-Wind/FUSED-Wind/tree/develop/fusedwind_plugins/fused_wake

- **keywords:** openmdao

- **license:** Research collaboration

- **maintainer:** Pierre-Elouan Rethore, DTU Wind Energy

- **maintainer-email:** pire@dtu.dk

- **name:** fused_wake

- **requires-dist:** openmdao.main

- **requires-python**:: 

    >=2.6
    <3.0

- **static_path:** [ '_static' ]

- **version:** 0.1.1

