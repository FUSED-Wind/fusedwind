
from openmdao.main.api import VariableTree
from openmdao.main.datatypes.api import Str, Float, Array, List


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
