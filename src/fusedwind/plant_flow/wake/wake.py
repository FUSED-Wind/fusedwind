#__all__ = ['fused_wake']

from numpy import array, log, zeros, cos, sin, nonzero, argsort, ones, arange, pi, sqrt, dot
from numpy.linalg.linalg import norm
from openmdao.lib.datatypes.api import VarTree, Float, Slot, Array, List, Int, Str, Instance
from openmdao.lib.drivers.api import CaseIteratorDriver
from openmdao.main.api import Driver
from openmdao.main.api import Component, Assembly
from openmdao.lib.casehandlers.api import ListCaseRecorder, ListCaseIterator
from openmdao.main.interfaces import ICaseIterator
from openmdao.main.case import Case

## FUSED-Wind imports
from fusedwind.plant_flow.vt import GenericWindTurbineVT, GenericWindTurbinePowerCurveVT, \
    ExtendedWindTurbinePowerCurveVT, GenericWindFarmTurbineLayout, \
    GenericWindRoseVT
from fusedwind.plant_flow.comp import GenericWindTurbine, GenericWSPosition, HubCenterWSPosition, GenericWakeSum, GenericHubWindSpeed, GenericFlowModel, GenericWakeModel
from fusedwind.plant_flow.asym import GenericWindFarm
from fusedwind.interface import base, implement_base, InterfaceSlot, \
    FUSEDAssembly, configure_base

# Wake Model stuffs ######################################################
# TODO: Move this to somewhere more general?
# Define the rotation matrices function in the X direction
RotX = lambda a: array([[1,         0,        0],
                        [0,       cos(a),   -sin(a)],
                        [0,       sin(a),   cos(a)]])
# Define the rotation matrices function in the Y direction
RotY = lambda a: array([[cos(a),    0,      sin(a)],
                        [0,         1,        0],
                        [-sin(a),   0,      cos(a)]])
# Define the rotation matrices function in the Z direction
RotZ = lambda a: array([[cos(a),  -sin(a),    0],
                        [sin(a),   cos(a),    0],
                        [0,         0,        1]])

### Some helper functions --------------------------------------------------
# TODO: Is this needed?
# def call_func(self, **kwargs):
#     """ Transform an openmdao Component or Assembly into a function
#     my_var = obj(input1=.., input2=..).output
#     -- is equivalent to --
#     obj.input1=..
#     obj.input2=..
#     obj.run()
#     my_var = obj.output
#     """
#     for k,v in kwargs.iteritems():
#         if k in self.list_inputs():
#             setattr(self, k, v)
#     self.run()
#     return self
#
# Assembly.__call__ = call_func
# Component.__call__ = call_funck

def set_inputs(self, dic):
    """ Helping function to set the inputs of an assembly using a dictionary """
    for k, v in dic.iteritems():
        if k in self.list_inputs():
            setattr(self, k, v)

Assembly.set_inputs = set_inputs

def nnz(list):
    """ Emulate nnz function of Matlab """
    return len(nonzero(list)[0])


def find(nparray):
    """ Emulate find function of Matlab """
    return nonzero(nparray)[0]


class WTStreamwiseSorting(Component):
    """
    Order the wind turbine in the streamwise direction. Return an index list of the sorted wind turbines.
    """
    # Inputs
    wind_direction = Float(0.0, iotype='in', unit='degree')
    wt_positions = Array([], iotype='in', unit='m',
                         desc='The x,y position of the wind turbines in the wind farm array([n_wt,2])')

    # Outputs
    ordered_indices = List([], iotype='out',
        desc="the ordered list of indexes (int)")

    def execute(self):
        n_wt = self.wt_positions.shape[0]
        disti = zeros([n_wt, n_wt, 2])
        n_downstream = zeros([n_wt])
        for i in range(n_wt):
            for j in range(n_wt):
                disti[j] = wake_length_dist(self.wind_direction,
                                            self.wt_positions[
                                                j, 0], self.wt_positions[j, 1],
                                            self.wt_positions[i, 0], self.wt_positions[i, 1])
            # Number of downstream turbines
            n_downstream[i] = nnz(disti > 0)

        self.ordered_indices = argsort(n_downstream).tolist()


@implement_base(GenericHubWindSpeed)
class HubCenterWS(Component):
    """
    Provide the wind speed at the center of the hub. Only compatible with HubCenterWSPosition
    """
    ws_array = Array([], iotype='in', units='m/s',
        desc='an array of wind speed on the rotor')

    hub_wind_speed = Float(0.0, iotype='out', units='m/s',
        desc='hub wind speed')

    def execute(self):
        self.hub_wind_speed = self.ws_array[0]


