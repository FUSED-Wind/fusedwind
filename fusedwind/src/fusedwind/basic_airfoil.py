#!/usr/bin/env python
# encoding: utf-8


from openmdao.main.api import Component, Assembly, VariableTree
from openmdao.main.datatypes.api import Float, Array, Slot, Str, List


# ------- variable trees ---------

class PolarDataVT(VariableTree):
    """airfoil data at a given Reynolds number"""

    alpha = Array(units='deg', desc='angles of attack')
    cl = Array(desc='corresponding lift coefficients')
    cd = Array(desc='corresponding drag coefficients')
    cm = Array(desc='corresponding pitching moment coefficients')



class AirfoilDataVT(VariableTree):

    Re = Array(desc='Reynolds number')
    polars = List(PolarDataVT, desc='corresponding Polar data')


# ------------------------------------


# ------- base classes ----------

class BasicAirfoilBase(Component):
    """Evaluation of airfoil at angle of attack and Reynolds number"""

    # inputs
    alpha = Float(iotype='in', units='deg', desc='angle of attack')
    Re = Float(iotype='in', desc='Reynolds number')

    # outputs
    cl = Float(iotype='out', desc='lift coefficient')
    cd = Float(iotype='out', desc='drag coefficient')
    cm = Float(iotype='out', desc='pitching moment coefficient')


def airfoilForces(airfoil, alpha, Re):
    """convenience method to use BasicAirfoilBase
    as a regular python function as opposed to a component"""

    airfoil.alpha = alpha
    airfoil.Re = Re
    airfoil.run()
    return airfoil.cl, airfoil.cd, airfoil.cm



class ModifyAirfoilBase(Component):
    """Used for extrapolation, 3D corrections, etc."""

    # inputs
    afIn = Slot(AirfoilDataVT, iotype='in', desc='tabulated airfoil data')

    # outputs
    afOut = Slot(AirfoilDataVT, iotype='out', desc='tabulated airfoil data')

    def __init__(self):
        super(ModifyAirfoilBase, self).__init__()
        self.afIn = AirfoilDataVT()
        self.afOut = AirfoilDataVT()



class ReadAirfoilBase(Component):
    """Read airfoil data from a file"""

    # inputs
    fileIn = Str(iotype='in', desc='name of file')

    # outputs
    afOut = Slot(AirfoilDataVT, iotype='out', desc='tabulated airfoil data')

    def __init__(self):
        super(ReadAirfoilBase, self).__init__()
        self.afOut = AirfoilDataVT()



class WriteAirfoilBase(Component):
    """Write airfoil data to a file"""

    # inputs
    afIn = Slot(AirfoilDataVT, iotype='in', desc='tabulated airfoil data')
    fileOut = Str(iotype='in', desc='name of file')

    def __init__(self):
        super(WriteAirfoilBase, self).__init__()
        self.afIn = AirfoilDataVT()



# ---------------------------




# ------- assemblies -------------

class AirfoilPreprocessingAssembly(Assembly):

    # for the benefit of the GUI
    read = Slot(ReadAirfoilBase)
    correct3D = Slot(ModifyAirfoilBase)
    extrapolate = Slot(ModifyAirfoilBase)
    write = Slot(WriteAirfoilBase)


    def configure(self):

        self.add('read', ReadAirfoilBase())
        self.add('correct3D', ModifyAirfoilBase())
        self.add('extrapolate', ModifyAirfoilBase())
        self.add('write', WriteAirfoilBase())

        self.driver.workflow.add(['read', 'correct3D', 'extrapolate', 'write'])

        self.connect('read.afOut', 'correct3D.afIn')
        self.connect('correct3D.afOut', 'extrapolate.afIn')
        self.connect('extrapolate.afOut', 'write.afIn')

        self.create_passthrough('read.fileIn')
        self.create_passthrough('write.fileOut')


# ---------------------------------




