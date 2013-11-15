from openmdao.main.api import Component, Assembly, set_as_top, VariableTree
from openmdao.main.datatypes.api import Int, Bool, Float, Array, Str, VarTree

# strictly put variables for OpenMDAO

class Blades(VariableTree):

    mass = Float(0.0, units='kg', desc= 'mass of component')
    cost = Float(0.0, units='USD', desc= 'cost of component')
    length = Float(0.0, units='m', desc= 'length of component')
    width = Float(0.0, units='m', desc= 'diameter of component')

    def __init__(self):
        """ 
        Blades Variable Tree
        
        Parameters
        ----------
        mass : float
          mass [kg]
        cost : float
          cost
        length : float
          length of component [m]
        width : float
          width of component [m]
        
        """
        super(Blades, self).__init__()

    def printVT(self):
        """ Prints Variable Tree """
        
        print "Blade design results:"
        print "mass (kg)| %f" % self.mass
        print "cost (USD)|%f" % self.cost

    def fwriteVT(self, fwritef):
        """ Prints Variable tree to file 
        
        Parameters
        ----------
        fwritef : file
          file for variable tree print out
        """
        
        if fwritef.closed == True:
            # TODO: raise an error
            pass

        fwritef.write("Blade design results:|")
        fwritef.write("mass (kg)| %f|" % self.mass)
        fwritef.write("cost (USD)|%f|" % self.cost)

class Hub(VariableTree):

    mass = Float(0.0, units='kg', desc= 'mass of component')
    cost = Float(0.0, units='USD', desc= 'cost of component')
    diameter = Float(0.0, units='m', desc= 'diameter of component')

    def __init__(self):
        """ 
        Hub Variable Tree
        
        Parameters
        ----------
        mass : float
          mass [kg]
        cost : float
          cost
        diameter : float
          diameter [m]
        
        """
        super(Hub, self).__init__()

    def printVT(self):
        """ Prints Variable Tree 
        """
        
        print "Hub design results:"
        print "mass (kg)| %f" % self.mass
        print "cost (USD)|%f" % self.cost

    def fwriteVT(self, fwritef):
        """ Prints Variable tree to file 
        
        Parameters
        ----------
        fwritef : file
          file for variable tree print out
        """

        if fwritef.closed == True:
            # TODO: raise an error
            pass

        fwritef.write("Hub design results:|")
        fwritef.write("mass (kg)| %f|" % self.mass)
        fwritef.write("cost (USD)|%f|" % self.cost)

class PitchSys(VariableTree):

    mass = Float(0.0, units='kg', desc= 'mass of component')
    cost = Float(0.0, units='USD', desc= 'cost of component')

    def __init__(self):
        """ 
        Pitch System Variable Tree
        
        Parameters
        ----------
        mass : float
          mass [kg]
        cost : float
          cost
        
        """
        super(PitchSys, self).__init__()

    def printVT(self):
        """ Prints Variable Tree """
        
        print "Pitch System design results:"
        print "mass (kg)| %f" % self.mass
        print "cost (USD)|%f" % self.cost

    def fwriteVT(self, fwritef):
        """ Prints Variable tree to file 
        
        Parameters
        ----------
        fwritef : file
          file for variable tree print out
        """
        
        if fwritef.closed == True:
            # TODO: raise an error
            pass

        fwritef.write("Pitch System design results:|")
        fwritef.write("mass (kg)| %f|" % self.mass)
        fwritef.write("cost (USD)|%f|" % self.cost)

class Spinner(VariableTree):

    mass = Float(0.0, units='kg', desc= 'mass of component')
    cost = Float(0.0, units='USD', desc= 'cost of component')

    def __init__(self):
        """ 
        Spinner Variable Tree
        
        Parameters
        ----------
        mass : float
          mass [kg]
        cost : float
          cost
        
        """
        super(Spinner, self).__init__()

    def printVT(self):
        """ Prints Variable Tree 
        """
        
        print "Spinner / Nose Cone design results:"
        print "mass (kg)| %f" % self.mass
        print "cost (USD)|%f" % self.cost

    def fwriteVT(self, fwritef):
        """ Prints Variable tree to file 
        
        Parameters
        ----------
        fwritef : file
          file for variable tree print out
        """
        
        if fwritef.closed == True:
            # TODO: raise an error
            pass

        fwritef.write("Spinner / Nose Cone design results:|")
        fwritef.write("mass (kg)| %f|" % self.mass)
        fwritef.write("cost (USD)|%f|" % self.cost)