@implement_base(GenericWSPosition)
class GaussWSPosition(Component):

    """
    Calculate numerically the gauss integration. The algorithm is based on
    [1].

    References:
      [1] Larsen GC. "A simple stationary semi-analytical wake model".
      [2] http://www.holoborodko.com/pavel/?page_id=679
      [3] http://en.wikipedia.org/wiki/Gaussian_quadrature
    """
    #GenericWSPosition
    wt_desc = VarTree(GenericWindTurbineVT(), iotype='in')
    ws_positions = Array([], iotype='out', units='m',
        desc='the position [n,3] of the ws_array')
    wt_xy = List([0.0, 0.0], iotype='in', units='m',
        desc='The x,y position of the wind turbine')

    #GaussWSPosition
    wind_direction = Float(270.0, iotype='in', unit='deg',
        desc='The wind direction oriented form the North [deg]')
    N = Int(5, min=4, max=6, iotype='in',
        desc='coefficient of gauss integration')
    te = Array([], iotype='out',
        desc='The theta angles')
    w = Array([], iotype='out',
        desc='The radiuses')

    def execute(self):
        N = self.N
        A = pi * self.wt_desc.rotor_diameter ** 2.0
        # turbine rotor area

        # Gauss interpolation coefficients (Eq.30)
        # Also in [2] and [3]
        #  N = 4:
        if N == 4:
            rt = [-0.339981043584856,
                  -0.861136311594053,
                  0.339981043584856,
                  0.861136311594053]
            w = [0.652145154862546,
                 0.347854845137454,
                 0.652145154862546,
                 0.347854845137454]
        elif N == 5:
            rt = [0,
                  0.5384693101056830910363144,
                  -0.5384693101056830910363144,
                  0.9061798459386639927976269,
                  -0.9061798459386639927976269]

            w = [0.5688888888888888888888889,
                 0.4786286704993664680412915,
                 0.4786286704993664680412915,
                 0.2369268850561890875142640,
                 0.2369268850561890875142640]
        elif N == 6:
            rt = [0.2386191860831969086305017,
                  -0.2386191860831969086305017,
                  0.6612093864662645136613996,
                  -0.6612093864662645136613996,
                  0.9324695142031520278123016,
                  -0.9324695142031520278123016]

            w = [0.4679139345726910473898703,
                 0.4679139345726910473898703,
                 0.3607615730481386075698335,
                 0.3607615730481386075698335,
                 0.1713244923791703450402961,
                 0.1713244923791703450402961]
        else:
            raise Exception('N is not a valid value', self.N)

        te = rt

        # res = 0;  # result output
        self.ws_positions = zeros([N * N, 3])
        inc = 0
        for j in range(N):
            for i in range(N):
                # (Eq.45)
                r = self.wt_desc.rotor_diameter/2.0 * (rt[i] + 1) / 2
                t = pi * (te[j] + 1)
                # Flow direction
                x = 0.0
                # Cross-flow direction
                y = r * cos(t+0.5*pi)
                # Vertical direction
                z = r * sin(t+0.5*pi)

                # Rotate in the Z direction to obtain the right positions
                wt_centered = dot(RotZ((-self.wind_direction + 270.0) * pi / 180.0), array([x, y, z]))
                self.ws_positions[inc,:] = wt_centered + array([self.wt_xy[0], self.wt_xy[1], self.wt_desc.hub_height])
                inc += 1
        self.te = te
        self.w = w


@implement_base(GenericHubWindSpeed)
class GaussHubWS(Component):

    """
    Calculate numerically the gauss integration. The algorithm is based on
    [1].

    References:
      [1] Larsen GC. "A simple stationary semi-analytical wake model".
      [2] http://www.holoborodko.com/pavel/?page_id=679
      [3] http://en.wikipedia.org/wiki/Gaussian_quadrature
    """

    #GenericHubWindSpeed
    ws_array = Array([], iotype='in', units='m/s',
        desc='an array of wind speed on the rotor')

    hub_wind_speed = Float(0.0, iotype='out', units='m/s',
        desc='hub wind speed')

    #GaussHubWS
    wt_desc = VarTree(GenericWindTurbineVT(), iotype='in')
    N = Int(5, min=4, max=6, iotype='in',
        desc='coefficient of gauss integration')
    # te = Array([], iotype='in',
        # desc='The theta angles')
    # w = Array([], iotype='in',
        # desc='The radiuses')

    def execute(self):
        R = self.wt_desc.rotor_diameter
        A = pi * R ** 2.0
        # turbine rotor area

        N = self.N

        if N == 4:
            rt = [-0.339981043584856,
                  -0.861136311594053,
                  0.339981043584856,
                  0.861136311594053]
            w = [0.652145154862546,
                 0.347854845137454,
                 0.652145154862546,
                 0.347854845137454]
        elif N == 5:
            rt = [0,
                  0.5384693101056830910363144,
                  -0.5384693101056830910363144,
                  0.9061798459386639927976269,
                  -0.9061798459386639927976269]

            w = [0.5688888888888888888888889,
                 0.4786286704993664680412915,
                 0.4786286704993664680412915,
                 0.2369268850561890875142640,
                 0.2369268850561890875142640]
        elif N == 6:
            rt = [0.2386191860831969086305017,
                  -0.2386191860831969086305017,
                  0.6612093864662645136613996,
                  -0.6612093864662645136613996,
                  0.9324695142031520278123016,
                  -0.9324695142031520278123016]

            w = [0.4679139345726910473898703,
                 0.4679139345726910473898703,
                 0.3607615730481386075698335,
                 0.3607615730481386075698335,
                 0.1713244923791703450402961,
                 0.1713244923791703450402961]
        else:
            raise Exception('N is not a valid value', self.N)

        # te = rt

        # rt = self.te
        # w = self.w

        # res = 0;  # result output
        res = zeros([N, N])
        inc = 0
        for j in range(N):
            for i in range(N):

                # (Eq.45)
                res[j, i] = w[j] * w[i] * (rt[i] + 1) * self.ws_array[inc]
                inc += 1

        res = (pi / 4.0) * (R ** 2.0 / A) * res
        self.hub_wind_speed = sum(sum(res))



