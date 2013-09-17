#__all__ = ['fused_wake']

from numpy import array, log, zeros, cos, sin, nonzero, argsort, ones, arange, pi, sqrt
from numpy.linalg.linalg import norm
from openmdao.lib.datatypes.api import VarTree, Float, Slot, Array, List, Int, Str
from openmdao.lib.drivers.api import CaseIteratorDriver
from openmdao.main.api import Driver, Run_Once
from openmdao.main.api import Component, Assembly
from openmdao.lib.casehandlers.api import ListCaseRecorder, ListCaseIterator
from openmdao.main.interfaces import ICaseIterator
from openmdao.main.case import Case

#from fused_wake.io import GenericWindTurbineVT, GenericWindTurbine
from io import GenericWindTurbineVT, GenericWindTurbine

# Wake Model stuffs ######################################################

# Define the rotaiton matrices function in the X direction
RotX = lambda a: array([[1,         0,        0],
                        [0,       cos(a),   -sin(a)],
                        [0,       sin(a),   cos(a)]])
# Define the rotaiton matrices function in the Y direction
RotY = lambda a: array([[cos(a),    0,      sin(a)],
                        [0,         1,        0],
                        [-sin(a),   0,      cos(a)]])
# Define the rotaiton matrices function in the Z direction
RotZ = lambda a: array([[cos(a),  -sin(a),    0],
                        [sin(a),   cos(a),    0],
                        [0,         0,        1]])


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
    ordered_indices = List([], iotype='out', desc="the ordered list of indexes (int)")

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


class GenericWSPosition(Component):
    """Calculate the position of the ws_array"""
    wt_desc = VarTree(GenericWindTurbineVT(), iotype='in')
    ws_positions = Array([], iotype='out', desc='the position [n,3] of the ws_array', unit='m')
    wt_xy = List([0.0, 0.0], iotype='in', desc='The x,y position of the wind turbine', unit='m')


class HubCenterWSPosition(GenericWSPosition):
    """
    Generate the positions at the center of the wind turbine rotor
    """
    def execute(self):
        self.ws_positions = array([[self.wt_xy[0], self.wt_xy[1], self.wt_desc.hub_height]])


class GenericWakeSum(Component):
    """
    Generic class for calculating the wake accumulation
    """
    wakes = List([], iotype='in', desc='wake contributions to rotor wind speed [nwake][n]')
    ws_array_inflow = Array([], iotype='in', desc='inflow contributions to rotor wind speed [n]', unit='m/s')

    ws_array = Array([], iotype='out', desc='the rotor wind speed [n]', unit='m/s')


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


class GenericHubWindSpeed(Component):
    """
    Generic class for calculating the wind turbine hub wind speed. 
    Typically used as an input to a wind turbine power curve / thrust coefficient curve.
    """
    ws_array = Array([], iotype='in', desc='an array of wind speed on the rotor', unit='m/s')

    hub_wind_speed = Float(0.0, iotype='out', desc='hub wind speed', unit='m/s')


class HubCenterWS(GenericHubWindSpeed):
    """
    Provide the wind speed at the center of the hub. Only compatible with HubCenterWSPosition
    """

    def execute(self):
        self.hub_wind_speed = self.ws_array[0]


class GenericFlowModel(Component):
    """
    Framework for a flow model
    """
    ws_positions = Array([], iotype='in', desc='the positions of the wind speeds in the global frame of reference [n,3] (x,y,z)')
    ws_array = Array([], iotype='out', desc='an array of wind speed to find wind speed')


class GenericWakeModel(GenericFlowModel):

    """
    Framework for a wake model
    """
    wt_desc = VarTree(GenericWindTurbineVT(), iotype='in', desc='the geometrical description of the current turbine')
    wt_xy = List([0.0, 0.0], iotype='in', desc='The x,y position of the current wind turbine', unit='m')
    c_t = Float(0.0, iotype='in', desc='the thrust coefficient of the wind turbine')
    ws_array_inflow = Array([], iotype='in', desc='The inflow velocity at the ws_positions', unit='m/s')
    wind_direction = Float(0.0, iotype='in', desc='The inflow wind direction', unit='deg')
    du_array = Array([], iotype='out', desc='The deficit in m/s. Empty if only zeros', unit='m/s')

    def post_execute(self):
        """
        In the case where we are only interested in deficits, there isn't any advantage 
        of copying arrays of 0. So let's post process those out.
        """
        self.du_array = self.ws_array - self.ws_array_inflow
        if norm(self.du_array) < 1E-5:
            self.du_array = []


