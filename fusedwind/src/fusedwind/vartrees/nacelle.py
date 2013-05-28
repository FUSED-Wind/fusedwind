#!/usr/bin/env python
# encoding: utf-8

from openmdao.main.api import VariableTree
from openmdao.main.datatypes.api import Float, Bool, Str, Enum


class DrivetrainVT(VariableTree):

    drivetrainDesign = Enum('3stage', ('3stage', 'singlespeed', 'multigenerator', 'directdrive'),
        desc='drivetrain configuration type')
    gearRatio = Float(97.0, desc='overall gear ratio of gearbox')
    gearConfig = Str('eep', desc='gearbox configuration')
    crane = Bool(True, desc='boolean for presence of a service crane up tower')