@implement_base(GenericFlowModel, GenericWakeModel)
class GenericEngineeringWakeModel(GenericWakeModel):
    """
    A class that sets up the single wake frame.
    The specialized wake models have to specify the single_wake method.
    """
    #GenericWakeModel
    wt_desc = VarTree(GenericWindTurbineVT(), iotype='in',
        desc='the geometrical description of the current turbine')
    ws_positions = Array([], iotype='in',
        desc='the positions of the wind speeds in the global frame of reference [n,3] (x,y,z)')
    wt_xy = List([0.0, 0.0], iotype='in', units='m',
        desc='The x,y position of the current wind turbine')
    c_t = Float(0.0, iotype='in',
        desc='the thrust coefficient of the wind turbine')
    ws_array_inflow = Array([], iotype='in', units='m/s',
        desc='The inflow velocity at the ws_positions')
    wind_direction = Float(0.0, iotype='in', units='deg',
        desc='The inflow wind direction')

    ws_array = Array([], iotype='out',
        desc='an array of wind speed to find wind speed')
    du_array = Array([], iotype='out', units='m/s',
        desc='The deficit in m/s. Empty if only zeros')

    def execute(self):
        if abs(self.c_t) < 1E-8:
            # If the ct is too small, there isn't any wake
            self.ws_array = self.ws_array_inflow
            return

        self.ws_array = zeros(self.ws_array_inflow.shape)

        for i in range(self.ws_positions.shape[0]):
            cWTx = self.ws_positions[i, 0] - self.wt_xy[0]
            cWTy = self.ws_positions[i, 1] - self.wt_xy[1]
            ws = self.ws_array_inflow[i]
            X = wake_length_dist(self.wind_direction, 0.0, 0.0, cWTx, cWTy)
            rely = c2c_dist(self.wind_direction, 0.0, 0.0, cWTx, cWTy)
            relz = self.ws_positions[i, 2] - self.wt_desc.hub_height
            dr = sqrt(rely ** 2.0 + relz ** 2.0)
            self.ws_array[i] = ws * (1.0 + self.single_wake(X, dr, ws))

    def single_wake(self, X, dr, ws):
        """
        X : Stream wise wake distance
        dr: Cross wise wake distance
        ws: local inflow wind speed

        Output:
        Return the normalized axial velocity deficit
        """
        pass


@implement_base(GenericFlowModel)
class GenericInflowGenerator(GenericFlowModel):
    """
    Framework for an inflow model
    """
    #GenericFlowModel
    ws_positions = Array([], iotype='in',
        desc='the positions of the wind speeds in the global frame of reference [n,3] (x,y,z)')

    ws_array = Array([], iotype='out',
        desc='an array of wind speed to find wind speed')

    #GenericInflowGenerator
    wind_speed = Float(0.0, iotype='in',
        desc='the reference wind speed')


@implement_base(GenericInflowGenerator)
class HomogeneousInflowGenerator(GenericInflowGenerator):
    """
    Same wind speed at each positions
    """
    #GenericInflowGenerator
    wind_speed = Float(0.0, iotype='in', units='m/s',
        desc='the reference wind speed')
    ws_positions = Array([], iotype='in',
        desc='the positions of the wind speeds in the global frame of reference [n,3] (x,y,z)')

    ws_array = Array([], iotype='out',
        desc='an array of wind speed to find wind speed')

    def execute(self):
        # print "running HomogeneousInflowGenerator"
        self.ws_array = self.wind_speed * ones(self.ws_positions.shape[0])

@implement_base(GenericInflowGenerator)
class NeutralLogLawInflowGenerator(GenericInflowGenerator):
    """
    Create the inflow for a neutral log law input
    """
    #GenericInflowGenerator
    wind_speed = Float(0.0, iotype='in', units='m/s',
        desc='the reference wind speed')
    ws_positions = Array([], iotype='in',
        desc='the positions of the wind speeds in the global frame of reference [n,3] (x,y,z)')

    ws_array = Array([], iotype='out',
        desc='an array of wind speed to find wind speed')

    #NeutralLogLawInflowGenerator
    z_0 = Float(0.0, iotype='in',
        desc='the surface roughness')
    z_ref = Float(0.0, iotype='in',
        desc='the reference height')

    KAPPA = 0.4

    def execute(self):
        if self.z_0 == 0.0:
            raise Exception("z0 is null")
        if self.z_ref == 0.0:
            raise Exception("z_ref is null")
        self.u_star = self.wind_speed * self.KAPPA / log(self.z_ref / self.z_0)
        n = self.ws_positions.shape[0]
        self.ws_array = zeros([n])
        for i in range(n):
            zi = self.ws_positions[i, 2]
            self.ws_array[i] = self.u_star / self.KAPPA * log(zi / self.z_0)


