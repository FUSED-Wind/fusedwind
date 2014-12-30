
Plant Cost
----------


Turbine Capital Costs
++++++++++++++++++++++

The turbine capital costs portion of FUSED-Wind specifies interfaces for wind turbine component cost models as well as configure methods to put together a full turbine cost model for a single wind turbine.

.. automodule:: fusedwind.plant_cost.fused_tcc
  :members:

Balance of Station Costs
+++++++++++++++++++++++++

The balance of station costs portion of FUSED-Wind specifies interfaces for wind plant capital expenditures.  There are multiple interfaces for models of varying levels of complexity.

.. automodule:: fusedwind.plant_cost.fused_bos_costs
  :members:

Operational Expenditures
+++++++++++++++++++++++++

The operational expenditures portion of FUSED-Wind specifies interfaces for wind plant operational expenditures.  There are multiple interfaces for models of varying levels of complexity.

.. automodule:: fusedwind.plant_cost.fused_opex
  :members:

Finance
++++++++

The finance portion of FUSED-Wind specifies interfaces for wind plant financial models.  There are multiple interfaces for models of varying levels of complexity as well as configure methods to put together a finance model that depends on multiple sub-models such as turbine capital costs, balance of station costs, operational expenditures and energy capture.

.. automodule:: fusedwind.plant_cost.fused_finance
  :members:
