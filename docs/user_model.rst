
.. _user-model-label:


Writing a FUSED-Wind Compatible Model
-------------------------------------

This tutorial provides a guide on how to develop a FUSED-Wind compatible model.
It will introduce you to the *interface decorators* that are used in FUSED-Wind to declare and implement interfaces and give a practical example of how to wrap a code for predicting the aerodynamic loads on a rotor.

Instead of using class inheritance to implement an I/O interface, FUSED-Wind uses so-called *decorators* to declare which interfaces a class adheres to.
While you can still use inheritance to implement the methods that base classes declare, you still need to use decorators to declare I/O.
The reason for this is that parent class dependencies can often become deep, making it very difficult to see *all* the I/O that a class has if it inherits from a parent.

What is a decorator then? 
A decorator allows you to inject or even modify code in functions or classes or run a set of operations on these every time they are run.
In our usage, decorators are used to *declare a base class* (``@base``), be it a Variable Tree, Component or Assembly, or to declare that a class *implements* a base class (``@implement_base``).
A third decorator is ``@configure_base`` which operates on methods and is used to check that an already instantiated class adheres to a given list of interfaces.

Lets take a look at a practical example where we wish to write an interface to a code for predicting the aerodynamic loads on a wind turbine rotor.


.. literalinclude:: ../src/fusedwind/examples/turbine/rotoraero_model.py


In this case our class inherits from ``Component``, but often codes are not python-based and need to be executed externally.
In this case, you can use OpenMDAO's ``ExternalCode`` class, which inherits from ``Component`` and adds some methods to more easily execute codes on the system.