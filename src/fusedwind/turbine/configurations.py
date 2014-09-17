
import numpy as np
from openmdao.main.api import Component
from fusedwind.turbine_aeroelastic.fused_turbine_vt import TurbineVT, MainBody
from openmdao.lib.datatypes.api import VarTree


class WTConfigurationBuilder(Component):
    """
    class for generating a wind turbine configuration
    """

    wt = VarTree(TurbineVT(), iotype='out', desc='Variable trees containing WT configuration')

    def add_main_body(self, name):

        self.wt.main_bodies.add(name, VarTree(MainBody()))
        return getattr(self.wt.main_bodies, name)

    def get_main_body(self, name):

        return getattr(self.wt.main_bodies, name)

    def remove_main_body(self, name):

        self.wt.main_bodies.delete(name)


    def configure_wt(self):

        self.configure_tower_body()
        self.configure_towertop_body()
        self.configure_shaft_body()
        self.configure_hub_bodies()
        self.configure_blade_bodies()

        # self.add_tower_aerodrag()
        # self.add_nacelle_aerodrag()

    def configure_tower_body(self):
        """convenience method for adding tower body with orientation and constraints"""

        b = self.add_main_body('tower')
        b.initialize_geom(10)
        b.geom.main_axis[:, 2] = np.linspace(0, -self.wt.tower_height, 10)
        b.add_orientation('base')
        b.orientations[0].eulerang.append(np.array([0, 0, 0]))
        b.add_constraint('fixed')

        return b

    def configure_towertop_body(self):
        """convenience method for adding towertop body with orientation and constraints"""

        b = self.add_main_body('towertop')
        b.initialize_geom(2)
        b.geom.main_axis[-1, 2] = -self.wt.nacelle_diameter / 2.
        b.add_orientation('relative')
        b.orientations[0].mbdy1_name = 'tower'
        b.orientations[0].eulerang.append(np.array([0, 0, 0]))
        b.add_constraint('fixed_to_body', body1='tower')

    def configure_shaft_body(self):
        """convenience method for adding shaft body with orientation and constraints"""

        b =self.add_main_body('shaft')
        b.initialize_geom(5)
        b.geom.main_axis[:, 2] = np.linspace(0, self.wt.shaft_length, 5)
        b.add_orientation('relative')
        b.orientations[0].mbdy1_name = 'towertop'
        if self.wt.orientation == 'upwind':
            b.orientations[0].eulerang.append(np.array([90, 0, 0]))
        else:
            b.orientations[0].eulerang.append(np.array([-90, 0, 0]))

        b.orientations[0].eulerang.append(np.array([self.wt.tilt_angle, 0, 0]))
        b.orientations[0].initial_speed = 0.314 # ???
        b.orientations[0].rotation_dof = [0, 0, -1]
        b.add_constraint('free', body1='towertop', con_name='shaft_rot', DOF=np.array([0,0,0,0,0,-1]))

    def configure_hub_bodies(self):
        """convenience method for adding hub bodies with orientation and constraints"""

        b = self.add_main_body('hub1')
        b.initialize_geom(2)
        b.geom.main_axis[1, 2] = self.wt.hub_radius
        b.nbodies = 1
        b.add_orientation('relative')
        b.orientations[0].mbdy1_name = 'shaft'
        b.orientations[0].eulerang.append(np.array([-90, 0, 0]))
        b.orientations[0].eulerang.append(np.array([0., 180., 0]))
        b.orientations[0].eulerang.append(np.array([self.wt.cone_angle, 0, 0]))
        b.add_constraint('fixed_to_body', body1='shaft')

        for i in range(1, self.wt.nblades):
            b = self.add_main_body('hub'+str(i+1))
            b.copy_main_body = 'hub1'
            b.add_orientation('relative')
            b.orientations[0].mbdy1_name = 'shaft'
            b.orientations[0].eulerang.append(np.array([-90, 0, 0]))
            b.orientations[0].eulerang.append(np.array([0., 60. - (i-1) * 120., 0]))
            b.orientations[0].eulerang.append(np.array([self.wt.cone_angle, 0, 0]))
            b.add_constraint('fixed_to_body', body1='shaft')

    def configure_blade_bodies(self):
        """convenience method for adding blade bodies with orientation and constraints"""

        b = self.add_main_body('blade1')
        b.geom.main_axis = self.wt.blade_geom.main_axis
        b.geom.rot_z = self.wt.blade_geom.rot_z
        b.nbodies = 10
        b.add_orientation('relative')
        b.orientations[0].mbdy1_name = 'hub1'
        b.orientations[0].eulerang.append(np.array([0, 0, 0]))
        b.add_constraint('prescribed_angle', body1='hub1', con_name='pitch1', DOF=np.array([0,0,0,0,0,-1]))

        for i in range(1, self.wt.nblades):
            b = self.add_main_body('blade'+str(i+1))
            b.copy_main_body = 'blade1'
            b.add_orientation('relative')
            b.orientations[0].mbdy1_name = 'hub'+str(i+1)
            b.orientations[0].eulerang.append(np.array([0, 0, 0]))
            b.add_constraint('prescribed_angle', body1='hub'+str(i+1), con_name='pitch'+str(i+1), DOF=np.array([0,0,0,0,0,-1]))
