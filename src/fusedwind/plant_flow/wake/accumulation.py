
from numpy import zeros, array, sqrt
from fusedwind.plant_flow.fused_plant_comp import GenericWakeSum

class LinearWakeSum(GenericWakeSum):
    """
    Sum the wakes linearly
    """
    def execute(self):
        # Create the output
        self.ws_array = zeros(self.ws_array_inflow.shape)
        # loop on the points
        if len(self.wakes) == 0:
            self.ws_array = self.ws_array_inflow
        else:
            for i in range(self.ws_array_inflow.shape[0]):
                DUs = array([wake[i] / self.ws_array_inflow[i] for wake in self.wakes])
                self.ws_array[i] = self.ws_array_inflow[i] * (1 - sum(DUs))


class QuadraticWakeSum(GenericWakeSum):
    """
    Sum the wakes quadratically (square root sum of the squares).
    Used typically in relation with the NOJ, MozaicTile wake models.
    """
    def execute(self):
        # Create the output
        self.ws_array = zeros(self.ws_array_inflow.shape)
        # loop on the points
        if len(self.wakes) == 0:
            self.ws_array = self.ws_array_inflow
        else:
            for i in range(self.ws_array_inflow.shape[0]):
                # Calculate the normalized velocities deficits
                DUs = array([wake[i] / self.ws_array_inflow[i] for wake in self.wakes])
                self.ws_array[i] = self.ws_array_inflow[i] * (1 - sqrt(sum(DUs ** 2.0)))


class EnergyBalanceWakeSum(GenericWakeSum):
    """
    Sum the wakes linearly
    """
    def execute(self):
        # Create the output
        self.ws_array = zeros(self.ws_array_inflow.shape)
        # loop on the points
        if len(self.wakes) == 0:
            self.ws_array = self.ws_array_inflow
        else:
            for i in range(self.ws_array_inflow.shape[0]):
                DUs = array([self.ws[j] - wake[i]**2.0 for wake in self.wakes])
                self.ws_array[i] = sqrt(self.ws_array_inflow[i]**2.0 - sum(DUs))
