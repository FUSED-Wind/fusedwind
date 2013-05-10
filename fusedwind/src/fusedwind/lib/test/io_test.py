


from openmdao.main.api import Component, Assembly 
from fusedwind.vartrees.api import *
from fusedwind.lib.fusedvartree import FusedIOVariableTree
from fusedwind.lib.fusedIO import FUSEDWindIO

class NewTree(FusedIOVariableTree):

    pass

class FusedAssebly(Assembly):

    def configure(self):
        self.add('vtrees',Component())
        self.vtrees.add('turbine', WindTurbineVT())
        self.vtrees.turbine.turbine_name = 'DTU 10MW RWT'
        self.vtrees.add('rotor', RotorVT())
        self.vtrees.rotor.hub_height = 119.
        self.vtrees.rotor.diameter = 178.332
        self.vtrees.rotor.nb = 3
        self.vtrees.rotor.cone_angle = 2.5
        self.vtrees.rotor.tilt_angle = 5.
        self.vtrees.rotor.mass = 227962.
        self.vtrees.rotor.overhang = 7.1
        self.vtrees.add('blade', BladeVT())
        self.vtrees.blade.airfoils = ['cylinder','FFA-W3-480GF','FFA-W3-360GF','FFA-W3-301','FFA-W3-241']
        self.vtrees.blade.length = 89.166
        self.vtrees.blade.max_chord = 6.203
        self.vtrees.blade.tip_chord = 1.23
        self.vtrees.blade.root_chord = 5.38
        self.vtrees.add('machine_type', VarSpeedVarPitch())
        self.vtrees.machine_type.ratedPower = 10.e7
        self.vtrees.machine_type.minOmega = 6.
        self.vtrees.machine_type.maxOmega = 9.6
        self.vtrees.machine_type.Vin = 4.
        self.vtrees.machine_type.Vout = 25.
        self.vtrees.add('hub', HubVT())
        self.vtrees.hub.diameter = 5.6
        self.vtrees.add('nacelle', NacelleVT())
        self.vtrees.nacelle.mass = 446036.
        self.vtrees.add('tower', TowerVT())
        self.vtrees.tower.mass = 628442.
        self.vtrees.add('airfoil_data',AirfoilDataArrayVT())
        data = AirfoilDataVT()
        data.alpha = np.linspace(0,20,11)
        data.cl = 2. * np.pi * data.alpha * np.pi / 180.
        self.vtrees.airfoil_data.polars.append(data)

        # test that a warning is raised if the vartree is unknown
        #self.vtrees.add('newtree',NewTree())


if __name__ == "__main__":
    # load some assembly
    top = FusedAssebly()

    # start an empty IO object
    io = FUSEDWindIO()
    io.add('vtrees_out',top.vtrees)
    # write JSON file
    io.write_master()

    # read it again
    io.master_input_file = io.master_output_file
    io.load_master()




