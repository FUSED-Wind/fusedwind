
Installation
==============

.. admonition:: Prerequisites
   :class: note

   Python 2.7.x, NumPy, SciPy > 0.14.0, OpenMDAO <= 0.10.3.2, Pandas

First install OpenMDAO. The most practical way of doing this is to clone into the OpenMDAO-Framework git `repository <https://github.com/OpenMDAO/OpenMDAO-Framework>`_
since upgrading to new releases will then be a lot simpler.
FUSED-Wind currently only supports OpenMDAO <= v0.10.3.2, since the framework has undergone significant changes since then, which have not yet been tested for FUSED-Wind.

.. code-block:: bash

    $ cd git
    $ git clone https://github.com/OpenMDAO/OpenMDAO-Framework.git
    $ git checkout 0.10.3.2  

Alternatively, you can navigate to http://openmdao.org/downloads/recent/ and follow the installation instructions for the v0.10.3.2 release.

Then run the following commands to download and install FUSED-Wind

.. code-block:: bash

    $ git clone https://github.com/FUSED-Wind/fusedwind.git
    $ cd fusedwind
    $ plugin install

To check if the installation was successful try to import the module

.. code-block:: bash

    $ python

.. code-block:: python

    > import fusedwind

or run the unit tests:

.. code-block:: bash

   $ python -m unittest discover 'src/fusedwind/test' 'test_*.py'

An "OK" signifies that all the tests passed.

.. only:: latex

    An HTML version of this documentation that contains further details and links to the source code is available at `<http://fusedwind.org/index.html>`_

If you want to have the documentation available while offline, the documentation can be built locally on your machine using Sphinx.
To do this you need to install a few dependencies:

.. code-block:: bash

   pip install numpydoc sphinxcontrib-bibtex sphinxcontrib-zopeext sphinxcontrib-napoleon

Once installed, the docs can be built using the command

.. code-block:: bash

    $ cd fusedwind/docs
    $ make html

To view the docs open the file _build/html/index.html in a web browser.