class GenericEngineeringWakeModel(GenericWakeModel):
    """
    A class that sets up the single wake frame. 
    The specialized wake models have to specify the single_wake method.
    """
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
            self.ws_array[i] = ws + self.single_wake(X, dr, ws)

    def single_wake(self, X, dr, ws):
        """
        X : Stream wise wake distance
        dr: Cross wise wake distance
        ws: local inflow wind speed

        Output:
        Return the axial velocity deficit
        """
        pass


class GenericInflowGenerator(GenericFlowModel):
    """
    Framework for an inflow model
    """
    wind_speed = Float(0.0, iotype='in', desc='the reference wind speed')


class HomogeneousInflowGenerator(GenericInflowGenerator):
    """
    Same wind speed at each positions
    """
    def execute(self):
        # print "running HomogeneousInflowGenerator"
        self.ws_array = self.wind_speed * ones(self.ws_positions.shape[0])


class NeutralLogLawInflowGenerator(GenericInflowGenerator):
    """
    Create the inflow for a neutral log law input
    """
    z_0 = Float(0.0, iotype='in', desc='the surface roughness')
    z_ref = Float(0.0, iotype='in', desc='the reference height')

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
    cases = Slot(ICaseIterator, iotype='in', desc='Iterator supplying evaluated Cases.')
    wakes = List([], iotype='out', desc='wake contributions to rotor wind speed [nwake][n]')
    wake_model = Str('wake_model', iotype='in', desc='the name of the wake model to read from')

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
    wakes = List([], iotype='out', desc='wake contributions to rotor wind speed [nwake][n]')
    wake_model = Str('wake_model', iotype='in', desc='the name of the wake model to read from')

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
    wt_list = List([], iotype='in', desc='A list of wind turbine types')
    wt_positions = Array([], iotype='in', unit='m', desc='The x,y position of the wind turbines in the wind farm array([nWT,2])')
    wt_indices = List([], iotype='in', desc='A list of indices to loop throught')
    outputs = List([], iotype='in', desc='A list of outputs to save')

    # Registering the connections for the different types of information
    upstream_index_connections = List([], iotype='in', desc='A list of connections to implement for the upstream index')
    wt_connections = List([], iotype='in', desc='A list of connections to implement for the wts')
    index_connections = List([], iotype='in', desc='A list of connections to implement for the indices')
    xy_connections = List([], iotype='in', desc='A list of connections to implement the (x,y) positions of the turbines')
    recorded_connections = List([], iotype='in', desc='The list of connections to implement in the upstream driver')
    upstream_driver = Str('upstream_wake_driver.iterator', iotype='in', desc='Name of the upstream wake driver')

    evaluated = Slot(ICaseIterator, iotype='out', desc='Iterator supplying evaluated Cases.')
    wti = Int(0, iotype='out', desc='Current wind turbine investigated')

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
    cases = Slot(ICaseIterator, iotype='in', desc='The wind turbine cases')
    # wt_positions = Array([], unit='m', iotype='in')

    power = Float(iotype='out', desc='Total wind farm power production', unit='W')
    thrust = Float(iotype='out', desc='Total wind farm thrust', unit='N')
    wt_power = Array([], iotype='out', desc='The power production of each wind turbine', unit='W')
    wt_thrust = Array([], iotype='out', desc='The thrust of each wind turbine', unit='N')
    wt_hub_wind_speed = Array([], iotype='out', desc='The hub wind speed of each wind turbine', unit='m/s')

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



class GenericWindFarm(Assembly):
    # Inputs:
    wind_speed = Float(0.0, iotype='in', desc='Inflow wind speed at hub height')
    wind_direction = Float(0.0, iotype='in', desc='Inflow wind direction at hub height', my_metadata='hello')
    wt_list = List([], iotype='in', desc='The wind turbine list of descriptions')
    wt_positions = Array([], unit='m', iotype='in')

    # Outputs:
    power = Float(0.0, iotype='out', desc='Total wind farm power production', unit='W')
    thrust = Float(0.0, iotype='out', desc='Total wind farm thrust', unit='N')
    wt_power = Array([], iotype='out', desc='The power production of each wind turbine')
    wt_thrust = Array([], iotype='out', desc='The thrust of each wind turbine')

    def execute(self):
        # print "Running %s with ws:%f and wd:%f "%(self.__class__.__name__, self.wind_speed, self.wind_direction)
        super(GenericWindFarm, self).execute()
        # time.sleep(2)

