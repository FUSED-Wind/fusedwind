FUSED-Wind
==========

# Overview

Welcome to the Framework for Unified Systems Engineering and Design of Wind
Turbine Plants ( FUSED-Wind).
This is an open-source framework for multi-disciplinary optimisation and
analysis (MDAO) of wind energy systems, developed jointly by DTU and NREL.
The framework is designed as an extension to the NASA developed OpenMDAO, and
defines key I/O elements and methods necessary for wiring together different
simulation codes in order to achieve a system level analysis capability of wind
turbine plants with multiple levels of fidelity.
NREL and DTU have developed independent interfaces to their respective
simulation codes and cost models (e.g. FAST/CCBlade, HAWC2/BECAS) with the aim
of offering an environment where these codes can be used interchangeably.
The open source nature of the framework enables third parties to develop
interfaces to their own tools, either replacing or extending those offered by
DTU and NREL.

# Dependencies and supported Python versions

FUSED-Wind depends on [OpenMDAO](http://www.openmdao.org) and support python
2.7.x. Some modules also depends on [pandas](http://pandas.pydata.org).

# Development installation

First install OpenMDAO development from their [repository](https://github.com/OpenMDAO/OpenMDAO-Framework)
and activate its virtual environment.

Then run the following commands to download and install FUSED-Wind

    $ git clone https://github.com/FUSED-Wind/fusedwind.git
    $ cd fusedwind
    $ plugin install

# Documentation

The documentation will be available soon on the [project website](fusedwind.org).

# Tutorials and Examples

The tutorials and examples will be available soon in another repository.

# Reporting bugs

Please use git [issue tracker](https://github.com/FUSED-Wind/fusedwind/issues) for reporting bugs.

# Contacts

If you want more information about the platform, please contact the following authors

**DTU:**
[Pierre-Elouan Réthoré](mailto:pire@dtu.dk),
[Frederik Zahle](mailto:frza@dtu.dk),

**NREL:**
[Katherine Dykes](mailto:katherine.dykes@nrel.gov),
[Peter Graf](mailto:Peter.Graf@nrel.gov),
[Andrew Ning](mailto:aning@byu.edu)
