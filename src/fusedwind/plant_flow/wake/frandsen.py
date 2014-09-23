## FUSED-Wake imports
from wake import WindFarmWake, \
    HomogeneousInflowGenerator, \
    HubCenterWSPosition, HubCenterWS, GenericEngineeringWakeModel

from accumulation import QuadraticWakeSum

## Moved to FUSED-Wind plugin
#from fused_wake.io import GenericWindTurbineVT
#from fused_wake.windturbine import WindTurbinePowerCurve
#from io import GenericWindTurbineVT

## FUSED-Wind imports
from fusedwind.plant_flow.fused_plant_vt import GenericWindTurbineVT
from fusedwind.plant_flow.fused_plant_comp import WindTurbinePowerCurve

## OpenMDAO imports
from openmdao.lib.datatypes.api import VarTree, Float, Int

## Other imports
from numpy import sin, pi, sqrt, arccos

class FrandsenWakeModel(GenericEngineeringWakeModel):
    """
    The Frandsen wake model, described in the article:
    Frandsen et al. Analytical Modelling of Wind Speed Deficit in Large Offshore Wind Farms, Wind Energy.
    and Storpark Analytical Model(SAM) that was presented at the European Wind Energy Conference and Exhibition 2006
    """
    k = Float(2.0, iotype='in', desc='expansion exponent')
    alpha = Float(0.7, iotype='in', desc='expansion parameter')
    version = Int(1, min=1, max=2, iotype='in', desc='wake expansion version')

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

        D = self.wt_desc.rotor_diameter
        R =  D / 2.0
        A = pi * R**2.0
        #Rw = abs(R + self.k * X)  # upstream turbine wake radius

        beta = (1.0 + sqrt(1.0 - self.c_t)) / (2.0 * sqrt(1.0 - self.c_t))

        if self.version == 1:
            Rw = R * (beta**(self.k / 2.0) + self.alpha * X / D)**(1.0/self.k)            
        elif self.version == 2:
            Rw = R * max(beta, self.alpha * X / D)**(1.0/2.0)            

        Aw = pi * Rw**2.0
        DU = 0.5 * (1.0 - sqrt(1.0 - 2.0 * self.c_t * A / Aw))

        # There is a downstream wind turbine, so we activate the partial wake
        # calculation
        cR = self.down_wt_desc.rotor_diameter / 2.0
        if dr + cR < Rw:
            # Complete wake
            return - DU
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
            return - DU


class FrandsenWindFarmWake(WindFarmWake):

    """
    The Fransen wind farm wake model.
    """
    def configure(self):
        super(FrandsenWindFarmWake, self).configure()
        self.replace('ws_positions', HubCenterWSPosition())
        self.replace('wake_sum', QuadraticWakeSum())
        self.replace('hub_wind_speed', HubCenterWS())
        self.replace('wt_model', WindTurbinePowerCurve())
        self.replace('wake_model', FrandsenWakeModel())
        self.replace('inflow_gen', HomogeneousInflowGenerator())
        if 'k' not in self.list_inputs():
            self.create_passthrough('wake_model.k')
        self.wake_driver.wt_connections.append('wake_model.down_wt_desc')            