class WakeReader(Component):
    """
    Read the recorder from the CaseIteratorDriver, and produce the list of wakes.
    It does the same as UpstreamWakeDriver.execute(). So it's redundant.
    """
    cases = Instance(ICaseIterator, iotype='in',
        desc='Iterator supplying evaluated Cases.')
    wakes = List([], iotype='out',
        desc='wake contributions to rotor wind speed [nwake][n]')
    wake_model = Str('wake_model', iotype='in',
        desc='the name of the wake model to read from')

    def execute(self):
        self.wakes = []
        for c in self.cases:
            ws_array = c[self.wake_model + '.ws_array']
            ws_array_inflow = c[self.wake_model + '.ws_array_inflow']
            if norm(ws_array_inflow - ws_array) > 1E-5:
                self.wakes.append(ws_array_inflow - ws_array)

class UpstreamWakeDriver(CaseIteratorDriver):
    """
    Loop through the upstream turbines and calculate the wake on the curent turbines.
    The cases are being built in the WakeDriver.
    In post_execute, the recorder is postprocessed to create a list of wakes.
    """
    wakes = List([], iotype='out',
        desc='wake contributions to rotor wind speed [nwake][n]')
    wake_model = Str('wake_model', iotype='in',
        desc='the name of the wake model to read from')

    def execute(self):
        super(UpstreamWakeDriver, self).execute()

        ### Prepare the wakes for the wake summation
        self.wakes = []
        for c in self.evaluated:
            ws_array = c[self.wake_model + '.ws_array']
            ws_array_inflow = c[self.wake_model + '.ws_array_inflow']
            if norm(ws_array_inflow - ws_array) > 1E-5:
                self.wakes.append(ws_array_inflow - ws_array)

class WakeDriver(Driver):
    """
    Loop over all the wind turbine in the direction of wt_indices.
    """
    wt_list = List([], iotype='in',
        desc='A list of wind turbine types')
    wt_positions = Array([], iotype='in', unit='m',
        desc='The x,y position of the wind turbines in the wind farm array([nWT,2])')
    wt_indices = List([], iotype='in',
        desc='A list of indices to loop throught')
    outputs = List([], iotype='in',
        desc='A list of outputs to save')

    # Registering the connections for the different types of information
    upstream_index_connections = List([], iotype='in',
        desc='A list of connections to implement for the upstream index')
    wt_connections = List([], iotype='in',
        desc='A list of connections to implement for the wts')
    index_connections = List([], iotype='in',
        desc='A list of connections to implement for the indices')
    xy_connections = List([], iotype='in',
        desc='A list of connections to implement the (x,y) positions of the turbines')
    recorded_connections = List([], iotype='in',
        desc='The list of connections to implement in the upstream driver')
    upstream_driver = Str('upstream_wake_driver.iterator', iotype='in',
        desc='Name of the upstream wake driver')

    evaluated = Instance(ICaseIterator, iotype='out',
        desc='Iterator supplying evaluated Cases.')
    wti = Int(0, iotype='out',
        desc='Current wind turbine investigated')

    def run_iteration(self):
        if self._nb_iterations < len(self.wt_indices):
            self.wti = self.wt_indices[self._nb_iterations]

            self._set_wt_connections()
            self._set_xy_connections()
            self._set_index_connections()
            self._set_upstream_inputs()

            self._nb_iterations += 1
            super(WakeDriver, self).run_iteration()

        else:
            self._continue = False

    def _set_wt_connections(self):
        """
        Copy around all the wt_desc
        """
        for wtc in self.wt_connections:
            self._set_inputs(wtc, self.wt_list[self.wti])

    def _set_xy_connections(self):
        """
        Copy around all the wind turbine positions
        """
        for xyc in self.xy_connections:
            self._set_inputs(xyc, [self.wt_positions[self.wti, 0], self.wt_positions[self.wti, 1]])

    def _set_index_connections(self):
        """
        Copy around all the wind turbine index (self.wti)
        """
        for indi in self.index_connections:
            self._set_inputs(indi, self.wti)

    def _set_upstream_inputs(self):
        """
        Setup the upstream wakes inputs
        """
        # We go through the previous cases, and create the upstream cases list
        upcases = []
        for precase in self.recorders[-1].cases:
            upcase = Case()
            for c1, c2 in self.recorded_connections:
                # Check if the connection is in the precase
                if c1 in precase:
                    upcase.add_input(c2, precase[c1])
                else:
                    raise Exception(c1+" have to be added to the wake_driver.printvars")
            upcases.append(upcase)
        self._set_inputs(self.upstream_driver, ListCaseIterator(upcases))

    def post_iteration(self):
        """
        After the iteration, indicates that it's over to the parent class
        """
        self.record_case()
        if self._nb_iterations >= len(self.wt_indices):
            self._continue = False
        else:
            self._continue = True

    def _set_inputs(self, targ, obj):
        """
        Set the target with the object. Travel through the hierarchy to set the inputs.
        """
        # Create the hierarchy
        hiera = targ.split('.')
        target = self.parent
        for i in range(len(hiera)-1):
            if hiera[i] in dir(target):
                target = getattr(target, hiera[i])
            else:
                raise Exception(hiera[i] + " is not in " + target.__class__.__name__)
        if hiera[-1] in dir(target):
            setattr(target, hiera[-1], obj)
        else:
            raise Exception(hiera[-1] + " is not in " + '.'.join(hiera[:-1]))

    def execute(self):
        self._nb_iterations = 0

        ### Stolen from the CaseIteratorDriver class ---
        self.evaluated = None
        self.recorders.append(ListCaseRecorder())
        try:
            super(WakeDriver, self).execute()
        finally:
            self.evaluated = self.recorders.pop().get_iterator()


