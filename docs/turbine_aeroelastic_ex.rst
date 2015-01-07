

Aero-elastic Turbine Example
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This example shows the basics of how to connect a parameterized geometric definition of a wind turbine blade planform to the inputs of an aeroelastic solver.
The example is located in ``src/fusedwind/examples/turbine/aeroelastic_turbine.py``.

The overall turbine geometry and beam properties are defined in the ``fusedwind.turbine.turbine_vt.AeroelasticHAWTVT`` variable tree.
This variable tree needs to be an input to an aeroelastic solver wrapper, and is currently the only requirement.
For optimization contexts you will need some parameterization of the blade geometry and if you choose to use the one supplied in FUSED-Wind, hooking up the solver with this geometric definition is easy.

The first step is to write a wrapper for an aeroelastic code.
In the example we have made a dummy component that implements the AeroElasticSolverBase interface and otherwise does nothing.

.. literalinclude:: ../src/fusedwind/examples/turbine/aeroelastic_turbine.py
    :start-after: # --- 1
    :end-before: # --- 2

Then we instantiate the assembly we want to run our analysis in and add an instance of the ``fusedwind.turbine.geometry.SplinedBladePlanform`` class which adds an FFD spline to each of the planform curves.
Secondly, we add our new aeroelastic solver.

.. literalinclude:: ../src/fusedwind/examples/turbine/aeroelastic_turbine.py
    :start-after: # --- 2
    :end-before: # --- 3

In the next step we then configure this turbine.
The ``fusedwind.turbine.turbine_vt.configure_turbine`` method configures the ``AeroelasticHAWTVT`` variable tree as a standard three bladed turbine with a tower, tower top, shaft, hub and blades.
Each of these are a ``MainBody`` variable tree, which defines the body's geometric and structural properties.
The overall dimensions of the turbine are then specified, which in this case corresponds to the DTU 10MW RWT.

.. literalinclude:: ../src/fusedwind/examples/turbine/aeroelastic_turbine.py
    :start-after: # --- 3
    :end-before: # --- 4

The final configuration step is to link the splined geometry to the blade geometry of the turbine definition in the aeroelastic solver.

.. literalinclude:: ../src/fusedwind/examples/turbine/aeroelastic_turbine.py
    :start-after: # --- 4
    :end-before: # --- 5

And all that remains is to run the assembly which in this case is not so eventful.
