# KLD: _cost model for FUSED_Wind - most basic structure

from openmdao.lib.datatypes.api import Float, Int, Array, VarTree
from openmdao.main.api import Component, Assembly, VariableTree

from fusedwind.interface import base, implement_base

#####################################################################################
# Plant OPEX Models

# OPEX Model Variable Trees, Components and Assemblies
@base
class BaseOPEXAggregator(Component):

    # Outputs
    avg_annual_opex = Float(iotype='out', desc='Average annual Operating Expenditures for a wind plant over its lifetime')

@base
class BaseOPEXModel(Assembly):
    """
    Framework for a balance of station cost model
    """
    # Outputs
    avg_annual_opex = Float(iotype='out', desc='Average annual Operating Expenditures for a wind plant over its lifetime')
    
def configure_base_opex(assembly):
    
    assembly.add('opex', BaseOPEXAggregator())
    
    assembly.driver.workflow.add('opex')

    assembly.connect('opex.avg_annual_opex','avg_annual_opex')

# Extended Variable Trees, Components and Assemblies
@base
class OPEXVarTree(VariableTree):

    preventative_opex = Float(desc='annual expenditures on preventative maintenance - BOP and turbines')
    corrective_opex = Float(desc='annual unscheduled maintenance costs (replacements) - BOP and turbines')
    lease_opex = Float(desc='annual lease expenditures')
    other_opex = Float(desc='other operational expenditures such as fixed costs')

@implement_base(BaseOPEXAggregator)
class ExtendedOPEXAggregator(Component):

    # Outputs
    avg_annual_opex = Float(iotype='out', desc='Average annual Operating Expenditures for a wind plant over its lifetime')
    opex_breakdown = VarTree(OPEXVarTree(),iotype='out')

@implement_base(BaseOPEXModel)
class ExtendedOPEXModel(Assembly):

    # Outputs
    avg_annual_opex = Float(iotype='out', desc='Average annual Operating Expenditures for a wind plant over its lifetime')
    opex_breakdown = VarTree(OPEXVarTree(),iotype='out')

def configure_extended_opex(assembly):
	  
	  configure_base_opex(assembly)
	  
	  assembly.replace('opex', ExtendedOPEXAggregator())
	  
	  assembly.connect('opex.opex_breakdown','opex_breakdown')


# Full OPEX Variable Trees, Components and Assemblies
@implement_base(BaseOPEXAggregator)
class FullOPEXAggregator(Component):
    """
    Framework for an enhanced operations expenditures model that gives a series of annual operating expenditures over the the plants lifetime
    """

    # Outputs
    avg_annual_opex = Float(iotype='out', desc='Average annual Operating Expenditures for a wind plant over its lifetime')
    opex_breakdown = VarTree(OPEXVarTree(),iotype='out')
    annual_opex = Array(iotype='out', desc='Array of annual Operating Expenditure estimates for each year of expected project operation')


########################################################################################
# Plant Decommissioning Specific Models (usually part of CAPEX or OPEX)

# DECOMEX Model
class BaseDECOMEXModel(Assembly):
    """
    Framework for a decomissioning expenditures model for plant end of life
    """

    # Outputs
    decomex = Float(iotype='out', desc='General DECOMEX model produces Decomissioning Expenditures for a wind plant for the end of its life')