class GenericWindFarmWake(GenericWindFarm):
    """
    TODO: write docstring
    """
    ws_positions = Slot(GenericWSPosition, desc='The wind speed positions calculator for the wind farm wake workflow')
    wake_dist = Slot(WTStreamwiseSorting)
    wake_model = Slot(GenericWakeModel)
    wt_model = Slot(GenericWindTurbine)
    wake_sum = Slot(GenericWakeSum)
    wake_driver = Slot(WakeDriver)
    upstream_wake_driver = Slot(CaseIteratorDriver)
    hub_wind_speed = Slot(GenericHubWindSpeed, desc='The hub wind speed calculator for the wind farm wake workflow')
    inflow_gen = Slot(GenericInflowGenerator)
    # wake_reader = Slot(WakeReader)

    def configure(self):
        super(GenericWindFarmWake, self).configure()
        # Add the components
        self.add('wt1', WTID())
        self.add('wt2', WTID())
        self.add('ws_positions', GenericWSPosition())
        self.add('inflow_gen', GenericInflowGenerator())
        self.add('wake_dist', WTStreamwiseSorting())
        self.add('wt_model', GenericWindTurbine())
        self.add('wake_sum', GenericWakeSum())
        self.add('hub_wind_speed', GenericHubWindSpeed())
        self.add('wake_model', GenericWakeModel())
        self.add('wake_driver', WakeDriver())
        self.add('upstream_wake_driver', UpstreamWakeDriver())
        self.add('postprocess_wt_cases', PostProcessWTCases())
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
        self.connect('wt_list', ['wake_driver.wt_list'])
        self.connect('wind_speed', 'inflow_gen.wind_speed')
        self.connect('wind_direction', ['wake_dist.wind_direction', 'wake_model.wind_direction'])
        self.connect('wt_positions', ['wake_dist.wt_positions', 'wake_driver.wt_positions'])
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
        self.connect('wt_list[0]', ['ws_positions.wt_desc', 'wt_model.wt_desc', 'wake_model.wt_desc'])


class PostProcessWindRose(Component):
    cases = Slot(ICaseIterator, iotype='in')
    aep = Float(0.0, iotype='out', desc='Annual Energy Production', unit='kWh')
    energies = Array([], iotype='out', desc='The energy production per sector', unit='kWh')

    def execute(self):
        self.energies = [c['P'] * c['wf.power'] * 24 * 365 for c in self.cases]
        self.aep = sum(self.energies)

class GenericAEP(Assembly):
    """ Generic assembly to compute the Annual Energy Production of a wind farm """
    # Inputs
    wind_speeds = Array([], iotype='in', desc='The different wind speeds to run [nWS]', unit='m/s')
    wind_directions = Array([], iotype='in', desc='The different wind directions to run [nWD]', unit='deg')
    wind_rose = Array([], iotype='in', desc='Probability distribution of wind speed, wind direction [nWS, nWD]')
    
    # In case there is a list of wind turbines
    wt_list = List([], iotype='in', desc='A list of wind turbine types')
    wt_positions = Array([], iotype='in', unit='m', desc='The x,y position of the wind turbines in the wind farm array([n_wt,2])')
    
    # Outputs
    aep = Float(0.0, iotype='out', desc='Annual Energy Production', unit='kWh')
    energies = Array([], iotype='out', desc='The energy production per sector', unit='kWh')

    # In case there is a list of wind turbines
    wt_aep = Array([], iotype='out', desc='Annual Energy Production per each turbine', unit='kWh')
    wt_energies = Array([], iotype='out', desc='The energy production per sector per turbine', unit='kWh')

class AEP(GenericAEP):
    wf = Slot(GenericWindFarm, desc='A wind farm assembly or component')
    P = Float(0.0, iotype='in', desc='Place holder for the probability')

    def configure(self):
        super(AEP, self).configure()
        self.add('wf', GenericWindFarm())
        self.wf.configure()
        self.add('driver', Run_Once())
        self.add('wind_rose_driver', CaseIteratorDriver())
        self.add('postprocess_wind_rose', PostProcessWindRose())
        self.wind_rose_driver.workflow.add('wf')
        self.wind_rose_driver.printvars = ['wf.power', 'wf.wt_power', 'wf.wt_thrust']
        self.driver.workflow.add(['wind_rose_driver', 'postprocess_wind_rose'])
        self.connect('wind_rose_driver.evaluated', 'postprocess_wind_rose.cases')
        self.connect('postprocess_wind_rose.aep', 'aep')
        self.connect('postprocess_wind_rose.energies', 'energies')
        self.connect('wt_list', 'wf.wt_list')
        self.connect('wt_positions', 'wf.wt_positions')

    def generate_cases(self):
        cases = []
        for i, ws in enumerate(self.wind_speeds):
            for j, wd in enumerate(self.wind_directions):
                cases.append(Case(inputs=[('wf.wind_direction', wd), ('wf.wind_speed', ws), ('P', self.wind_rose[i, j])]))
        return cases


    def _pre_execute(self, force=True):
        self.wind_rose_driver.iterator = ListCaseIterator(self.generate_cases())
        super(AEP, self)._pre_execute()
         



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