class HubSystem(VariableTree):
    
    mass = Float(0.0, units='kg', desc= 'mass of component')
    cost = Float(0.0, units='USD', desc= 'cost of component')
    
    hub = VarTree(Hub())
    pitchsys = VarTree(PitchSys())
    spinner = VarTree(Spinner())

    def __init__(self):
        """ 
        Hub System Variable Tree
        
        Parameters
        ----------
        mass : float
          mass [kg]
        cost : float
          cost
        hub : Hub
          Hub component
        pitchsys : PitchSys
          Pitch System assembly
        spinner : Spinner
          Spinner component
        
        """
        super(HubSystem, self).__init__()

    def sumMass(self):
        """ Sum mass of hub, pitch system and spinner."""
        self.mass = self.hub.mass + self.pitchsys.mass + self.spinner.mass

    def sumCost(self):
        """ Sum cost of hub, pitch system and spinner."""
       
        self.cost = self.hub.cost + self.pitchsys.cost + self.spinner.cost

    def printVT(self):
        """ Prints Variable Tree 
        """
        
        print "Hub System design results:"
        print "mass (kg)| %f" % self.mass
        print "cost (USD)|%f" % self.cost
        self.hub.printVT()
        self.pitchsys.printVT()
        self.spinner.printVT()

    def fwriteVT(self, fwritef):
        """ Prints Variable tree to file 
        
        Parameters
        ----------
        fwritef : file
          file for variable tree print out
        """
        
        if fwritef.closed == True:
            # TODO: raise an error
            pass

        fwritef.write("Hub System design results:|")
        fwritef.write("mass (kg)| %f|" % self.mass)
        fwritef.write("cost (USD)|%f|" % self.cost)
        fwritef.write("\n")
        self.hub.fwriteVT(fwritef)
        fwritef.write("\n")
        self.pitchsys.fwriteVT(fwritef)
        fwritef.write("\n")
        self.spinner.fwriteVT(fwritef)
        fwritef.write("\n")

class Rotor(VariableTree):

    mass = Float(0.0, units='kg', desc= 'mass of turbine')
    cost = Float(0.0, units='USD', desc= 'cost of turbine')
    
    blades = VarTree(Blades())
    hubsystem = VarTree(HubSystem())
    
    def __init__(self):
        """ 
        Rotor nested tree includes blades, hub, spinner cone and pitch system
        
        Parameters
        ----------
        mass : float
          mass [kg]
        cost : float
          cost
        blades : Blades
          blades component
        hubsystem : HubSystem
          Hub system assembly  
        
        """
        super(Rotor, self).__init__()

    def sumMass(self):
        """ Sums mass of blades and hub system."""
       
        self.mass = self.blades.mass + self.hubsystem.mass

    def sumCost(self):
        """ Sums cost of blades and hub system."""
       
        self.cost = self.blades.cost + self.hubsystem.mass

    def printVT(self):
        """ Prints Variable Tree """
        
        print "Rotor design results:"
        print "mass (kg)| %f" % self.mass
        print "cost (USD)|%f" % self.cost
        self.blades.printVT()
        self.hubsystem.printVT()

    def fwriteVT(self, fwritef):
        """ Prints Variable tree to file 
        
        Parameters
        ----------
        fwritef : file
          file for variable tree print out
        """
        
        if fwritef.closed == True:
            # TODO: raise an error
            pass

        fwritef.write("Rotor design results:|")
        fwritef.write("mass (kg)| %f|" % self.mass)
        fwritef.write("cost (USD)|%f|" % self.cost)
        fwritef.write("\n")
        self.blades.fwriteVT(fwritef)
        fwritef.write("\n")
        self.hubsystem.fwriteVT(fwritef)


class LSS(VariableTree):

    mass = Float(0.0, units='kg', desc= 'mass of component')
    cost = Float(0.0, units='USD', desc= 'cost of component')

    def __init__(self):
        """ 
        LSS Variable Tree
        
        Parameters
        ----------
        mass : float
          mass [kg]
        cost : float
          cost
        
        """
        super(LSS, self).__init__()

    def printVT(self):
        """ Prints Variable Tree """
   
        print "Low Speed Shaft design results:"
        print "mass (kg)| %f" % self.mass
        print "cost (USD)|%f" % self.cost

    def fwriteVT(self, fwritef):
        """ Prints Variable tree to file 
        
        Parameters
        ----------
        fwritef : file
          file for variable tree print out
        """
        if fwritef.closed == True:
            # TODO: raise an error
            pass

        fwritef.write("Low Speed Shaft design results:|")
        fwritef.write("mass (kg)| %f|" % self.mass)
        fwritef.write("cost (USD)|%f|" % self.cost)

class MainBearings(VariableTree):

    mass = Float(0.0, units='kg', desc= 'mass of component')
    cost = Float(0.0, units='USD', desc= 'cost of component')

    def __init__(self):
        """ 
        Main Bearings Variable Tree
        
        Parameters
        ----------
        mass : float
          mass [kg]
        cost : float
          cost
        
        """
        super(MainBearings, self).__init__()

    def printVT(self):
        """ Prints Variable Tree """
   
        print "Main Bearings design results:"
        print "mass (kg)| %f" % self.mass
        print "cost (USD)|%f" % self.cost

    def fwriteVT(self, fwritef):
        """ Prints Variable tree to file 
        
        Parameters
        ----------
        fwritef : file
          file for variable tree print out
        """
        if fwritef.closed == True:
            # TODO: raise an error
            pass

        fwritef.write("Main Bearings design results:|")
        fwritef.write("mass (kg)| %f|" % self.mass)
        fwritef.write("cost (USD)|%f|" % self.cost)

class Gearbox(VariableTree):

    mass = Float(0.0, units='kg', desc= 'mass of component')
    cost = Float(0.0, units='USD', desc= 'cost of component')

    def __init__(self):
        """ 
        Gearbox Variable Tree
        
        Parameters
        ----------
        mass : float
          mass [kg]
        cost : float
          cost
        
        """
        super(Gearbox, self).__init__()

    def printVT(self):
        """ Prints Variable Tree """
   
        print "Gearbox design results:"
        print "mass (kg)| %f" % self.mass
        print "cost (USD)|%f" % self.cost

    def fwriteVT(self, fwritef):
        """ Prints Variable tree to file 
        
        Parameters
        ----------
        fwritef : file
          file for variable tree print out
        """
        if fwritef.closed == True:
            # TODO: raise an error
            pass

        fwritef.write("Gearbox design results:|")
        fwritef.write("mass (kg)| %f|" % self.mass)
        fwritef.write("cost (USD)|%f|" % self.cost)

