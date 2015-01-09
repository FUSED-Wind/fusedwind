
from fusedwind.interface import base, implement_base


def configure_bladesurface(cls, planform_nC):
    """
    method that adds a ``LoftedBladeSurface`` instance to the assembly

    Parameters
    ----------
    cls: class instance
        Instance of an OpenMDAO Assembly that the analysis is run from
    planform_nC: int
        number of spline control points for the planform variables
    """

    from fusedwind.turbine.geometry import SplinedBladePlanform, LoftedBladeSurface

    cls.add('pf_splines', SplinedBladePlanform())
    cls.add('blade_surface', LoftedBladeSurface())

    cls.driver.workflow.add(['pf_splines','blade_surface'])

    cls.create_passthrough('pf_splines.blade_length')
    cls.create_passthrough('pf_splines.span_ni')

    cls.connect('pf_splines.pfOut', 'blade_surface.pf')
    cls.connect('span_ni', 'blade_surface.span_ni')
    cls.pf_splines.nC = planform_nC

def configure_bladestructure(cls, file_base, planform_nC=8, structure_nC=8):
    """
    method for configuring an assembly with 
    blade geometry and structural parameterization
    of a blade.

    Parameters
    ----------
    cls: class instance
        Instance of an OpenMDAO Assembly that the analysis is run from
    file_base: str
        path + filebase to the blade structure files, e.g. data/DTU10MW
    planform_nC: int
        number of spline control points for the planform variables
    structure_nC: int
        number of spline control points for the structural variables
    """

    if not hasattr(cls, 'blade_surface'):
        configure_bladesurface(cls, planform_nC)

    from fusedwind.turbine.blade_structure import BladeStructureReader, \
                                                  BladeStructureWriter, \
                                                  SplinedBladeStructure, \
                                                  BladeStructureCSBuilder

    cls.add('st_reader', BladeStructureReader())
    cls.add('st_splines', SplinedBladeStructure())
    cls.add('st_builder', BladeStructureCSBuilder())
    cls.add('st_writer', BladeStructureWriter())

    cls.driver.workflow.add(['st_splines',
                             'st_builder', 
                             'st_writer'])

    cls.connect('blade_surface.pf', 'st_splines.pfIn')
    cls.connect('blade_length', 'st_builder.blade_length')
    # connect the blade structure vartrees through the chain
    # of components
    cls.connect('st_splines.st3dOut', 'st_builder.st3d')
    cls.connect('st_splines.st3dOut', 'st_writer.st3d')

    # connect the stacked blade surface to the st_builder component
    cls.connect('blade_surface.surfnorot', 'st_builder.surface')

    cls.st_reader.filebase = file_base
    cls.st_reader.execute()

    cls.st_splines.st3dIn = cls.st_reader.st3d.copy()
    cls.st_splines.nC = structure_nC
    cls.st_splines.configure_bladestructure()
