#__all__ = ['fused_wake']

## FUSED-Wake imports
from wake import GenericWindFarmWake, \
    HomogeneousInflowGenerator, QuadraticWakeSum, \
    HubCenterWSPosition, HubCenterWS, GenericEngineeringWakeModel

## Moved to FUSED-Wind plugin
#from fused_wake.io import GenericWindTurbineVT
#from fused_wake.windturbine import WindTurbinePowerCurve
#from io import GenericWindTurbineVT

## FUSED-Wind imports
from fusedwind.plant_flow.fused_plant_vt import GenericWindTurbineVT
from fusedwind.plant_flow.fused_plant_comp import WindTurbinePowerCurve

## OpenMDAO imports
from openmdao.lib.datatypes.api import VarTree, Float

## Other imports
from numpy import sin, pi, sqrt, arccos


class NOJWakeModel(GenericEngineeringWakeModel):

    """
    The N.O. Jensen wake model.
    """
    k = Float(0.04, iotype='in', desc='The wake spreading parameter')

    def single_wake(self, X, dr, ws):
        """
        X : Stream wise wake distance
        dr: Cross wise wake distance
        ws: local inflow wind speed

        Output:
        DU: the axial velocity deficit
        """
        if X <= 0.0:
            # No wake upstream in this model!
            return 0.0

        R = self.wt_desc.rotor_diameter / 2.0
        # NOJ Specific
        Rw = R + self.k * X  # upstream turbine wake radius
        DU = (1.0 - sqrt(1.0 - self.c_t)) / (1.0 + (self.k * X) / R) ** 2.0

        if dr < abs(Rw):
            return - ws*DU
        else:
            return 0.0


class MozaicTileWakeModel(NOJWakeModel):

    """
    The N.O. Jensen wake model, the wake model will assume that there is a
    downstream wind turbine, and the deficit will be calculated
    using the mozaic tile approach.
    """
    down_wt_desc = VarTree(GenericWindTurbineVT(), iotype='in',
                           desc='Downstream wind turbine descriptor (only used when partial=True)')

    def single_wake(self, X, dr, ws):
        """
        X : Stream wise wake distance
        dr: Cross wise wake distance
        ws: local inflow wind speed


        Output:
        Return the axial velocity deficit
        """
        if X <= 0.0:
            # No wake upstream in this model!
            return 0.0

        R = self.wt_desc.rotor_diameter / 2.0
        Rw = abs(R + self.k * X)  # upstream turbine wake radius
        DU = (1.0 - sqrt(1.0 - self.c_t)) / (1.0 + (self.k * X) / R) ** 2.0

        # There is a downstream wind turbine, so we activate the partial wake
        # calculation
        cR = self.down_wt_desc.rotor_diameter / 2.0
        if dr + cR < Rw:
            # Complete wake
            return - ws*DU
        elif dr > cR + Rw:
            # Outside the wake
            return 0.0
        else:
            # Partial wake
            alpha1 = 2.0 * arccos((
                cR ** 2.0 + dr ** 2.0 - Rw ** 2.0) / (2.0 * cR * abs(dr)))
            alpha2 = 2.0 * arccos((
                Rw ** 2.0 + dr ** 2.0 - cR ** 2.0) / (2.0 * Rw * abs(dr)))
            qki = (0.5 * cR ** 2.0 * (alpha1 - sin(alpha1)) + 0.5 * Rw ** 2.0 * (
                alpha2 - sin(alpha2))) / (pi * cR ** 2.0)
            DU = (DU * qki)
            return - ws*DU


class NOJWindFarmWake(GenericWindFarmWake):

    """
    The Original NOJ model.
    """
    def configure(self):
        super(NOJWindFarmWake, self).configure()
        self.replace('ws_positions', HubCenterWSPosition())
        self.replace('wake_sum', QuadraticWakeSum())
        self.replace('hub_wind_speed', HubCenterWS())
        self.replace('wt_model', WindTurbinePowerCurve())
        self.replace('wake_model', NOJWakeModel())
        self.replace('inflow_gen', HomogeneousInflowGenerator())
        if 'k' not in self.list_inputs():
            self.create_passthrough('wake_model.k')


class MozaicTileWindFarmWake(NOJWindFarmWake):

    """
    The Mozaic Tile model from Rathmann. Based on the NOJ model.
    """
    def configure(self):
        super(MozaicTileWindFarmWake, self).configure()
        self.replace('wake_model', MozaicTileWakeModel())
        self.wake_driver.wt_connections.append('wake_model.down_wt_desc')

    def configure_single_turbine_type(self):
        super(MozaicTileWindFarmWake, self).configure_single_turbine_type()
        self.connect('wt_list[0]', 'wake_model.down_wt_desc')