class HSS(VariableTree):

    mass = Float(0.0, units='kg', desc= 'mass of component')
    cost = Float(0.0, units='USD', desc= 'cost of component')

    def __init__(self):
        """ 
        HSS Variable Tree
        
        Parameters
        ----------
        mass : float
          mass [kg]
        cost : float
          cost
        
        """
        super(HSS, self).__init__()

    def printVT(self):
        """ Prints Variable Tree """
   
        print "High Speed Shaft design results:"
        print "mass (kg)| %f" % self.mass
        print "cost (USD)|%f" % self.cost

    def fwriteVT(self, fwritef):
        """ Prints Variable tree to file 
        
        Parameters
        ----------
        fwritef : file
          file for variable tree print out
        """
        if fwritef.closed == True:
            # TODO: raise an error
            pass

        fwritef.write("High Speed Shaft design results:|")
        fwritef.write("mass (kg)| %f|" % self.mass)
        fwritef.write("cost (USD)|%f|" % self.cost)

class MechBrakes(VariableTree):

    mass = Float(0.0, units='kg', desc= 'mass of component')
    cost = Float(0.0, units='USD', desc= 'cost of component')

    def __init__(self):
        """ 
        Mechanical Brakes Variable Tree
        
        Parameters
        ----------
        mass : float
          mass [kg]
        cost : float
          cost
        
        """
        super(MechBrakes, self).__init__()

    def printVT(self):
        """ Prints Variable Tree """
   
        print "Mechanical Brakes design results:"
        print "mass (kg)| %f" % self.mass
        print "cost (USD)|%f" % self.cost

    def fwriteVT(self, fwritef):
        """ Prints Variable tree to file 
        
        Parameters
        ----------
        fwritef : file
          file for variable tree print out
        """
        if fwritef.closed == True:
            # TODO: raise an error
            pass

        fwritef.write("Mechanical Brakes design results:|")
        fwritef.write("mass (kg)| %f|" % self.mass)
        fwritef.write("cost (USD)|%f|" % self.cost)

class Generator(VariableTree):

    mass = Float(0.0, units='kg', desc= 'mass of component')
    cost = Float(0.0, units='USD', desc= 'cost of component')

    def __init__(self):
        """ 
        Generator Variable Tree
        
        Parameters
        ----------
        mass : float
          mass [kg]
        cost : float
          cost
        
        """
        super(Generator, self).__init__()

    def printVT(self):
        """ Prints Variable Tree """
   
        print "Generator design results:"
        print "mass (kg)| %f" % self.mass
        print "cost (USD)|%f" % self.cost

    def fwriteVT(self, fwritef):
        """ Prints Variable tree to file 
        
        Parameters
        ----------
        fwritef : file
          file for variable tree print out
        """
        if fwritef.closed == True:
            # TODO: raise an error
            pass

        fwritef.write("Generator design results:|")
        fwritef.write("mass (kg)| %f|" % self.mass)
        fwritef.write("cost (USD)|%f|" % self.cost)

class VSElectronics(VariableTree):

    mass = Float(0.0, units='kg', desc= 'mass of component')
    cost = Float(0.0, units='USD', desc= 'cost of component')

    def __init__(self):
        """ 
        Variable Speed Electronics Variable Tree
        
        Parameters
        ----------
        mass : float
          mass [kg]
        cost : float
          cost
        
        """
        super(VSElectronics, self).__init__()

    def printVT(self):
        """ Prints Variable Tree """
   
        print "Variable Speed Electronics design results:"
        print "mass (kg)| %f" % self.mass
        print "cost (USD)|%f" % self.cost

    def fwriteVT(self, fwritef):
        """ Prints Variable tree to file 
        
        Parameters
        ----------
        fwritef : file
          file for variable tree print out
        """
        if fwritef.closed == True:
            # TODO: raise an error
            pass

        fwritef.write("Variable Speed Electronics design results:|")
        fwritef.write("mass (kg)| %f|" % self.mass)
        fwritef.write("cost (USD)|%f|" % self.cost)

class ElecConnections(VariableTree):

    mass = Float(0.0, units='kg', desc= 'mass of component')
    cost = Float(0.0, units='USD', desc= 'cost of component')

    def __init__(self):
        """ 
        Electrical Connections Variable Tree
        
        Parameters
        ----------
        mass : float
          mass [kg]
        cost : float
          cost
        
        """
        super(ElecConnections, self).__init__()

    def printVT(self):
        """ Prints Variable Tree """
   
        print "Electrical Connections design results:"
        print "mass (kg)| %f" % self.mass
        print "cost (USD)|%f" % self.cost

    def fwriteVT(self, fwritef):
        """ Prints Variable tree to file 
        
        Parameters
        ----------
        fwritef : file
          file for variable tree print out
        """
        if fwritef.closed == True:
            # TODO: raise an error
            pass

        fwritef.write("Electrical Connections design results:|")
        fwritef.write("mass (kg)| %f|" % self.mass)
        fwritef.write("cost (USD)|%f|" % self.cost)

