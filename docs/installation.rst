Installation
------------

.. admonition:: Prerequisites
   :class: warning

   Python 2.7.x, NumPy, SciPy, OpenMDAO, Pandas

First install OpenMDAO development from their `repository <https://github.com/OpenMDAO/OpenMDAO-Framework>`_
and activate its virtual environment.

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
