Energy Production Tutorials
----------------------------

This tutorial covers how to use FUSED-Wind's energy analysis framework for basic energy production analysis.

Tutorial for Basic_AEP
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

As an example of Basic_AEP, let us simulate energy production for a land-based wind plant.  

The first step is to import the relevant files and set up the component.

.. literalinclude:: examples/Fused_flow_docs_example.py
    :start-after: # 1 ---
    :end-before: # 1 ---

The plant energy production model relies on some turbine as well as plant input parameters that must be specified.  Firstly the wind turbine power curve must be set along with the site hub height Weibull scale and shape factors.  There is no flow model so array losses and other turbine and plant losses must be directly set.  Finally the number of turbines is included as the AEP per turbine is calculated by the number of turbines in the plant to get the total energy production.

.. literalinclude:: examples/Fused_flow_docs_example.py
    :start-after: # 2 ---
    :end-before: # 2 ---

We can now evaluate the plant energy production.

.. literalinclude:: examples/Fused_flow_docs_example.py
    :start-after: # 3 ---
    :end-before: # 3 ---

We then print out the resulting energy production values.

.. literalinclude:: examples/Fused_flow_docs_example.py
    :start-after: # 4 ---
    :end-before: # 4 ---

The result is:

>>> Annual energy production for an offshore wind plant with 100 NREL 5 MW reference
 turbines.
>>> AEP gross output (before losses): 1570713782.2 kWh
>>> AEP net output (after losses): 1389359168.9 kWh