class Hydraulics(VariableTree):

    mass = Float(0.0, units='kg', desc= 'mass of component')
    cost = Float(0.0, units='USD', desc= 'cost of component')

    def __init__(self):
        """ 
        Hydraulics Variable Tree
        
        Parameters
        ----------
        mass : float
          mass [kg]
        cost : float
          cost
        
        """
        super(Hydraulics, self).__init__()

    def printVT(self):
        """ Prints Variable Tree """
   
        print "Hydraulics and Cooling design results:"
        print "mass (kg)| %f" % self.mass
        print "cost (USD)|%f" % self.cost

    def fwriteVT(self, fwritef):
        """ Prints Variable tree to file 
        
        Parameters
        ----------
        fwritef : file
          file for variable tree print out
        """
        if fwritef.closed == True:
            # TODO: raise an error
            pass

        fwritef.write("Hydraulics and Cooling design results:|")
        fwritef.write("mass (kg)| %f|" % self.mass)
        fwritef.write("cost (USD)|%f|" % self.cost)

class Controls(VariableTree):

    mass = Float(0.0, units='kg', desc= 'mass of component')
    cost = Float(0.0, units='USD', desc= 'cost of component')

    def __init__(self):
        """ 
        Controls Variable Tree
        
        Parameters
        ----------
        mass : float
          mass [kg]
        cost : float
          cost
        
        """
        super(Controls, self).__init__()

    def printVT(self):
        """ Prints Variable Tree """
   
        print "Controls design results:"
        print "mass (kg)| %f" % self.mass
        print "cost (USD)|%f" % self.cost

    def fwriteVT(self, fwritef):
        """ Prints Variable tree to file 
        
        Parameters
        ----------
        fwritef : file
          file for variable tree print out
        """
        if fwritef.closed == True:
            # TODO: raise an error
            pass

        fwritef.write("Controls design results:|")
        fwritef.write("mass (kg)| %f|" % self.mass)
        fwritef.write("cost (USD)|%f|" % self.cost)

class Yaw(VariableTree):

    mass = Float(0.0, units='kg', desc= 'mass of component')
    cost = Float(0.0, units='USD', desc= 'cost of component')

    def __init__(self):
        """ 
        Yaw Variable Tree
        
        Parameters
        ----------
        mass : float
          mass [kg]
        cost : float
          cost
        
        """
        super(Yaw, self).__init__()

    def printVT(self):
        """ Prints Variable Tree """
   
        print "Yaw System design results:"
        print "mass (kg)| %f" % self.mass
        print "cost (USD)|%f" % self.cost

    def fwriteVT(self, fwritef):
        """ Prints Variable tree to file 
        
        Parameters
        ----------
        fwritef : file
          file for variable tree print out
        """
        if fwritef.closed == True:
            # TODO: raise an error
            pass

        fwritef.write("Yaw System design results:|")
        fwritef.write("mass (kg)| %f|" % self.mass)
        fwritef.write("cost (USD)|%f|" % self.cost)

class MainFrame(VariableTree):

    mass = Float(0.0, units='kg', desc= 'mass of component')
    cost = Float(0.0, units='USD', desc= 'cost of component')

    def __init__(self):
        """ 
        MainFrame Variable Tree
        
        Parameters
        ----------
        mass : float
          mass [kg]
        cost : float
          cost
        
        """
        super(MainFrame, self).__init__()

    def printVT(self):
        """ Prints Variable Tree """
   
        print "Mainframe design results:"
        print "mass (kg)| %f" % self.mass
        print "cost (USD)|%f" % self.cost

    def fwriteVT(self, fwritef):
        """ Prints Variable tree to file 
        
        Parameters
        ----------
        fwritef : file
          file for variable tree print out
        """
        if fwritef.closed == True:
            # TODO: raise an error
            pass

        fwritef.write("Mainframe design results:|")
        fwritef.write("mass (kg)| %f|" % self.mass)
        fwritef.write("cost (USD)|%f|" % self.cost)

class NacelleCover(VariableTree):

    mass = Float(0.0, units='kg', desc= 'mass of component')
    cost = Float(0.0, units='USD', desc= 'cost of component')

    def __init__(self):
        """ 
        Nacelle Variable Tree
        
        Parameters
        ----------
        mass : float
          mass [kg]
        cost : float
          cost
        
        """
        super(NacelleCover, self).__init__()

    def printVT(self):
        """ Prints Variable Tree """
   
        print "Nacelle Cover design results:"
        print "mass (kg)| %f" % self.mass
        print "cost (USD)|%f" % self.cost

    def fwriteVT(self, fwritef):
        """ Prints Variable tree to file 
        
        Parameters
        ----------
        fwritef : file
          file for variable tree print out
        """
        if fwritef.closed == True:
            # TODO: raise an error
            pass

        fwritef.write("Nacelle Cover design results:|")
        fwritef.write("mass (kg)| %f|" % self.mass)
        fwritef.write("cost (USD)|%f|" % self.cost)



