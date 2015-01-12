from openmdao.main.datatypes.api import List, Array, Float, Int, Enum
from openmdao.main.api import Component, Assembly

from dakota import DakotaInput, run_dakota
from dakota_driver.driver import DakotaBase

# for testing
class Rosenbrock(Component):
    """ Standard two-dimensional Rosenbrock function. """

    x = Array([0., 0.],iotype='in')
    f = Float(iotype='out')

    def execute(self):
        """ Just evaluate the function. """
        x1 = self.x[0]
        x2 = self.x[1]
        self.f = 100 * (x2 - x1**2)**2 + (1 - x1)**2


class DakotaParamStudy(DakotaBase):
    """ Multidimensional parameter study using DAKOTA. """

    partitions = List(Int, low=1, iotype='in',
                      desc='List giving # of partitions for each parameter')

    def setup_cases(self,studycases, aerocode):
        # for now, only special type of cases: 1 case, and it has to be all just enumeration vars
        if (len(studycases) != 1):
            print "sorry, only 1 case allowed for now"

        dlc = studycases[0]
        parser = dlc.parser
        bounds = parser.get_bounds()
        self.partitions = parser.get_partitions()        

        ## sort of hacks to save this info
        aerocode.param_names = parser.get_names()
        aerocode.dlc = dlc
        # and to size x at runtime:
        aerocode.create_x(len(aerocode.param_names))
        ##
        
        ## Now we can add params and objective official to openmdao, for it to manage them.
        # note runner.x and runner.f must exist in your aero assembly.
        self.add_parameter('runner.x', low=bounds[0], high=bounds[1])
        self.add_objective('runner.f')

    def configure_input(self):
        """ Configures input specification. """
        if len(self.partitions) != self.total_parameters():
            self.raise_exception('#partitions (%s) != #parameters (%s)'
                                 % (len(self.partitions), self.total_parameters()),
                                 ValueError)

        partitions = [str(partition) for partition in self.partitions]
        objectives = self.get_objectives()

        self.input.method = [
            'multidim_parameter_study',
            '    output = %s' % self.output,
            '    partitions = %s' % ' '.join(partitions)]

        self.set_variables(need_start=False)

        self.input.responses = [
            'response_functions = %s' % len(objectives),
            'no_gradients',
            'no_hessians']


class DakotaSamplingStudy(DakotaBase):
    """ Multidimensional parameter study using DAKOTA. """

    sample_type = Enum('lhs', iotype='in', values=('random', 'lhs'),
                       desc='Type of sampling')
    seed = Int(52983, iotype='in', desc='Seed for random number generator')
    samples = Int(100, iotype='in', low=1, desc='# of samples to evaluate')


    def setup_cases(self,studycases, aerocode):
        # for now, only special type of cases: 1 case, and it has to be all just enumeration vars
        if (len(studycases) != 1):
            print "sorry, only 1 case allowed for now"

        dlc = studycases[0]
        parser = dlc.parser
        bounds = parser.get_bounds()
        self.partitions = parser.get_partitions()        

        ## sort of hacks to save this info
        aerocode.param_names = parser.get_names()
        aerocode.dlc = dlc
        # and to size x at runtime:
        aerocode.create_x(len(aerocode.param_names))
        ##
        ## Now we can add params and objective official to openmdao, for it to manage them.
        # note runner.x and runner.f must exist in your aero assembly.
        self.add_parameter('runner.x', low=bounds[0], high=bounds[1])
        self.add_objective('runner.f')

    def configure_input(self):
        """ Configures input specification. """
        objectives = self.get_objectives()

        self.input.method = [
            'sampling',
            '    output = %s' % self.output,
            '    sample_type = %s' % self.sample_type,
            '    seed = %s' % self.seed,
            '    samples = %s' % self.samples]

        self.set_variables(need_start=False, uniform=True)

        names = ['%r' % name for name in objectives.keys()]
        self.input.responses = [
            'num_response_functions = %s' % len(objectives),
            'response_descriptors = %s' % ' '.join(names),
            'no_gradients',
            'no_hessians']


    def set_variables(self, need_start, uniform=False):
        """ Set :class:`DakotaInput` ``variables`` section. """
        parameters = self.get_parameters()

        print "setting variables"
        lbounds = [str(val) for val in self.get_lower_bounds(dtype=None)]
        ubounds = [str(val) for val in self.get_upper_bounds(dtype=None)]
        names = []
        for param in parameters.values():
            for name in param.names:
                names.append('%r' % name)

        if uniform:
            self.input.variables = [
                'uniform_uncertain = %s' % self.total_parameters()]
        else:
            self.input.variables = [
                'continuous_design = %s' % self.total_parameters()]

        if need_start:
            initial = [str(val) for val in self.eval_parameters(dtype=None)]
            self.input.variables.append(
                '    initial_point %s' % ' '.join(initial))

        self.input.variables.extend([
            '    lower_bounds  %s' % ' '.join(lbounds),
            '    upper_bounds  %s' % ' '.join(ubounds),
            '    descriptors   %s' % ' '.join(names)
        ])



## for testing
class ParameterStudy(Assembly):
    """ Use DAKOTA to run a multidimensional parameter study. """

    def configure(self):
        """ Configure driver and its workflow. """
        super(Assembly, self).configure()
        self.add('rosenbrock', Rosenbrock()) 

        driver = self.add('driver', DakotaStudy())
        driver.tabular_graphics_data = True  ### special flag to turn on graphics, don't just write into strategy field!
        driver.workflow.add('rosenbrock')
        driver.stdout = 'dakota.out'
        driver.stderr = 'dakota.err'
        driver.partitions = [6, 6]

        driver.add_parameter('rosenbrock.x', low=-2, high=2)
        driver.add_objective('rosenbrock.f')


def run_test():
    study = ParameterStudy()
    study.run()

####
class DakLauncher(object):
    def dakota_callback(self, **kwargs):
        print " I got called , ugh "
def just_run():
    run_dakota('driver.in',data=DakLauncher())
#######

if __name__=="__main__":
    run_test()
#    just_run()