class PostProcessWTCases(Component):
    """
    Postprocess the cases generated by WakeDriver.
    """
    cases = Instance(ICaseIterator, iotype='in',
        desc='The wind turbine cases')
    # wt_positions = Array([], unit='m', iotype='in')

    power = Float(iotype='out',
        desc='Total wind farm power production', unit='W')
    thrust = Float(iotype='out',
        desc='Total wind farm thrust', unit='N')
    wt_power = Array([], iotype='out',
        desc='The power production of each wind turbine', unit='W')
    wt_thrust = Array([], iotype='out',
        desc='The thrust of each wind turbine', unit='N')
    wt_hub_wind_speed = Array([], iotype='out',
        desc='The hub wind speed of each wind turbine', unit='m/s')

    def execute(self):
        indices = array([c['wt1.i'] for c in self.cases])
        sorter_indices = argsort(indices)
        indices.sort()
        # the indices sorted should exactly be equal to range(nWT)
        if norm(indices - arange(len(indices))) > 1E-5:
            raise Exception('Not all the cases have been computed')

        self.wt_power = array([self.cases[i]['wt_model.power'] for i in sorter_indices])
        self.wt_thrust = array([self.cases[i]['wt_model.thrust'] for i in sorter_indices])
        self.wt_hub_wind_speed = array([self.cases[i]['wt_model.hub_wind_speed'] for i in sorter_indices])

        self.power = sum(self.wt_power)
        self.thrust = sum(self.wt_thrust)

class WTID(Component):
    """
    Useless component used to keep track of which case was recorded.
    """
    i = Int(0, iotype='in')
    def execute(self):
        pass
        # print 'running WTID', self.name, self.i



@implement_base(GenericWindFarm)
class GenericWindFarmWake(GenericWindFarm):
    """
    TODO: write docstring
    """
    # GenericWindFarm
    # Inputs:
    wind_speed = Float(iotype='in', low=0.0, high=100.0, units='m/s',
        desc='Inflow wind speed at hub height')
    wind_direction = Float(iotype='in', low=0.0, high=360.0, units='deg',
        desc='Inflow wind direction at hub height')
    wt_layout = VarTree(GenericWindFarmTurbineLayout(), iotype='in',
        desc='wind turbine properties and layout')

    # Outputs:
    power = Float(iotype='out', units='kW',
        desc='Total wind farm power production')
    thrust = Float(iotype='out', units='N',
        desc='Total wind farm thrust')
    wt_power = Array([], iotype='out',
        desc='The power production of each wind turbine')
    wt_thrust = Array([], iotype='out',
        desc='The thrust of each wind turbine')

    # Slots
    ws_positions = InterfaceSlot(GenericWSPosition,
        desc='The wind speed positions calculator for the wind farm wake workflow')
    wake_dist = InterfaceSlot(WTStreamwiseSorting)
    wake_model = InterfaceSlot(GenericWakeModel)
    wt_model = InterfaceSlot(GenericWindTurbine)
    wake_sum = InterfaceSlot(GenericWakeSum)
    wake_driver = InterfaceSlot(WakeDriver)
    upstream_wake_driver = InterfaceSlot(CaseIteratorDriver)
    hub_wind_speed = InterfaceSlot(GenericHubWindSpeed,
        desc='The hub wind speed calculator for the wind farm wake workflow')
    inflow_gen = InterfaceSlot(GenericInflowGenerator)
    # wake_reader = Slot(WakeReader)

    def configure(self):
        super(GenericWindFarmWake, self).configure()
        # Add the components
        self.add('ws_positions', GenericWSPosition())
        self.add('inflow_gen', GenericInflowGenerator())
        self.add('wake_dist', WTStreamwiseSorting())
        self.add('wt_model', GenericWindTurbine())
        self.add('wake_sum', GenericWakeSum())
        self.add('hub_wind_speed', GenericHubWindSpeed())
        self.add('wake_model', GenericWakeModel())