class Nacelle(VariableTree):

    mass = Float(0.0, units='kg', desc= 'mass of component')
    cost = Float(0.0, units='USD', desc= 'cost of component')
    length = Float(0.0, units='m', desc= 'length of component')
    height = Float(0.0, units='m', desc= 'length of component')
    width = Float(0.0, units='m', desc= 'length of component')

    lss = VarTree(LSS())
    mainbearings = VarTree(MainBearings())
    gearbox = VarTree(Gearbox())
    mechbrakes = VarTree(MechBrakes())
    generatorc = VarTree(Generator())
    vselectronics = VarTree(VSElectronics())
    elecconnections = VarTree(ElecConnections())
    hydraulics = VarTree(Hydraulics())
    controls = VarTree(Controls())
    yaw = VarTree(Yaw())
    mainframe = VarTree(MainFrame())
    nacellecover = VarTree(NacelleCover())

    def __init__(self):
        """ 
        Nacelle nested tree includes all drivetrain components, yaw system, mainframe and auxiliary equipment in the nacelle
    
        Parameters
        ----------
        mass : float
          mass [kg]
        cost : float
          cost
        length : float
          length of component [m]
        width : float
          width of component [m]
        height : float
          height of component [m]   
        lss : LSS
          Low Speed Shaft component 
        mainbearings : MainBearings
          Main Bearings component
        gearbox : Gearbox
          gearbox component
        mechbrakes : MechBrakes
          mechanical brakes / HSS component
        generatorc : Generator
          generator component
        vselectronics : VSElectronics
          Variable Speed Electronics component
        elecconnections : ElecConnections
          electrical connections component
        hydraulics : Hydraulics
          hydraulics component
        controls : Controls
          controls component
        yaw : Yaw
          yaw component
        mainframe : Mainframe
          mainframe component
        nacellecover : NacelleCover
          nacelle cover component
        """
        
        super(Nacelle, self).__init__()

    def sumMass(self):
        """ Sum mass of all nacelle components in assembly."""

        self.mass = self.lss.mass + self.mainbearings.mass + self.gearbox.mass + self.mechbrakes.mass + self.generator.mass + \
                    self.vselectronics.mass + self.elecconnections.mass + self.hydraulics.mass + self.controls.mass + self.yaw.mass + self.mainframe.mass + self.nacellecover.mass

    def sumCost(self):
        """ Sum cost of all nacelle components in assembly."""

        self.cost = self.lss.cost + self.mainbearings.cost + self.gearbox.cost + self.mechbrakes.cost + self.generator.cost + \
                    self.vselectronics.cost + self.elecconnections.cost + self.hydraulics.cost + self.controls.cost + self.yaw.cost + self.mainframe.cost + self.nacellecover.cost

    def printVT(self):
        """ Prints Variable Tree """
        
        print "Nacelle design results:"
        print "mass (kg)| %f" % self.mass
        print "cost (USD)|%f" % self.cost
        self.lss.printVT()
        self.mainbearings.printVT()
        self.gearbox.printVT()
        self.mechbrakes.printVT()
        self.generatorc.printVT()
        self.vselectronics.printVT()
        self.elecconnections.printVT()
        self.hydraulics.printVT()
        self.controls.printVT()
        self.yaw.printVT()
        self.mainframe.printVT()    
        self.nacellecover.printVT()      

    def fwriteVT(self, fwritef):
        """ Prints Variable tree to file 
        
        Parameters
        ----------
        fwritef : file
          file for variable tree print out
        """
        
        if fwritef.closed == True:
            # TODO: raise an error
            pass

        fwritef.write("Nacelle design results:|")
        fwritef.write("mass (kg)| %f|" % self.mass)
        fwritef.write("cost (USD)|%f|" % self.cost)
        fwritef.write("\n")
        self.lss.fwriteVT(fwritef)
        fwritef.write("\n")
        self.mainbearings.fwriteVT(fwritef)
        fwritef.write("\n")
        self.gearbox.fwriteVT(fwritef)
        fwritef.write("\n")
        self.mechbrakes.fwriteVT(fwritef)
        fwritef.write("\n")
        self.generatorc.fwriteVT(fwritef)
        fwritef.write("\n")
        self.vselectronics.fwriteVT(fwritef)
        fwritef.write("\n")
        self.elecconnections.fwriteVT(fwritef)
        fwritef.write("\n")
        self.hydraulics.fwriteVT(fwritef)
        fwritef.write("\n")
        self.controls.fwriteVT(fwritef)
        fwritef.write("\n")
        self.yaw.fwriteVT(fwritef)
        fwritef.write("\n")
        self.mainframe.fwriteVT(fwritef)    
        fwritef.write("\n")
        self.nacellecover.fwriteVT(fwritef) 
        fwritef.write("\n")


class Tower(VariableTree):

    mass = Float(0.0, units='kg', desc= 'mass of component')
    cost = Float(0.0, units='USD', desc= 'cost of component')
    height = Float(0.0, units='m', desc= 'height of component')
    maxDiameter = Float(0.0, units='m', desc= 'diameter of component')

    def __init__(self):
        """ 
        Tower Variable Tree
        
        Parameters
        ----------
        mass : float
          mass [kg]
        cost : float
          cost
        height : float
          height of component [m]
        maxDiameter : float
          max diameter of component [m]
        
        """
        super(Tower, self).__init__()

    def printVT(self):
        """ Prints Variable Tree """
   
        print "Tower design results:"
        print "mass (kg)| %f" % self.mass
        print "cost (USD)|%f" % self.cost

    def fwriteVT(self, fwritef):
        """ Prints Variable tree to file 
        
        Parameters
        ----------
        fwritef : file
          file for variable tree print out
        """
        if fwritef.closed == True:
            # TODO: raise an error
            pass

        fwritef.write("Tower design results:|")
        fwritef.write("mass (kg)| %f|" % self.mass)
        fwritef.write("cost (USD)|%f|" % self.cost)

