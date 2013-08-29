#!/usr/bin/env python
# encoding: utf-8

from openmdao.main.api import Assembly
from openmdao.main.datatypes.api import Slot

from fusedwind.components.airfoil import ReadAirfoilBase, ModifyAirfoilBase, WriteAirfoilBase


class AirfoilPreprocessingAssembly(Assembly):

    # for the benefit of the GUI
    read = Slot(ReadAirfoilBase)
    mod1 = Slot(ModifyAirfoilBase)
    mod2 = Slot(ModifyAirfoilBase)
    mod3 = Slot(ModifyAirfoilBase)
    write = Slot(WriteAirfoilBase)


    def configure(self):

        self.add('read', ReadAirfoilBase())
        self.add('mod1', ModifyAirfoilBase())
        self.add('mod2', ModifyAirfoilBase())
        self.add('mod3', ModifyAirfoilBase())
        self.add('write', WriteAirfoilBase())

        self.driver.workflow.add(['read', 'mod1', 'mod2', 'mod3', 'write'])

        self.connect('read.afOut', 'mod1.afIn')
        self.connect('mod1.afOut', 'mod2.afIn')
        self.connect('mod2.afOut', 'mod3.afIn')
        self.connect('mod3.afOut', 'write.afIn')

        self.create_passthrough('read.fileIn')
        self.create_passthrough('write.fileOut')
