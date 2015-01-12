
import copy
import numpy as np

from openmdao.main.api import VariableTree
from openmdao.main.datatypes.api import Str, Float, Array, List

from fusedwind.interface import base

@base
class AirfoilDataVT(VariableTree):
    """
    airfoil data at a specific Reynolds number over of range of angles of attack
    """

    desc = Str(desc='Description of data, i.e. airfoil name, flow conditions (clean/rough) etc')
    Re = Float(desc='Reynolds number')
    alpha = Array(units='deg', desc='angles of attack')
    cl = Array(desc='corresponding lift coefficients')
    cd = Array(desc='corresponding drag coefficients')
    cm = Array(desc='corresponding pitching moment coefficients')


@base
class AirfoilDatasetVT(VariableTree):
    """
    List of AirfoilDataVT datasets

    The ``interpolator`` parameter can be used to characterize the list of data
    in terms of e.g. Reynolds number, relative thickness, TE flap angle, roughness ratio etc,
    and should have the same length as the number of polars.
    """

    desc = Str(desc='Description of dataset')
    interpolator = Array(desc='The interpolator could characterize e.g. TE flap angle, roughness ratio etc')
    polars = List(AirfoilDataVT, desc='List of AirfoilDataVT')


@base
class AirfoilDataExtVT(AirfoilDataVT):
    """
    Extended airfoil polar data
    """

    alpha_rel = Array(units='deg', desc='angles of attack relative to alpha|Cl=0')
    clcd = Array(desc='corresponding lift coefficients')
    xtr_s = Array(desc='chordwise suction side transition points')
    xtr_p = Array(desc='chordwise pressure side transition points')
    xsep_s = Array(desc='chordwise suction side transition points')
    xsep_p = Array(desc='chordwise pressure side transition points')


@base
class AirfoilBLdata(VariableTree):
    """
    Airfoil boundary layer parameters
    """
    x = Array(desc='chordwise discretization')
    dstar_s = Array(desc='suction side displacement thickness')
    dstar_p = Array(desc='pressure side displacement thickness')
    theta_s = Array(desc='suction side momentum thickness')
    theta_p = Array(desc='pressure side momentum thickness')
    hk_s = Array(desc='suction side shape factor')
    hk_p = Array(desc='pressure side shape factor')
    cf_s = Array(desc='suction side skin friction coefficient')
    cf_p = Array(desc='pressure side skin friction coefficient')
    cp_s = Array(desc='suction side pressure coefficient')
    cp_p = Array(desc='pressure side pressure coefficient')