class Foundation(VariableTree):

    mass = Float(0.0, units='kg', desc= 'mass of component')
    cost = Float(0.0, units='USD', desc= 'cost of component')

    def __init__(self):
        """ 
        Foundation Variable Tree
        
        Parameters
        ----------
        mass : float
          mass [kg]
        cost : float
          cost
        
        """
        super(Foundation, self).__init__()

    def printVT(self):
        """ Prints Variable Tree """
   
        print "Foundation design results:"
        print "mass (kg)| %f" % self.mass
        print "cost (USD)|%f" % self.cost

    def fwriteVT(self, fwritef):
        """ Prints Variable tree to file 
        
        Parameters
        ----------
        fwritef : file
          file for variable tree print out
        """
        if fwritef.closed == True:
            # TODO: raise an error
            pass

        fwritef.write("Foundation design results:|")
        fwritef.write("mass (kg)| %f|" % self.mass)
        fwritef.write("cost (USD)|%f|" % self.cost)

class Turbine(VariableTree):

    mass = Float(0.0, units='kg', desc= 'mass of turbine')
    cost = Float(0.0, units='USD', desc= 'cost of turbine')
    RNAmass = Float(0.0, units='kg', desc = 'mass of RNA assembly')
    RNAcost = Float(0.0, units='USD', desc = 'cost of RNA assembly')
    
    rotor = VarTree(Rotor())
    nacelle = VarTree(Nacelle())
    tower = VarTree(Tower())
    
    def __init__(self):
        """ 
        Turbine class for put includes mass and cost of each component in sub-assemblies for rotor, nacelle and tower/foundation
        
        Parameters
        ----------
        mass : float
          mass of turbine [kg]
        cost : float
          cost of turbine
        RNAmass : float
          mass of RNA assembly
        RNAcost : float
          cost of RNA assembly
        rotor : Rotor
          rotor assembly
        nacelle : Nacelle
          nacelle assembly
        tower : Tower
          tower / support structure assembly
        
        """
        super(Turbine, self).__init__()

    def sumMass(self):
        """Sums mass of tower, rotor and nacelle."""

        self.mass = self.rotor.mass + self.nacelle.mass + self.tower.mass

    def sumRNAMass(self):
        """ Sums mass of rotor and nacelle."""

        self.RNAmass = self.rotor.mass + self.nacelle.mass

    def sumRNACost(self):
        """ Sums cost of rotor and nacelle."""

        self.RNAcost = self.rotor.cost + self.nacelle.cost

    def sumCost(self):
        """ Sums mass of rotor, nacelle and tower."""
        
        self.cost = self.rotor.cost + self.nacelle.cost + self.tower.cost

    def printVT(self):
        """ Prints Variable Tree """

        print "Turbine design results:"
        print "mass (kg)| %f" % self.mass
        print "cost (USD)|%f" % self.cost
        self.rotor.printVT()
        self.nacelle.printVT()
        self.tower.printVT()

    def fwriteVT(self, fwritef):
        """ Prints Variable tree to file 
        
        Parameters
        ----------
        fwritef : file
          file for variable tree print out
        """
        
        if fwritef.closed == True:
            # TODO: raise an error
            pass

        fwritef.write("Turbine design results:|")
        fwritef.write("mass (kg)| %f|" % self.mass)
        fwritef.write("cost (USD)|%f|" % self.cost)
        fwritef.write("\n")
        self.rotor.fwriteVT(fwritef)
        fwritef.write("\n")
        self.nacelle.fwriteVT(fwritef)
        fwritef.write("\n")
        self.tower.fwriteVT(fwritef)
        fwritef.write("\n")