class WindFarmWake(GenericWindFarmWake):
    """
    TODO: write docstring
    """

    def configure(self):
        super(WindFarmWake, self).configure()
        self.add('wt1', WTID())
        self.add('wt2', WTID())
        self.add('wake_driver', WakeDriver())
        self.add('upstream_wake_driver', UpstreamWakeDriver())
        self.add('postprocess_wt_cases', PostProcessWTCases())
        # Add the components
        # self.add('wake_reader', WakeReader())

        # Activate parallelization:
        # self.upstream_wake_driver.sequential = False

        # Add and configure the drivers
        self.driver.workflow.add(['wake_dist', 'wake_driver', 'postprocess_wt_cases'])
        # self.wake_driver.workflow.add(['wt1', 'ws_positions', 'inflow_gen', 'upstream_wake_driver',
        #                                      'wake_reader', 'wake_sum', 'hub_wind_speed', 'wt_model'])
        self.wake_driver.workflow.add(['wt1', 'ws_positions', 'inflow_gen', 'upstream_wake_driver', 'wake_sum', 'hub_wind_speed', 'wt_model'])
        self.upstream_wake_driver.workflow.add(['wt2', 'wake_model'])

        # Wire the components
        self.connect('wake_dist.ordered_indices', 'wake_driver.wt_indices')
        self.connect('ws_positions.ws_positions', ['inflow_gen.ws_positions', 'wake_model.ws_positions'])
        self.connect('inflow_gen.ws_array', ['wake_sum.ws_array_inflow', 'wake_model.ws_array_inflow'])
        self.connect('wake_sum.ws_array', ['hub_wind_speed.ws_array'])
        self.connect('hub_wind_speed.hub_wind_speed', 'wt_model.hub_wind_speed')
        self.wake_driver.recorded_connections = [('wt_model.c_t', 'wake_model.c_t'),
                                                 ('ws_positions.wt_desc', 'wake_model.wt_desc'),
                                                 ('ws_positions.wt_xy', 'wake_model.wt_xy'),
                                                 ('wt1.i', 'wt2.i')]

        self.connect('wake_driver.evaluated', 'postprocess_wt_cases.cases')
        # self.connect('upstream_wake_driver.evaluated', 'wake_reader.cases')
        # self.connect('wake_reader.wakes', 'wake_sum.wakes')
        self.connect('upstream_wake_driver.wakes', 'wake_sum.wakes')

        # Prepare the wake case drivers
        self.wake_driver.wt_connections = ['ws_positions.wt_desc', 'wt_model.wt_desc']
        self.wake_driver.xy_connections = ['ws_positions.wt_xy']
        self.wake_driver.index_connections = ['wt1.i']

        # Indicates the outputs to record in the ListCaseRecorder. Some will be used to feed in the upstream_wake_driver
        # and some will be used to calculate the AEP after everything is finished.
        self.wake_driver.printvars = ['wake_dist.wind_direction',
                                      'inflow_gen.wind_speed',
                                      'wt_model.power',
                                      'wt_model.hub_wind_speed',
                                      'wt_model.thrust',
                                      'wt_model.c_t',
                                      'wt1.i',
                                      'ws_positions.wt_xy',
                                      'ws_positions.wt_desc',
                                      'wake_driver.wti']
        self.upstream_wake_driver.printvars = ['wt2.i', 'wake_model.ws_array', 'wake_model.ws_array_inflow', 'wake_model.ws_positions']


        # def configure_single_inflow(self):
        #     """
        #     Configure the assembly for single inflow
        #     """
        self.connect('wt_layout.wt_list', ['wake_driver.wt_list'])
        self.connect('wind_speed', 'inflow_gen.wind_speed')
        self.connect('wind_direction', ['wake_dist.wind_direction', 'wake_model.wind_direction'])
        self.connect('wt_layout.wt_positions', ['wake_dist.wt_positions', 'wake_driver.wt_positions'])
        self.connect('postprocess_wt_cases.wt_power', 'wt_power')
        self.connect('postprocess_wt_cases.wt_thrust', 'wt_thrust')
        self.connect('postprocess_wt_cases.power', 'power')
        self.connect('postprocess_wt_cases.thrust', 'thrust')

    def configure_single_turbine_type(self):
        """
        There is only one type of wind turbine, so no need to copy arround the wt_desc. Just connect it.
        Should be called after self.configure and self.configure_single_inflow.
        """
        ### Removing the existing connections
        self.wake_driver.wt_connections = []
        for i, con in enumerate(self.wake_driver.recorded_connections):
            if 'wt_desc' in con[0]:
                self.wake_driver.recorded_connections.remove(con)

        for i, var in enumerate(self.wake_driver.printvars):
            if 'wt_desc' in var:
                self.wake_driver.printvars.remove(var)

        ### Adding the new connections
        self.connect('wt_layout.wt_list[0]', ['ws_positions.wt_desc', 'wt_model.wt_desc', 'wake_model.wt_desc'])




