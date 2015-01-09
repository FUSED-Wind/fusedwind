

Run Batch Tutorials
-----------------------

The :mod:`fusedwind.runSuite.runCaseGenerator` and :mod:`fusedwind.runSuite.runBatch` modules facilitate high throughput aeroelastic simulation via a generic
interface that can accomodate a variety of specifc wind codes.  The philosophy of the tool is illustrated in
the following figure (:num:`Figure #batchrunner-fig`):

.. _batchrunner-fig:

.. figure:: /images/batchrunner.*
    :height: 1.5in
    :align: center

    The separation of case generation and case execution implementated by fusedwind's runCaseGenerator and runBatch classes.


Run Case Generator
^^^^^^^^^^^^^^^^^^
.. automodule:: fusedwind.runSuite.runCaseGenerator
  :members:

Case Runner
^^^^^^^^^^^
.. automodule:: fusedwind.runSuite.runBatch
  :members:
