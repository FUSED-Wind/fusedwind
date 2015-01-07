

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


Coupled Structural Aero-elastic Turbine Example
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In this example, we extend the above example to also interface to to a structural model capable of computing the mass and stiffness beam properties of the blade, that is a required input to most aeroelastic solvers, e.g. FAST and HAWC2.
The aim with this is to have the capability of *simultaneously* optimize the structural and aerodynamic design of a blade.

The example combines the example explaining the blade structural parameterization with the above example of interfacing an aeroelastic solver.
The example is located in ``src/fusedwind/examples/turbine/aerostructural_turbine.py``.

The first step is to define our solvers, which is now both an aeroelastic solver and a cross-sectional structure solver capable of computing the beam properties of a blade.

.. literalinclude:: ../src/fusedwind/examples/turbine/aerostructural_turbine.py
    :start-after: # --- 1
    :end-before: # --- 2

Next, we define our blade geometry, both in terms of planform and lofted shape.

.. literalinclude:: ../src/fusedwind/examples/turbine/aerostructural_turbine.py
    :start-after: # --- 2
    :end-before: # --- 3

Then we add our two solvers:

.. literalinclude:: ../src/fusedwind/examples/turbine/aerostructural_turbine.py
    :start-after: # --- 3
    :end-before: # --- 4

And configure the turbine:

.. literalinclude:: ../src/fusedwind/examples/turbine/aerostructural_turbine.py
    :start-after: # --- 4
    :end-before: # --- 5

And finally make the necessary connections between, firstly, the structural geometry and the cross-sectional
solver, secondly, the planform splines and the aeroelastic solver, and finally the beam structural properties
computed by the structural solver with the blade beam properties used by the aeroelastic solver.

.. literalinclude:: ../src/fusedwind/examples/turbine/aerostructural_turbine.py
    :start-after: # --- 5
    :end-before: # --- 6

And lastly, we run the aero-structural analysis.

.. literalinclude:: ../src/fusedwind/examples/turbine/aerostructural_turbine.py
    :start-after: # --- 6
    :end-before: # --- 7