class FasterWindFarmWake(Component):
    """
    This component does the same thing as WindFarmWake, but without using the
    assembly driver and connection in order to speeds things up.
    """
    # Inputs:
    wind_speed = Float(iotype='in', desc='Inflow wind speed at hub height')
    wind_direction = Float(iotype='in', desc='Inflow wind direction at hub height', my_metadata='hello')
    wt_positions = Array(iotype='in', desc='')

    #wt_layout = VarTree(GenericWindFarmTurbineLayout(), iotype='in', desc='wind turbine properties and layout')

    # Outputs:
    wt_desc = VarTree(GenericWindTurbineVT(), iotype='in')
    power = Float(iotype='out', desc='Total wind farm power production', unit='W')
    thrust = Float(iotype='out', desc='Total wind farm thrust', unit='N')
    wt_power = Array([], iotype='out', desc='The power production of each wind turbine')
    wt_thrust = Array([], iotype='out', desc='The thrust of each wind turbine')
    wt_c_t = Array([], iotype='out', desc='The thrust coefficient of each wind turbine')

    # Slots:
    ws_positions = InterfaceSlot(GenericWSPosition, desc='The wind speed positions calculator for the wind farm wake workflow')
    wake_dist = InterfaceSlot(WTStreamwiseSorting)
    wake_model = InterfaceSlot(GenericWakeModel)
    wt_model = InterfaceSlot(GenericWindTurbine)
    wake_sum = InterfaceSlot(GenericWakeSum)
    wake_driver = InterfaceSlot(WakeDriver)
    upstream_wake_driver = InterfaceSlot(CaseIteratorDriver)
    hub_wind_speed = InterfaceSlot(GenericHubWindSpeed, desc='The hub wind speed calculator for the wind farm wake workflow')
    inflow_gen = InterfaceSlot(GenericInflowGenerator)
    # wake_reader = Slot(WakeReader)

    def __init__(self):
        super(FasterWindFarmWake, self).__init__()
        self._configure()

    def _configure(self):
        self.ws_positions = GenericWSPosition()
        self.inflow_gen = GenericInflowGenerator()
        self.wake_dist = WTStreamwiseSorting()
        self.wt_model = GenericWindTurbine()
        self.wake_sum = GenericWakeSum()
        self.hub_wind_speed = GenericHubWindSpeed()
        self.wake_model = GenericWakeModel()

    def execute(self):
        """Here we don't use any Driver, or connection, everything is done manually,
        to avoid the OpenMDAO overhead
        """
        n_wt = self.wt_positions.shape[0]
        self.wt_c_t = zeros([n_wt])
        self.wt_power = zeros([n_wt])

        self._run_wake_dist()
        for i, i_wt in enumerate(self.wake_dist.ordered_indices):
            self._run_ws_positions(i_wt)
            self._run_inflow_gen(i_wt)
            self._run_upstream_wake_driver(i, i_wt)
            self._run_wake_sum(i_wt)
            self._run_hub_wind_speed(i_wt)
            self._run_wt_model(i_wt)

        self.power = sum(self.wt_power)
        self.thrust = sum(self.wt_thrust)


    def _run_wake_dist(self):
        self.wake_dist.wind_direction = self.wind_direction
        self.wake_dist.wt_positions = self.wt_positions
        self.wake_dist.run()

    def _run_ws_positions(self, i_wt):
        self.ws_positions.wt_xy = self.wt_positions[i_wt,:].tolist()
        self.ws_positions.wt_desc = self.wt_desc
        self.ws_positions.run()

    def _run_inflow_gen(self, i_wt):
        self.inflow_gen.wind_speed = self.wind_speed
        self.inflow_gen.ws_positions = self.ws_positions.ws_positions
        self.inflow_gen.run()

    def _run_upstream_wake_driver(self, i, i_wt):
        self._upstream_wakes = []
        for j, j_wt in enumerate(self.wake_dist.ordered_indices[:i]):
            self._run_wake_model(i_wt, j_wt)
            if norm(self.wake_model.ws_array_inflow - self.wake_model.ws_array) > 1E-5:
               self._upstream_wakes.append(self.wake_model.ws_array_inflow - self.wake_model.ws_array)

    def _run_wake_model(self, i_wt, j_wt):
        self.wake_model.wind_direction = self.wind_direction
        self.wake_model.wt_desc = self.wt_desc
        self.wake_model.ws_array_inflow = self.inflow_gen.ws_array
        self.wake_model.ws_positions = self.ws_positions.ws_positions
        self.wake_model.c_t = self.wt_c_t[j_wt]
        self.wake_model.wt_xy = self.wt_positions[j_wt,:].tolist()
        self.wake_model.run()

    def _run_wake_sum(self, i_wt):
        self.wake_sum.ws_array_inflow = self.inflow_gen.ws_array
        self.wake_sum.wakes = self._upstream_wakes
        self.wake_sum.run()

    def _run_hub_wind_speed(self, i_wt):
        self.hub_wind_speed.ws_array = self.wake_sum.ws_array
        self.hub_wind_speed.run()

    def _run_wt_model(self, i_wt):
        self.wt_model.wt_desc = self.wt_desc
        self.wt_model.hub_wind_speed = self.hub_wind_speed.hub_wind_speed
        self.wt_model.run()
        self.wt_c_t[i_wt] = self.wt_model.c_t
        self.wt_power[i_wt] = self.wt_model.power



