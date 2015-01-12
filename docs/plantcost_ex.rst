Plant Cost and Financial Analysis Tutorials
-----------------------------------------------

This tutorial covers how to use FUSED-Wind's financial analysis capabilities with a simple set of cost models for a wind turbine and plant.

First, the necessary modules are imported; in this case we import the example models that draw upon the FUSED-Wind financial analysis framework.

.. literalinclude:: ../docs/examples/Fused_cost_docs_example.py
    :start-after: # --- 1
    :end-before: # --- 1

We will perform a set up of each of the base, extended and full models for analysis of turbine and balance of station costs as well as operational expenditures and overall financial analysis.

Turbine Cost Models
++++++++++++++++++++

We begin with the turbine cost models and the most basic of them which simple allows you to have a turbine assembly consisting of whatever sub-models necessary and a simple cost aggregator model for the turbine.  We set up the model, run it and print out the turbine cost results.
 

.. literalinclude:: ../docs/examples/Fused_cost_docs_example.py
    :start-after: # --- 2
    :end-before: # --- 2

The results should be:

>>> Turbine capital cost is: $9000000 USD

Next, we used an extended version of the turbine cost model where separate cost modules are explicitly used for the rotor, nacelle and tower.  The simple models in this example have no inputs and just output respective costs.  Therefor it is necessary to explicitly run them to update their cost outputs.  We set up the model, run it for a first configuration, then run the sub-models, run the model again and print out the turbine and sub-assembly cost results to screen.

.. literalinclude:: ../docs/examples/Fused_cost_docs_example.py
    :start-after: # --- 3
    :end-before: # --- 3

The results should be:

>>> Turbine capital cost is: $9000000 USD
>>> Rotor capital cost is: $3000000 USD
>>> Nacelle capital cost is: $3000000 USD
>>> Tower capital cost is: $3000000 USD

Finally, the full version of the turbine cost model includes individual cost models for each major wind turbine component.  The same process is used as for the extended model.

.. literalinclude:: ../docs/examples/Fused_cost_docs_example.py
    :start-after: # --- 4
    :end-before: # --- 4

The results should be:

>>> Turbine capital cost is: $9000000 USD

>>> Rotor capital cost is: $1000000 USD
>>> Blade capital cost is: $350000 USD
>>> Hub capital cost is: $300000 USD
>>> Pitch System capital cost is: $300000 USD
>>> Spinner capital cost is: $400000 USD

>>> Nacelle capital cost is: $4000000 USD
>>> Low speed shaft capital cost is: $500000 USD
>>> Bearings shaft capital cost is: $500000 USD
>>> Gearbox shaft capital cost is: $1000000 USD
>>> Generator capital cost is: $500000 USD
>>> High speed shaft capital cost is: $500000 USD
>>> Bedplate shaft capital cost is: $500000 USD
>>> Yaw System shaft capital cost is: $500000 USD

>>> Tower capital cost is: $4000000 USD

Balance of Station Cost Models
+++++++++++++++++++++++++++++++

The basic balance of station model includes an assembly consisting of whatever sub-models are necessary and a simple cost aggregator.  We set up the model, run it and print out the balance of station cost results.

.. literalinclude:: ../docs/examples/Fused_cost_docs_example.py
    :start-after: # --- 5
    :end-before: # --- 5

The results should be:

>>> Balance of station cost is: $1800000000 USD

The extended balance of station model is similar but requires a more specific breakdown of balance of station costs.

.. literalinclude:: ../docs/examples/Fused_cost_docs_example.py
    :start-after: # --- 6
    :end-before: # --- 6

The results should be:

>>> Balance of station cost is: $1800000000 USD
>>> Balance of station development cost is: $90000000 USD
>>> Balance of station preparation and staging cost is: $180000000 USD
>>> Balance of station transportation cost is: $360000000 USD
>>> Balance of station foundation and substructure cost is: $360000000 USD
>>> Balance of station electrical cost is: $270000000 USD
>>> Balance of station assemlby and installation cost is: $270000000 USD
>>> Balance of station soft cost is: $180000000 USD
>>> Balance of station other cost is: $90000000 USD

The full version of the balance of station model requires even higher resolution on balance of station cost estimates.

.. literalinclude:: ../docs/examples/Fused_cost_docs_example.py
    :start-after: # --- 7
    :end-before: # --- 7

The results should be:

>>> Balance of station cost is: $1800000000 USD
>>> Balance of station cost is: $45000000 USD
>>> Balance of station cost is: $45000000 USD
>>> Balance of station cost is: $180000000 USD
>>> Balance of station cost is: $180000000 USD
>>> Balance of station cost is: $270000000 USD
>>> Balance of station cost is: $270000000 USD
>>> Balance of station cost is: $180000000 USD
>>> Balance of station cost is: $270000000 USD
>>> Balance of station cost is: $90000000 USD
>>> Balance of station cost is: $90000000 USD
>>> Balance of station cost is: $90000000 USD
>>> Balance of station cost is: $45000000 USD
>>> Balance of station cost is: $45000000 USD

Operational Expenditures Models
++++++++++++++++++++++++++++++++

The basic operational expenditures model includes an assembly consisting of whatever sub-models are necessary and a simple cost aggregator.  We set up the model, run it and print out the operational expenditures results.

.. literalinclude:: ../docs/examples/Fused_cost_docs_example.py
    :start-after: # --- 8
    :end-before: # --- 8

The results should be:

>>> Operational expenditures is: $50000000 USD

The extended operational expenditures model is similar but requires a more specific breakdown of operational expenditures.

.. literalinclude:: ../docs/examples/Fused_cost_docs_example.py
    :start-after: # --- 9
    :end-before: # --- 9

The results should be:

>>> Operational expenditures is: $50000000 USD
>>> Preventative operational expenditures is: $12500000 USD
>>> Corrective operational expenditures is: $25000000 USD
>>> Lease operational expenditures is: $12500000 USD
>>> Other operational expenditures is: $0 USD

Finance Models
+++++++++++++++

The basic finance model includes an assembly consisting of whatever sub-models are necessary and a simple cost aggregator.  We set up the model, run it and print out the finance results.

.. literalinclude:: ../docs/examples/Fused_cost_docs_example.py
    :start-after: # --- 10
    :end-before: # --- 10

The results should be:

>>> Financial analysis COE result is: $0.1655/kWh

The basic financial analysis model includes sub-assembly for turbine costs, balance of station costs, operational expenditures and energy production.  Models for energy production must be based on the FUSED-Wind energy production model.  The financial model has a global input, turbine number, which must be set.  It can then be run and the results printed out.

.. literalinclude:: ../docs/examples/Fused_cost_docs_example.py
    :start-after: # --- 11
    :end-before: # --- 11

The results should be:

>>> Financial analysis COE result is: $0.1655/kWh

The extended financial analysis model includes sub-assembly for turbine costs, balance of station costs, operational expenditures and energy production with extended models for balance of station and operational expenditures.  Models for energy production must be based on the FUSED-Wind energy production model.  The financial model has a global input, turbine number, which must be set.  It can then be run and the results printed out.

.. literalinclude:: ../docs/examples/Fused_cost_docs_example.py
    :start-after: # --- 12
    :end-before: # --- 12

The results should be:

>>> Financial analysis COE result is: $0.1655/kWh
