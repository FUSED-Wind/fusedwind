


from openmdao.main.api import Component 
from fusedwind.vartrees.api import *
from fusedwind.lib.fusedvartree import FusedIOVariableTree
from fusedwind.lib.fusedIO import FUSEDWindIO

class NewTree(FusedIOVariableTree):

    pass

top = Component()

top.add('turbine', WindTurbineVT())
top.add('rotor', RotorVT())
top.add('blade', BladeVT())
top.add('machine_type', FixedSpeedFixedPitch())
top.add('hub', HubVT())
top.add('nacelle', NacelleVT())
top.add('tower', TowerVT())
top.add('airfoil_data',AirfoilDataArrayVT())
data = AirfoilDataVT()
data.alpha = np.linspace(0,20,11)
data.cl = 2. * np.pi * data.alpha * np.pi / 180.
top.airfoil_data.polars.append(data)

# test that a warning is raised if the vartree is unknown
#top.add('newtree',NewTree())

# IO class
io = FUSEDWindIO()
# add the 
io.add('top',top)

# write JSON file
io.write_master()

# read it again
io.master_input_file = io.master_output_file
io.load_master()