# # Moved up to plant_flow
#
# class PostProcessWindRose(Component):
#     cases = Instance(ICaseIterator, iotype='in')
#     aep = Float(0.0, iotype='out',
#         desc='Annual Energy Production', unit='kWh')
#     energies = Array([], iotype='out',
#         desc='The energy production per sector', unit='kWh')
#
#     power_str = Str('wf.power', iotype='in')
#     frequencies_str = Str('P', iotype='in')
#
#     def execute(self):
#         self.energies = [c[self.frequencies_str] * c[self.power_str] * 24 * 365 for c in self.cases]
#         self.aep = sum(self.energies)
#
#
#
# class GenericAEP(Assembly):
#     """ Generic assembly to compute the Annual Energy Production of a wind farm """
#     # Inputs
#     wind_speeds = Array([], iotype='in',
#         desc='The different wind speeds to run [nWS]', unit='m/s')
#     wind_directions = Array([], iotype='in',
#         desc='The different wind directions to run [nWD]', unit='deg')
#     wind_rose = Array([], iotype='in',
#         desc='Probability distribution of wind speed, wind direction [nWS, nWD]')
#
#     # In case there is a list of wind turbines
#     wt_list = List([], iotype='in',
#         desc='A list of wind turbine types')
#     wt_positions = Array([], iotype='in', unit='m',
#         desc='The x,y position of the wind turbines in the wind farm array([n_wt,2])')
#
#     # Outputs
#     aep = Float(0.0, iotype='out',
#         desc='Annual Energy Production', unit='kWh')
#     energies = Array([], iotype='out',
#         desc='The energy production per sector', unit='kWh')
#
#     # In case there is a list of wind turbines
#     wt_aep = Array([], iotype='out',
#         desc='Annual Energy Production per each turbine', unit='kWh')
#     wt_energies = Array([], iotype='out',
#         desc='The energy production per sector per turbine', unit='kWh')
#
#
#
# class AEP(GenericAEP):
#     wf = Slot(GenericWindFarm,
#         desc='A wind farm assembly or component')
#     P = Float(0.0, iotype='in',
#         desc='Place holder for the probability')
#
#     def configure(self):
#         super(AEP, self).configure()
#         self.add('wf', GenericWindFarm())
#         self.wf.configure()
#         self.add('wind_rose_driver', CaseIteratorDriver())
#         self.add('postprocess_wind_rose', PostProcessWindRose())
#         self.wind_rose_driver.workflow.add('wf')
#         self.wind_rose_driver.printvars = ['wf.power', 'wf.wt_power', 'wf.wt_thrust']
#         self.driver.workflow.add(['wind_rose_driver', 'postprocess_wind_rose'])
#         self.connect('wind_rose_driver.evaluated', 'postprocess_wind_rose.cases')
#         self.connect('postprocess_wind_rose.aep', 'aep')
#         self.connect('postprocess_wind_rose.energies', 'energies')
#         self.connect('wt_list', 'wf.wt_list')
#         self.connect('wt_positions', 'wf.wt_positions')
#
#     def generate_cases(self):
#         cases = []
#         for i, ws in enumerate(self.wind_speeds):
#             for j, wd in enumerate(self.wind_directions):
#                 cases.append(Case(inputs=[('wf.wind_direction', wd), ('wf.wind_speed', ws), ('P', self.wind_rose[i, j])]))
#         return cases
#
#
#     def _pre_execute(self, force=True):
#         self.wind_rose_driver.iterator = ListCaseIterator(self.generate_cases())
#         super(AEP, self)._pre_execute()




def wake_length_dist(WD, uWTx, uWTy, cWTx, cWTy):
    """
    Calculation of the wake length and center to center distance
       X = WakeLengthDist(upstream turbine, current turbine), positif when
       upwind WT (uWT) is upstream of current WT (cWT).
       It's the stream-wise distance between the two turbines

       Inputs:
       WD: wind direction in [deg]
       uWTx: upstream Wind Turbine x position
       uWTy: upstream Wind Turbine y position
       cWTx: current Wind Turbine x position
       cWTy: current Wind Turbine y position

       output:
       wake_length_dist
    """
    return sin(WD * pi / 180.0) * (uWTx - cWTx) \
        + cos(WD * pi / 180.0) * (uWTy - cWTy)


def c2c_dist(WD, uWTx, uWTy, cWTx, cWTy):
    """
    Y = CtoCDist(upstream turbine, current turbine): Center to center
    distance
    It's the cross-wise distance between the two turbines

       Inputs:
       uWTx: upstream Wind Turbine x position
       uWTy: upstream Wind Turbine y position
       cWTx: current Wind Turbine x position
       cWTy: current Wind Turbine y position

       output:
       c2c_dist
    """
    return cos(WD * pi / 180.0) * (uWTx - cWTx) \
        - sin(WD * pi / 180.0) * (uWTy - cWTy)





if __name__ == '__main__':
    pass
