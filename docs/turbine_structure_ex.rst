
.. _sec_blade_geometry_ex_label:

Airfoil and Blade Geometry Examples
+++++++++++++++++++++++++++++++++++

A class for airfoil geometries is provided in the ``fusedwind.turbine.geometry_vt.AirfoilShape`` class.
The convention used for airfoil shapes is that the coordinates are defined as a continuous curve starting from the trailing edge pressure side, around the leading edge to the suction side trailing edge.
The airfoil geometry can be oriented in any direction in the *x*-*y*-plane.
The method ``computeLETE`` determines the trailing and leading edges.
The trailing edge is defined as the mean of the first and last points on the airfoil and the leading edge is defined as the point along the curve with maximum distance to the trailing edge.
The ``redistribute`` method can be used to redistribute the points on the airfoil with an arbitrary number of points.
See the source docs for specific parameters for this method.

In the simple example below, which is located in ``src/fusedwind/examples/turbine/fused_turbine_geom_example.py``, we load in the FFA-W3-301 airfoil and distribute 200 points along its surface, letting the AirfoilShape class determine an appropriate leading edge cell size.
Since the trailing edge is not closed, we do not need high clustering there, so we don't have to specify any cell size.
The easiest way to run the example and inspect the class is to run it inside iPython.

.. literalinclude:: ../src/fusedwind/examples/turbine/turbine_geom_example.py
    :start-after: # --- 1
    :end-before: # --- 2

The blade planform used in FUSED-Wind is described by spanwise distributions of *chord*, *twist*, *relative thickness*, and *pitch axis aft leading edge*, variables that are grouped in the ``fusedwind.turbine.geometry_vt.BladePlanformVT`` variable tree.
A lofted shape is generated from this planform in combination with a series of airfoils covering the range of relative thicknesses used on the blade.
The class ``fusedwind.turbine.geometry.LoftedBladeSurface`` can be used to generate to generate a smooth lofted shape, which uses method to interpolate in the airfoil family specified by the user is available available as a stand-alone class in ``fusedwind.turbine.airfoil_vt.BlendAirfoilShapes``.
The lofted blade surface is saved in the ``BladeSurfaceVT`` variable tree by the LoftedBladeSurface class.
The configuration method ``configure_bladesurface`` configures an assembly with a splined blade planform and a lofted blade surface.
In the example below we show how to use this method and plot some of the outputs. This example is also located in ``src/fusedwind/examples/turbine/fused_turbine_geom_example.py``. 

.. literalinclude:: ../src/fusedwind/examples/turbine/turbine_geom_example.py
    :start-after: # --- 2
    :end-before: # --- 3

.. _bladesurface_planform-fig:


    .. image::  images/chord.*
       :width: 49 %
    .. image::  images/twist.*
       :width: 49 %
    .. image::  images/rthick.*
       :width: 49 %
    .. image::  images/p_le.*
       :width: 49 %


.. _bladesurface_lofted-blade-fig:

.. figure:: /images/lofted_blade.*
    :width: 70 %
    :align: center

    Lofted blade shape.


Blade Structure Example
+++++++++++++++++++++++

The blade structure parameterization is primarily aimed for conceptual analysis and optimization, 
where the geometric detail is fairly low to enable its use more efficiently in an optimization context.

On a cross sectional level, the internal structure is defined in a ``CrossSectionStructureVT`` VariableTree object.
A cross-section is divided into a number of *regions* that each cover a fraction of the cross-section, defined in a ``Region`` VariableTree object. Each region, contains a stack of materials contained in a list of ``Layer`` vartrees.
In each layer, the material type, thickness and layup angle can be specified.
The materials used in the blade are specified in the ``MaterialProps`` variable tree, which holds a set of apparent material properties based on the properties of the constituent materials, which need to be pre-computed using simple micromechanics equations and classical lamination theory.

The figure below shows a blade cross section where the region division points (DPs) are indicated.
The location of each DP is specified as a normalized arc length along the cross section 
starting at the trailing edge pressure side with a value of s=-1., and along the surface to the leading edge where s=0., 
along the suction side to the trailing edge where s=1.
Any number of regions can thus be specified, distributed arbitrarily along the surface.

.. _bladestructure_cross_sec-fig:

.. figure:: /images/cross_sec_sdef13.*
    :width: 80 %
    :align: center

    Blade cross section with region division points (DPs) indicated with red dots and shear webs drawn as green lines.

The spar caps are specified in the same way as other regions, which means that their widths and position along the chord are not default parameters.
It is presently only possible to place shear webs at the location of a DP, which means that a single shear web topology would require the spar cap to be split into two regions.

The full blade parameterization is a simple extrusion of the cross-sectional denition, where every region covers the entire span of the blade.
The DP curves marked with red dots in the plot below are simple 1-D arrays as function of span that as in the cross-sectional definition take a value between -1. and 1.
The distribution of material and their layup angles along the blade are also specified as simple 1-D arrays as function of span.
Often, a specific composite will not cover the entire span, and in this case the thickness of this material is simply specified to be zero at that given spanwise location.

.. _bladestructure_lofted-blade-fig:

.. figure:: /images/structural_cross_sections.*
    :width: 15cm
    :align: center

    Lofted blade with region division points indicated with red dots and shear webs drawn as green lines.

FUSED-Wind provides methods to easily parameterize and spline the structural definition of a wind turbine blade and build a list of cross-sectional definitions of the blade structure for use with cross-sectional structure codes such as PreComp or BECAS.
The workflow contains a number of components:

* Blade planform spliner component
* Lofted blade surface component
* Blade structural data reader component
* Blade structural data spliner component
* Blade cross-sectional structure builder component
* Blade structural data writer component

In the example below, we show how to hook up an assembly with a complete lofted shape and structural definition of the DTU 10MW RWT.
The example and data is located in ``src/fusedwind/examples/turbine/turbine_structure_example.py``.

.. literalinclude:: ../src/fusedwind/examples/turbine/turbine_structure_example.py
    :start-after: # --- 1
    :end-before: # --- 2

The ``configure_bladestructure`` method associates an FFD spline component to each of the blade planform curves and blade material thickness and angle distributions and *DP* curves that defines the blade structure.
The starting point of all the splines is zero, so if we add a pertubation to one of the splines, e.g. the blade chord and spar cap uniax thickness, we can see how that changes the two curves:

.. literalinclude:: ../src/fusedwind/examples/turbine/turbine_structure_example.py
    :start-after: # --- 2
    :end-before: # --- 3

.. _bladeplanform_spline-fig:

.. figure:: /images/chord_ffd_spline.*
    :width: 80 %
    :align: center

    Blade chord pertubation.

.. literalinclude:: ../src/fusedwind/examples/turbine/turbine_structure_example.py
    :start-after: # --- 3
    :end-before: # --- 4


.. _bladestructure_spline-fig:

.. figure:: /images/turbine_structure_uniax_perturb.*
    :width: 80 %
    :align: center

    Blade spar cap uniax thickness pertubation.

