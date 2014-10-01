.. module:: fusedwind

.. _interfaces-label:

Documentation
-------------

Fused Wind consists of a collection of tools aimed at a level of abstraction that can be shared
across different simulation tools (e.g. FAST vs HAWC2).  Here we describe some of the concepts and
codebases in use for this ongoing project.

Run Batch
=========

The :mod:`fusedwind.runSuite.runCaseGenerator` and :mod:`fusedwind.runSuite.runBatch` modules facilitate high throughput aeroelastic simulation via a generic
interface that can accomodate a variety of specifc wind codes.  The philosophy of the tool is illustrated in
the following figure (:num:`Figure #batchrunner-fig`):

.. _batchrunner-fig:

.. figure:: /images/batchrunner.pdf
    :height: 1.5in
    :align: center

    The separation of case generation and case execution implementated by fusedwind's runCaseGenerator and runBatch classes.


Run Case Generator
^^^^^^^^^^^^^^^^^^
.. automodule:: fusedwind.runSuite.runCaseGenerator
  :members:
  :special-members:

Case Runner
^^^^^^^^^^^
.. automodule:: fusedwind.runSuite.runBatch
  :members:
  :special-members:

Plant Flow
==========

Variable Trees
^^^^^^^^^^^^^^
.. automodule:: fusedwind.plant_flow.vt
  :members:
  :special-members:

Components
^^^^^^^^^^
.. automodule:: fusedwind.plant_flow.comp
  :members:
  :special-members:

Assemblies
^^^^^^^^^^
.. automodule:: fusedwind.plant_flow.asym
  :members:
  :special-members:
