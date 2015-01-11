
.. _about-label:

Overview
========

Framework for Unified Systems Engineering and Design of Wind Plants (FUSED-Wind) is a framework for integrated system modeling of wind plants.
FUSED-Wind was started as a collaboration between DTU Wind Energy and NREL to help standardize the way wind turbine and plant software models are integrated together for holistic systems analysis, design and optimization.
FUSED-Wind does *not* provide any analysis models or interfaces to specific codes.
Instead, the aim with FUSED-Wind is to provide a variety of *generalized* interfaces for integrating wind turbine and plant specific software models together so that these models can be mixed and matched for a huge variety of different analyses.

FUSED-Wind is built on `OpenMDAO <http://openmdao.org/>`_ which is an open-source software from NASA Glenn Laboratories for multi-disciplinary design analysis and optimization (MDAO) of complex technical systems. 
It is designed specifically to support advanced analyses that combine several models of potentially varying levels of complexity together for MDAO, uncertainty quantification, design of experiments, and many more applications! 

FUSED-Wind is a free open-source software released under the `Apache 2 <http://www.apache.org/licenses/LICENSE-2.0>`_ license, which is very permissive, allowing users of the framework to use it for any purpose, to modify it and re-distribute it as part of their own software.
The framework is released under this license to encourage community contributions with the belief that as a community we can create something better and more widely applicapable than on our own.

Target Audience
---------------

Since FUSED-Wind itself does not contain any analysis codes, FUSED-Wind is primarily targetted at model developers who wish to use their model in an multidisciplinary analysis and optimization context.
You need to have some knowledge of software development, be familiar with Python and need to have made yourself acquainted with OpenMDAO and its concepts.
Are you a user with no desire to develop your own models, both NREL and DTU have developed more user friendly software packages based on OpenMDAO and FUSED-Wind that enable complex analysis of wind energy systems based on simple user interfaces that do not require programming experience, see for example `WISDEM <http://nwtc.nrel.gov/WISDEM>`_ or `TOPFARM <https://zenodo.org/search?f=keyword&p=%22TOPFARM%22&ln=en>`_.

Modules
-------

The current version of FUSED-Wind is organized into three primary modules:
 
* Plant Flow
    Interfaces related to wind turbine plant scale flow codes and wake models.
    The interfaces provide the basis for wind farm layout optimization.
* Plant Cost
    Interfaces and configure methods related to wind turbine and plant financial analysis models, such as capital costs, balance of station costs, operational expenditures and finance.
* Turbine
    Interfaces related to turbine analysis codes, such as aerodynamic, aeroelastic and structural codes.
    The module also contains parameterizations for the turbine geometry suited for conceptual design.

Basic Concepts
--------------

Since FUSED-Wind builds on OpenMDAO, the framework operates with the same basic building blocks as OpenMDAO.
The interfaces defined in the framework consist of three primary parts:

* Variable Trees
    FUSED-Wind defines key input and output variables for different types of analysis of wind plants.
    Variables are grouped logically into *Variable Trees*, that makes it easier to pass sets of
    I/O between codes.
* Components
    A *Component* in OpenMDAO is a class that takes a set of inputs and performs some operation on these, resulting
    in a set of outputs.
    FUSED-Wind defines a range of base classes with pre-defined sets of inputs and outputs commonly used in different types of analysis of wind energy systems.
* Assemblies
    An OpenMDAO Assembly is a container for a specific *workflow* defined by a series of components whose inputs and outputs are connected in a specific manner to perform a certain type of analysis.
    FUSED-Wind defines a range of commonly used workflows of varying complexity such as AEP calculation of a wind farm, or cost analysis of a wind turbine.

Based on these sets of component interfaces and workflows, users can develop a model that *implements* specific FUSED-Wind interfaces, making this model compatible with the rest of the framework, and other models also interfaced to the framework.
While adhering to a certain interface may seem very restrictive when developing a stand-alone model, we believe that this restriction is far outweighed by the host of other models and methods that will become available through this effort.
