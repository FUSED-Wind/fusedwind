
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

Writing a FUSED-Wind Compatible Model
-------------------------------------

This tutorial provides a guide on how to develop a FUSED-Wind compatible model.
It will introduce you to the *interface decorators* that are used in FUSED-Wind to declare and implement interfaces and give a practical example of how to wrap a code for predicting the aerodynamic loads on a rotor.

