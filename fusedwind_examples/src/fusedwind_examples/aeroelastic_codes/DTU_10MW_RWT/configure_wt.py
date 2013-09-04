

from openmdao.main.api import Assembly
from fusedwind.lib.fusedIO import FUSEDWindIO
from fusedwind.turbine_aeroelastic.configurations import WTConfigurationBuilder


class WTConfiguration(Assembly):

    def configure(self):

        self.add('inputs', WTConfigurationBuilder())

        # configuring a WT manually
        wt = self.inputs.wt

        wt.nblades = 3
        wt.rotor_radius = 89.166
        wt.tower_height = 116.36
        wt.tower_bottom_radius = 4.15
        wt.tower_top_radius = 2.75
        wt.tilt_angle = 5.
        wt.cone_angle = -2.5
        wt.hub_height = 119.
        wt.hub_overhang = 7.1
        wt.hub_radius = 2.8

        # this should build the basic wt configuration
        self.inputs.configure_wt()


if __name__ == '__main__':

    top = WTConfiguration()

    # list main bodies
    top.inputs.wt.main_bodies.list_containers()
    io = FUSEDWindIO()
    io.vtrees_out = top.inputs.wt
    io.write_master()

    io2=FUSEDWindIO()
    io2.master_input_file='fusedwind_master_out.json'
    io2.load_master()


