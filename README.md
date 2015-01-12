FUSED-Wind
==========
[![Stories in Ready](https://badge.waffle.io/FUSED-Wind/fusedwind.svg?label=ready&title=Ready)](http://waffle.io/FUSED-Wind/fusedwind)


# Overview

Framework for Unified Systems Engineering and Design of Wind
Plants ( FUSED-Wind) is an open-source framework for multi-disciplinary optimisation and
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

Python 2.7.x, NumPy, SciPy > 0.14.0, OpenMDAO <= 0.10.3.2, Pandas

# Installation

First install OpenMDAO. The most practical way of doing this is to clone into the OpenMDAO-Framework git [repository](https://github.com/OpenMDAO/OpenMDAO-Framework)
since upgrading to new releases will then be a lot simpler.
FUSED-Wind currently only supports OpenMDAO <= v0.10.3.2, since the framework has undergone significant changes since then, which have not yet been tested for FUSED-Wind.

    $ cd git
    $ git clone https://github.com/OpenMDAO/OpenMDAO-Framework.git
    $ git checkout 0.10.3.2  

Alternatively, you can navigate to http://openmdao.org/downloads/recent/ and follow the installation instructions for the v0.10.3.2 release.

Then run the following commands to download and install FUSED-Wind

    $ git clone https://github.com/FUSED-Wind/fusedwind.git
    $ cd fusedwind
    $ plugin install

# Run Unit Tests

To check if the installation was successful try to import the module

    $ python
    > import fusedwind

or run the unit tests

    $ python -m unittest discover 'src/fusedwind/test' 'test_*.py'

An "OK" signifies that all the tests passed.

# Documentation, Tutorials and Examples

The documentation is available on the [project website](http://www.fusedwind.org) 
along with tutorials and examples.
The source code for all examples is located in ``src/fusedwind/examples``.

# Reporting bugs

Please use git [issue tracker](https://github.com/FUSED-Wind/fusedwind/issues) for reporting bugs.
You can follow the progress of the project on our [Waffle page](https://waffle.io/FUSED-Wind/fusedwind).

# Contacts

If you want more information about the platform, please contact the following authors

**DTU:**
[Pierre-Elouan Réthoré](mailto:pire@dtu.dk),
[Frederik Zahle](mailto:frza@dtu.dk),

**NREL:**
[Katherine Dykes](mailto:katherine.dykes@nrel.gov),
[Peter Graf](mailto:Peter.Graf@nrel.gov),
[Andrew Ning](mailto:aning@byu.edu)