class PlantBOS(VariableTree):


    # plant cost variables
    totalBOSCost = Float(0.0, units='USD', desc= 'total BOS costs')

    foundationCost = Float(0.0, units='USD', desc = 'foundation capital costs')
 
    developmentCost = Float(0.0, units='USD', desc= 'cost of engineering, permits and other development related costs')
    engineeringCost = Float(0.0, units='USD', desc= 'cost of engineering')
    permittingCost = Float(0.0, units='USD', desc= 'cost of permitting')
    siteCharacterizationCost = Float(0.0, units='USD', desc= 'cost of site characterization')
    
    projectManagementCost = Float(0.0, units='USD', desc='project management costs')
 
    landCivilCost = Float(0.0, units='USD', desc= 'cost of road construction and civil work') 
    
    landTransportationCost = Float(0.0, units='USD', desc= 'cost of turbine transportation') 

    portsStagingCost = Float(0.0, units='USD', desc= 'cost of ports and staging')

    assemblyInstallationCost = Float(0.0, units='USD', desc= 'cost of assembly and installation') 
    assemblyCost = Float(0.0, units='USD', desc = 'turbine assembly costs')
    installationCost = Float(0.0, units='USD', desc = 'plant instllation costs')
    vesselsCost = Float(0.0, units='USD', desc = 'vessel costs')

    electricalInterconnectCost = Float(0.0, units='USD', desc= 'cost of electrical interconnection and equipment')

    offshoreAdditionalCost = Float(0.0, units='USD', desc = 'offshore additional capital expenditures (insurance, contingencies and decommissioning, other soft costs)')
    offshoreInsuranceCost = Float(0.0, units='USD', desc = 'offshore additional capital expenditures (insurance)')
    offshoreContingenciesCost = Float(0.0, units='USD', desc = 'offshore additional capital expenditures (contingencies)')

    offshoreDecommissioningCost = Float(0.0, units='USD', desc = 'offshore additional capital expenditures (decommissioning / surety bond)') 

    offshoreOtherCost = Float(0.0, units='USD', desc = 'other costs not captured above - such as access equipment and scour protection if not already covered')

    def __init__(self):
        """ 
        Plant class for put includes main cost level put variables for the balance of plant as well as the turbine.
        
        Parameters
        ----------
        totalBOSCost : float
          total BOS costs
        foundationCost : float
          foundation capital costs
        developmentCost : float
          cost of engineering, permits and other development related costs
        engineeringCost : float
          cost of engineering
        permittingCost : float
          cost of permitting
        siteCharacterizationCost : float
          cost of site characterization
        projectManagementCost : float
          project management costs
        landCivilCost : float
          cost of road construction and civil work  
        landTransportationCost : float
          cost of turbine transportation
        portsStagingCost : float
          cost of ports and staging
        assemblyInstallationCost : float
          cost of assembly and installation
        assemblyCost : float
          turbine assembly costs
        installationCost : float
          plant instllation costs
        vesselsCost : float
          vessel costs
        electricalInterconnectCost : float
          cost of electrical interconnection and equipment
        offshoreAdditionalCost : float
          offshore additional capital expenditures (insurance, contingencies and decommissioning, other soft costs)
        offshoreInsuranceCost : float
          offshore additional capital expenditures (insurance)
        offshoreContingenciesCost : float 
          offshore additional capital expenditures (contingencies)
        offshoreDecommissioningCost : float
          offshore additional capital expenditures (decommissioning / surety bond)
        offshoreOtherCost : float
          other costs not captured above - such as access equipment and scour protection if not already covered    
        """

        super(PlantBOS, self).__init__()

        # self.add('turbine', Turbine())                # TODO - for put side, not sure if plant and turbine should be coupled since different assemblies providing different pieces of put

    def printVT(self):
        """ Prints Variable Tree """

        print "Plant BOS cost puts:"
        print "totalBOScost| USD| %f" %self.totalBOSCost
        print " foundationCost| USD| %f" %self.foundationCost
        print " developmentCost| USD| %f" %self.developmentCost
        print "   engineeringcost| USD| %f" %self.engineeringCost
        print "   permittingCost| USD| %f" %self.permittingCost
        print "   siteCharacterizationCost| USD| %f" %self.siteCharacterizationCost
        print " projectManagementCost| USD| %f" %self.projectManagementCost
        print " landCivilCost| USD| %f" %self.landCivilCost
        print " landTransportationCost| USD| %f" %self.landTransportationCost
        print " assemblyInstallCost| USD| %f" %self.assemblyInstallationCost
        print "   assemblyCost| USD| %f" %self.assemblyCost
        print "   installationCost| USD| %f" %self.installationCost
        print "   vesselsCost| USD| %f" %self.vesselsCost
        print " portsStagingCost| USD| %f" %self.portsStagingCost
        print " elecInterconnectCost| USD| %f" %self.electricalInterconnectCost
        print " offshoreAdditionalCost| USD| %f" %self.offshoreAdditionalCost
        print "   offshoreInsuranceCost| USD| %f" %self.offshoreInsuranceCost
        print "   offshoreContingenciesCost| USD| %f" %self.offshoreContingenciesCost
        print " offshoreDecommissioningCost| USD| %f" %self.offshoreDecommissioningCost
        print " offshoreOtherCost| USD| %f" %self.offshoreOtherCost

    def fwriteVT(self, fwritef):
      
        """ Prints Variable tree to file 
        
        Parameters
        ----------
        fwritef : file
          file for variable tree print out
        """

        if fwritef.closed == True:
            # TODO: raise an error
            pass

        fwritef.write( "Plant BOS cost puts: \n")
        fwritef.write( "totalBOScost| USD| %f \n" %self.totalBOSCost)
        fwritef.write( "  foundationCost| USD| %f \n" %self.foundationCost)
        fwritef.write( "  developmentCost| USD| %f \n" %self.developmentCost)
        fwritef.write( "    engineeringCost| USD| %f \n" %self.engineeringCost)
        fwritef.write( "    permittingCost| USD| %f \n" %self.permittingCost)
        fwritef.write( "    siteCharacterizationCost| USD| %f \n" %self.siteCharacterizationCost)
        fwritef.write( "  projectManagementCost| USD| %f \n" %self.projectManagementCost)
        fwritef.write( "  landCivilCost| USD| %f \n" %self.landCivilCost)
        fwritef.write( "  landTransportationCost| USD| %f \n" %self.landTransportationCost)
        fwritef.write( "  assemblyInstallationCost| USD| %f \n" %self.assemblyInstallationCost)
        fwritef.write( "    assemblyCost| USD| %f \n" %self.assemblyCost)
        fwritef.write( "    installationCost| USD| %f \n" %self.installationCost)
        fwritef.write( "    vesselsCost| USD| %f \n" %self.vesselsCost)
        fwritef.write( "  portsStagingCost| USD| %f \n" %self.portsStagingCost)
        fwritef.write( "  electricalInterconnectCost| USD| %f \n" %self.electricalInterconnectCost)
        fwritef.write( "  offshoreAdditionalCost| USD| %f \n" %self.offshoreAdditionalCost)
        fwritef.write( "    offshoreInsuranceCost| USD| %f \n" %self.offshoreInsuranceCost)
        fwritef.write( "    offshoreContingenciesCost| USD| %f \n" %self.offshoreContingenciesCost)
        fwritef.write( "  offshoreDecommissioningCost| USD| %f \n" %self.offshoreDecommissioningCost)
        fwritef.write( "  offshoreOtherCost| USD| %f \n" %self.offshoreOtherCost)    

