
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
    fused_wake.wake.GenericWakeSum=fused_wake.wake:GenericWakeSum
    fused_wake.wake.UpstreamWakeDriver=fused_wake.wake:UpstreamWakeDriver
    fused_wake.wake.NeutralLogLawInflowGenerator=fused_wake.wake:NeutralLogLawInflowGenerator
    fused_wake.io.GenericWindTurbine=fused_wake.io:GenericWindTurbine
    fused_wake.wake.WTStreamwiseSorting=fused_wake.wake:WTStreamwiseSorting
    fused_wake.wake.GenericFlowModel=fused_wake.wake:GenericFlowModel
    fused_wake.wake.WTID=fused_wake.wake:WTID
    fused_wake.wake.PostProcessWTCases=fused_wake.wake:PostProcessWTCases
    fused_wake.wake.GenericWindFarmWake=fused_wake.wake:GenericWindFarmWake
    fused_wake.wake.QuadraticWakeSum=fused_wake.wake:QuadraticWakeSum
    fused_wake.wake.GenericWSPosition=fused_wake.wake:GenericWSPosition
    fused_wake.wake.HubCenterWSPosition=fused_wake.wake:HubCenterWSPosition
    fused_wake.wake.PostProcessWindRose=fused_wake.wake:PostProcessWindRose
    fused_wake.wake.HubCenterWS=fused_wake.wake:HubCenterWS
    fused_wake.wake.HomogeneousInflowGenerator=fused_wake.wake:HomogeneousInflowGenerator
    fused_wake.wake.GenericEngineeringWakeModel=fused_wake.wake:GenericEngineeringWakeModel
    fused_wake.wake.GenericWindFarm=fused_wake.wake:GenericWindFarm
    fused_wake.wake.GenericHubWindSpeed=fused_wake.wake:GenericHubWindSpeed
    fused_wake.wake.GenericInflowGenerator=fused_wake.wake:GenericInflowGenerator
    fused_wake.wake.GenericAEP=fused_wake.wake:GenericAEP
    fused_wake.wake.AEP=fused_wake.wake:AEP
    fused_wake.wake.LinearWakeSum=fused_wake.wake:LinearWakeSum
    fused_wake.wake.WakeReader=fused_wake.wake:WakeReader
    fused_wake.wake.GenericWakeModel=fused_wake.wake:GenericWakeModel
    [openmdao.driver]
    fused_wake.wake.WakeDriver=fused_wake.wake:WakeDriver
    fused_wake.wake.UpstreamWakeDriver=fused_wake.wake:UpstreamWakeDriver
    [openmdao.container]
    fused_wake.wake.WakeDriver=fused_wake.wake:WakeDriver
    fused_wake.wake.GenericFlowModel=fused_wake.wake:GenericFlowModel
    fused_wake.wake.UpstreamWakeDriver=fused_wake.wake:UpstreamWakeDriver
    fused_wake.wake.NeutralLogLawInflowGenerator=fused_wake.wake:NeutralLogLawInflowGenerator
    fused_wake.io.GenericWindTurbine=fused_wake.io:GenericWindTurbine
    fused_wake.wake.WTStreamwiseSorting=fused_wake.wake:WTStreamwiseSorting
    fused_wake.wake.GenericWakeSum=fused_wake.wake:GenericWakeSum
    fused_wake.wake.WTID=fused_wake.wake:WTID
    fused_wake.wake.PostProcessWTCases=fused_wake.wake:PostProcessWTCases
    fused_wake.wake.GenericWindFarmWake=fused_wake.wake:GenericWindFarmWake
    fused_wake.wake.QuadraticWakeSum=fused_wake.wake:QuadraticWakeSum
    fused_wake.io.GenericWindTurbineVT=fused_wake.io:GenericWindTurbineVT
    fused_wake.wake.GenericWSPosition=fused_wake.wake:GenericWSPosition
    fused_wake.wake.HubCenterWSPosition=fused_wake.wake:HubCenterWSPosition
    fused_wake.wake.PostProcessWindRose=fused_wake.wake:PostProcessWindRose
    fused_wake.wake.HubCenterWS=fused_wake.wake:HubCenterWS
    fused_wake.io.GenericWindTurbinePowerCurveVT=fused_wake.io:GenericWindTurbinePowerCurveVT
    fused_wake.wake.HomogeneousInflowGenerator=fused_wake.wake:HomogeneousInflowGenerator
    fused_wake.wake.GenericEngineeringWakeModel=fused_wake.wake:GenericEngineeringWakeModel
    fused_wake.wake.GenericWindFarm=fused_wake.wake:GenericWindFarm
    fused_wake.wake.GenericHubWindSpeed=fused_wake.wake:GenericHubWindSpeed
    fused_wake.wake.GenericInflowGenerator=fused_wake.wake:GenericInflowGenerator
    fused_wake.wake.GenericAEP=fused_wake.wake:GenericAEP
    fused_wake.wake.AEP=fused_wake.wake:AEP
    fused_wake.wake.LinearWakeSum=fused_wake.wake:LinearWakeSum
    fused_wake.wake.WakeReader=fused_wake.wake:WakeReader
    fused_wake.wake.GenericWakeModel=fused_wake.wake:GenericWakeModel

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

- **version:** 0.1

