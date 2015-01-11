
.. _developer-guide-label:

Developer Guide
===============

Contributing
------------

FUSED-Wind is an open-source initiative licensed under the `Apache 2 license <http://www.apache.org/licenses/LICENSE-2.0>`_ ,
with the intent to encourage contributions from external developers of wind components, turbine or plant models.
To contribute to the FUSED-Wind code, we encourage you to read the `OpenMDAO developer guide <http://openmdao.org/dev_docs/#openmdao-developer-guide>`_
which also explains how to develop an OpenMDAO *plugin*.
To contribute code into FUSED-Wind you should follow the `fork & pull <https://help.github.com/articles/using-pull-requests/>`_
approach.

Adding Models to FUSED-Wind
---------------------------

In the :ref:`tutorial-label`, you can follow a number of examples on how to develop an interface to your own model.
It is possible that an interface suitable for your model is not defined in FUSED-Wind, or your model requires inputs or provides outputs which are not defined either.
In this case, we encourage you to suggest to include these variables or interfaces in FUSED-Wind.
In general such interfaces and variables will be included if they are needed to couple to other models.
If they are very specific to your model, we suggest that you define these in your own distribution.