# strictly put variables for OpenMDAO
class PlantOM(VariableTree):

    # plant cost variables
    totalOMCost = Float(0.0, units='USD', desc = 'total costs for operations including planned and unplanned maintenance and fixed expenses')

    preventativeMaintenanceCost = Float(0.0, units='USD', desc= 'cost of preventative operations and maintenance')
    preventativeTurbineMaintenanceCost = Float(0.0, units='USD', desc= 'cost of wind turbine preventative operations and maintenance')
    preventativeBOPMaintenanceCost = Float(0.0, units='USD', desc= 'cost of BOP preventative operations and maintenance')

    correctiveMaintenanceCost = Float(0.0, units='USD', desc= 'cost of corrective operations and maintenance')
    correctiveTurbineMaintenanceCost = Float(0.0, units='USD', desc= 'cost of wind turbine corrective operations and maintenance')
    correctiveBOPMaintenanceCost = Float(0.0, units='USD', desc= 'cost of BOP corrective operations and maintenance')
    
    fixedOMCost = Float(0.0, units='USD', desc= 'fixed operational costs')  
    landLeaseCost = Float(0.0, units='USD', desc= 'cost of land leases')
    otherFixedCost = Float(0.0, units='USD', desc= 'other fixed operational costs')

    def __init__(self):
        """ 
        Plant class for put includes main cost level put variables for the balance of plant as well as the turbine
        
        Parameters
        ----------
        totalOMCost : float
          total costs for operations including planned and unplanned maintenance and fixed expenses
        preventativeMaintenanceCost : float
          cost of preventative operations and maintenance
        preventativeTurbineMaintenanceCost : float
          cost of wind turbine preventative operations and maintenance
        preventativeBOPMaintenanceCost : float
          cost of BOP preventative operations and maintenance
        correctiveMaintenanceCost : float
          cost of corrective operations and maintenance
        correctiveTurbineMaintenanceCost : float
          cost of wind turbine corrective operations and maintenance
        correctiveBOPMaintenanceCost : float
          cost of BOP corrective operations and maintenance
        fixedOMCost : float
          fixed operational costs
        landLeaseCost : float
          cost of land leases
        otherFixedCost : float
          other fixed operational costs 
        """
        super(PlantOM, self).__init__()

        # self.add('turbine', Turbine())                # TODO - for put side, not sure if plant and turbine should be coupled since different assemblies providing different pieces of put

    def printVT(self):
        """ Prints Variable Tree """
        
        print "Plant O&M cost puts:"
        print "totalOMcost| USD| %f" %self.totalOMCost
        print " preventativeMaintenanceCost| USD| %f" %self.preventativeMaintenanceCost
        print "   preventativeTurbineMaintenanceCost| USD| %f" %self.preventativeTurbineMaintenanceCost
        print "   preventativeBOPMaintenanceCost| USD| %f" %self.preventativeBOPMaintenanceCost
        print " correctiveMaintenanceCost| USD| %f" %self.correctiveMaintenanceCost
        print "   correctiveTurbineMaintenanceCost| USD| %f" %self.correctiveTurbineMaintenanceCost
        print "   correctiveBOPMaintenanceCost| USD| %f" %self.correctiveBOPMaintenanceCost
        print " landLeaseCost| USD| %f" %self.landLeaseCost

    def fwriteVT(self, fwritef):
        """ Prints Variable tree to file 
        
        Parameters
        ----------
        fwritef : file
          file for variable tree print out
        """
        
        if fwritef.closed == True:
            # TODO: raise an error
            pass

        fwritef.write("Plant O&M cost puts:| \n")
        fwritef.write("totalOMcost| USD| %f \n" %self.totalOMCost)
        fwritef.write(" preventativeMaintenanceCost| USD| %f \n" %self.preventativeMaintenanceCost)
        fwritef.write("   preventativeTurbineMaintenanceCost| USD| %f \n" %self.preventativeTurbineMaintenanceCost)
        fwritef.write("   preventativeBOPMaintenanceCost| USD| %f \n" %self.preventativeBOPMaintenanceCost)
        fwritef.write(" correctiveMaintenanceCost| USD| %f \n" %self.correctiveMaintenanceCost)
        fwritef.write("   correctiveTurbineMaintenanceCost| USD| %f \n" %self.correctiveTurbineMaintenanceCost)
        fwritef.write(" correctiveBOPMaintenanceCost| USD| %f \n" %self.correctiveBOPMaintenanceCost)
        fwritef.write(" landLeaseCost| USD| %f \n" %self.landLeaseCost)
    

