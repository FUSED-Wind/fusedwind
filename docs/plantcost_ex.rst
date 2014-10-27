Plant Cost and Financial Analysis Tutorials
-----------------------------------------------

This tutorial covers how to use FUSED-Wind's financial analysis capabilities with a simple set of cost models for a wind turbine and plant.

First, the necessary modules are imported; in this case we import the example models that draw upon the FUSED-Wind financial analysis framework.

.. literalinclude:: ../docs/examples/Fused_cost_docs_example.py
    :start-after: # --- 1
    :end-before: # --- 1

We will perform a set up of each of the base, extended and full models for analysis of turbine and balance of station costs as well as operational expenditures and overall financial analysis.

Turbine Cost Models
^^^^^^^^^^^^^^^^^^^^

We begin with the turbine cost models and the most basic of them which simple allows you to have a turbine assembly consisting of whatever sub-models necessary and a simple cost aggregator model for the turbine.  We set up the model, run it and print out the turbine cost results.
 

.. literalinclude:: ../docs/examples/Fused_cost_docs_example.py
    :start-after: # --- 2
    :end-before: # --- 2

Next, we used an extended version of the turbine cost model where separate cost modules are explicitly used for the rotor, nacelle and tower.  The simple models in this example have no inputs and just output respective costs.  Therefor it is necessary to explicitly run them to update their cost outputs.  We set up the model, run it for a first configuration, then run the sub-models, run the model again and print out the turbine and sub-assembly cost results to screen.

.. literalinclude:: ../docs/examples/Fused_cost_docs_example.py
    :start-after: # --- 3
    :end-before: # --- 3

Finally, the full version of the turbine cost model includes individual cost models for each major wind turbine component.  The same process is used as for the extended model.

.. literalinclude:: ../docs/examples/Fused_cost_docs_example.py
    :start-after: # --- 4
    :end-before: # --- 4

Balance of Station Cost Models
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The basic balance of station model includes an assembly consisting of whatever sub-models are necessary and a simple cost aggregator.  We set up the model, run it and print out the balance of station cost results.

.. literalinclude:: ../docs/examples/Fused_cost_docs_example.py
    :start-after: # --- 5
    :end-before: # --- 5

The extended balance of station model is similar but requires a more specific breakdown of balance of station costs.

.. literalinclude:: ../docs/examples/Fused_cost_docs_example.py
    :start-after: # --- 6
    :end-before: # --- 6

The full version of the balance of station model requires even higher resolution on balance of station cost estimates.

.. literalinclude:: ../docs/examples/Fused_cost_docs_example.py
    :start-after: # --- 7
    :end-before: # --- 7

Operational Expenditures Models
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The basic operational expenditures model includes an assembly consisting of whatever sub-models are necessary and a simple cost aggregator.  We set up the model, run it and print out the operational expenditures results.

.. literalinclude:: ../docs/examples/Fused_cost_docs_example.py
    :start-after: # --- 8
    :end-before: # --- 8

The extended operational expenditures model is similar but requires a more specific breakdown of operational expenditures.

.. literalinclude:: ../docs/examples/Fused_cost_docs_example.py
    :start-after: # --- 9
    :end-before: # --- 9

Finance Models
^^^^^^^^^^^^^^^

The basic finance model includes an assembly consisting of whatever sub-models are necessary and a simple cost aggregator.  We set up the model, run it and print out the finance results.

.. literalinclude:: ../docs/examples/Fused_cost_docs_example.py
    :start-after: # --- 10
    :end-before: # --- 10

The basic financial analysis model includes sub-assembly for turbine costs, balance of station costs, operational expenditures and energy production.  Models for energy production must be based on the FUSED-Wind energy production model.  The financial model has a global input, turbine number, which must be set.  It can then be run and the results printed out.

.. literalinclude:: ../docs/examples/Fused_cost_docs_example.py
    :start-after: # --- 11
    :end-before: # --- 11


The extended financial analysis model includes sub-assembly for turbine costs, balance of station costs, operational expenditures and energy production with extended models for balance of station and operational expenditures.  Models for energy production must be based on the FUSED-Wind energy production model.  The financial model has a global input, turbine number, which must be set.  It can then be run and the results printed out.

.. literalinclude:: ../docs/examples/Fused_cost_docs_example.py
    :start-after: # --- 12
    :end-before: # --- 12