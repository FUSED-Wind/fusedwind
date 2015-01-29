
import glob
import numpy as np
from string import digits

from openmdao.main.api import Component, Assembly
from openmdao.lib.datatypes.api import VarTree, Float, Array, Bool, Str, List, Int

from fusedwind.turbine.geometry_vt import BladeSurfaceVT, BladePlanformVT
from fusedwind.turbine.geometry import RedistributedBladePlanform, SplineComponentBase, FFDSplineComponentBase
from fusedwind.turbine.structure_vt import BladeStructureVT3D, CrossSectionStructureVT, BeamStructureVT
from fusedwind.turbine.rotoraero_vt import LoadVectorCaseList
from fusedwind.interface import base, implement_base


@base
class BladeStructureReaderBase(Component):

    st3d = VarTree(BladeStructureVT3D(), iotype='out',
                                         desc='Vartree containing discrete definition of blade structure')


@base
class BladeStructureWriterBase(Component):

    st3d = VarTree(BladeStructureVT3D(), iotype='in',
                                         desc='Vartree containing discrete definition of blade structure')


@base
class ModifyBladeStructureBase(Component):

    st3dIn = VarTree(BladeStructureVT3D(), iotype='in',
                                         desc='Vartree containing initial discrete definition of blade structure')
    st3dOut = VarTree(BladeStructureVT3D(), iotype='out',
                                         desc='Vartree containing modified discrete definition of blade structure')


@implement_base(BladeStructureReaderBase)
class BladeStructureReader(Component):
    """
    input file reader of BladeStructureVT3D data
    """

    filebase = Str(iotype='in')

    st3d = VarTree(BladeStructureVT3D(), iotype='out',
                                         desc='Vartree containing discrete definition of blade structure')

    def execute(self):

        self.read_layups()
        self.read_materials()

    def read_materials(self):

        fid = open(self.filebase + '.mat', 'r')
        materials = fid.readline().split()[1:]
        data = np.loadtxt(fid)
        for i, name in enumerate(materials):
            mat = self.st3d.add_material(name)
            try:
                d = data[i, :]
            except:
                d = data
            mat.E1 = d[0]
            mat.E2 = d[1]
            mat.E3 = d[2]
            mat.nu12 = d[3]
            mat.nu13 = d[4]
            mat.nu23 = d[5]
            mat.G12 = d[6]
            mat.G13 = d[7]
            mat.G23 = d[8]
            mat.rho = d[9]

        failcrit = {1:'maximum_strain', 2:'maximum_stress', 3:'tsai_wu'}
        fid = open(self.filebase + '.failmat', 'r')
        materials = fid.readline().split()[1:]
        data = np.loadtxt(fid)
        for i, name in enumerate(materials):
            mat = self.st3d.add_material(name)
            try:
                d = data[i, :]
            except:
                d = data
            mat.failure_criterium = failcrit[int(d[0])]
            mat.s11_t = d[1]
            mat.s22_t = d[2]
            mat.s33_t = d[3]
            mat.s11_c = d[4]
            mat.s22_c = d[5]
            mat.s33_c = d[6]
            mat.t12 = d[7]
            mat.t13 = d[8]
            mat.t23 = d[9]
            mat.e11_c = d[10]
            mat.e22_c = d[11]
            mat.e33_c = d[12]
            mat.e11_t = d[13]
            mat.e22_t = d[14]
            mat.e33_t = d[15]
            mat.g12 = d[16]
            mat.g13 = d[17]
            mat.g23 = d[18]
            mat.gM0 = d[19]
            mat.C1a = d[20]
            mat.C2a = d[21]
            mat.C3a = d[22]
            mat.C4a = d[23]

    def read_layups(self):
        """
        dp3d data format:

        # web00 web01\n
        <DP index0> <DP index1>\n
        <DP index0> <DP index0>\n
        # s DP00  DP01  DP02  DP03  DP04  DP05\n
        <float> <float> <float> <float> ... <float>\n
        .       .       .       .           .\n
        .       .       .       .           .\n
        .       .       .       .           .\n

        st3d data format:\n

        # region00\n
        # s    triax    uniax    core    uniax01    triax01    core01\n
        <float> <float> <float> <float> <float> <float> <float>\n
        .       .       .       .       .       .       .\n
        .       .       .       .       .       .       .\n
        .       .       .       .       .       .       .\n
        """

        self.dp_files = glob.glob(self.filebase + '*.dp3d')

        self.layup_files = glob.glob(self.filebase + '*.st3d')

        for dpfile in self.dp_files:
            self._logger.info('reading dp_file: %s' % dpfile)
            dpfid = open(dpfile, 'r')
            
            # read webs 
            wnames = dpfid.readline().split()[1:]
            iwebs = []
            for w, wname in enumerate(wnames):
                line = dpfid.readline().split()[1:]
                line = [int(entry) for entry in line]
                iwebs.append(line)
            nwebs = len(iwebs)
            header = dpfid.readline()
            dpdata = np.loadtxt(dpfile)
            nreg = dpdata.shape[1] - 2

            try:
                regions = header.split()[1:]
                assert len(regions) == nreg

            except:
                regions = ['region%02d' % i for i in range(nreg)]

            self.st3d.configure_regions(nreg, names=regions)
            self.st3d.configure_webs(len(wnames), iwebs, names=wnames)
            self.st3d.x = dpdata[:, 0]

            self.st3d.DP00 = dpdata[:, 1]

            for i, rname in enumerate(regions):
                r = getattr(self.st3d, rname)
                self._logger.info('  adding region: %s' % rname)

                dpname = 'DP%02d' % (i + 1)
                setattr(self.st3d, dpname, dpdata[:, i + 2])
        
                layup_file = '_'.join([self.filebase, rname]) + '.st3d'
                self._logger.info('  reading layup file %s' % layup_file)
                fid = open(layup_file, 'r')
                rrname = fid.readline().split()[1]
                lheader = fid.readline().split()[1:]

                cldata = np.loadtxt(fid)
                layers = lheader[1:]
                nl = len(lheader)

                s = cldata[:, 0]
                r.thickness = np.zeros(self.st3d.x.shape[0])
                for il, lname in enumerate(layers):
                    self._logger.info('    adding layer %s' % lname)
                    l = r.add_layer(lname)
                    l.thickness = cldata[:, il + 1]
                    r.thickness += l.thickness
                    try:
                        l.angle = cldata[:, il + 1 + nl]
                    except:
                        l.angle = np.zeros(s.shape[0])

            for i, rname in enumerate(wnames):
                r = getattr(self.st3d, rname)
                self._logger.info('  adding web: %s' % rname)
        
                layup_file = '_'.join([self.filebase, rname]) + '.st3d'
                self._logger.info('  reading layup file %s' % layup_file)
                fid = open(layup_file, 'r')
                rrname = fid.readline().split()[1]
                lheader = fid.readline().split()[1:]

                cldata = np.loadtxt(fid)
                layers = lheader[1:]
                nl = len(lheader)

                r.thickness = np.zeros(self.st3d.x.shape[0])
                # assert len(lheader) == cldata.shape[1]

                s = cldata[:, 0]
    
                for il, lname in enumerate(layers):
                    self._logger.info('    adding layer %s' % lname)
                    l = r.add_layer(lname)
                    l.thickness = cldata[:, il + 1]
                    r.thickness += l.thickness
                    try:
                        l.angle = cldata[:, il + 1 + nl]
                    except:
                        l.angle = np.zeros(s.shape[0])


@implement_base(BladeStructureWriterBase)
class BladeStructureWriter(Component):
    """
    input file writer of BladeStructureVT3D data
    """

    filebase = Str('blade', iotype='in')
    st3d = VarTree(BladeStructureVT3D(), iotype='in')

    def execute(self):

        try:
            if '-fd' in self.itername or '-fd' in self.parent.itername:
                return
            else:
                self.fbase = self.filebase + '_' + str(self.exec_count)
        except:
            self.fbase = self.filebase
        self.fbase = self.filebase

        self.write_layup_data()
        self.write_materials()

    def write_materials(self):

        fid = open(self.fbase + '.mat', 'w')
        fid.write('# %s\n' % (' '.join(self.st3d.materials.keys())))
        fid.write('# E1 E2 E3 nu12 nu13 nu23 G12 G13 G23 rho\n')
        matdata = []
        for name, mat in self.st3d.materials.iteritems():
            data = np.array([mat.E1,
                             mat.E2,
                             mat.E3, 
                             mat.nu12,
                             mat.nu13,
                             mat.nu23,
                             mat.G12,
                             mat.G13,
                             mat.G23,
                             mat.rho]) 
            matdata.append(data)

        np.savetxt(fid, np.asarray(matdata))

        failcrit = dict(maximum_strain=1, maximum_stress=2, tsai_wu=3)
        fid = open(self.fbase + '.failmat', 'w')
        fid.write('# %s\n' % (' '.join(self.st3d.materials.keys())))
        fid.write('# failcrit s11_t s22_t s33_t s11_c s22_c s33_c'
                  't12 t13 t23 e11_c e22_c e33_c e11_t e22_t e33_t g12 g13 g23'
                  'gM0 C1a C2a C3a C4a\n')
        matdata = []
        for name, mat in self.st3d.materials.iteritems():
            data = np.array([failcrit[mat.failure_criterium],
                             mat.s11_t,
                             mat.s22_t,
                             mat.s33_t, 
                             mat.s11_c,
                             mat.s22_c,
                             mat.s33_c,
                             mat.t12,
                             mat.t13,
                             mat.t23,
                             mat.e11_c,
                             mat.e22_c,
                             mat.e33_c,
                             mat.e11_t,
                             mat.e22_t,
                             mat.e33_t,
                             mat.g12,
                             mat.g13,
                             mat.g23,
                             mat.gM0,
                             mat.C1a,
                             mat.C2a,
                             mat.C3a,
                             mat.C4a])
            matdata.append(data)
        fmt = '%i ' + ' '.join(23*['%.20e'])
        np.savetxt(fid, np.asarray(matdata), fmt=fmt)

    def write_layup_data(self):

        DPs = []
        
        fid1 = open(self.fbase + '.dp3d', 'w')
        fid1.write('# %s\n' % ('  '.join(self.st3d.webs)))
        for web in self.st3d.iwebs:
            fid1.write('# %i %i\n' % (web[0], web[1]))
        fid1.write('# s %s\n' % ('  '.join(self.st3d.DPs)))
        DPs.append(self.st3d.x)
        for i, rname in enumerate(self.st3d.regions):
            
            self._logger.info('  writing region: %s' % rname)
            reg = getattr(self.st3d, rname)
            
            DP = getattr(self.st3d, 'DP%02d' % (i))
            DPs.append(DP)
            
            fname = '_'.join([self.fbase, rname]) + '.st3d'
            fid = open(fname, 'w')
            lnames = '    '.join(reg.layers)
            fid.write('# %s\n' % rname)
            fid.write('# s    %s\n' % lnames)
            data = []
            data.append(self.st3d.x)
            for lname in reg.layers:
                self._logger.info('    writing layer: %s' % lname)
                layer = getattr(reg, lname)
                data.append(layer.thickness)
            for lname in reg.layers:
                self._logger.info('    writing layer: %s' % lname)
                layer = getattr(reg, lname)
                data.append(layer.angle)
            data = np.asarray(data).T
            np.savetxt(fid, data)
            fid.close()
        DPs.append(getattr(self.st3d, 'DP%02d' % (i + 1)))
        DPs = np.asarray(DPs).T
        np.savetxt(fid1, DPs)
        for i, wname in enumerate(self.st3d.webs):
            
            self._logger.info('  writing web: %s' % rname)
            reg = getattr(self.st3d, wname)
            fname = '_'.join([self.fbase, wname]) + '.st3d'
            fid = open(fname, 'w')
            lnames = '    '.join(reg.layers)
            fid.write('# %s\n' % wname)
            fid.write('# s    %s\n' % lnames)
            data = []
            data.append(self.st3d.x)
            for lname in reg.layers:
                self._logger.info('    writing layer: %s' % lname)
                layer = getattr(reg, lname)
                data.append(layer.thickness)
            for lname in reg.layers:
                self._logger.info('    writing layer: %s' % lname)
                layer = getattr(reg, lname)
                data.append(layer.angle)
            data = np.asarray(data).T
            np.savetxt(fid, data)
            fid.close()


@base
class BeamStructureReaderBase(Component):

    beamprops = VarTree(BeamStructureVT(), iotype='out')


@implement_base(BeamStructureReaderBase)
class BeamStructureReader(Component):
    """
    Default reader for a beam structure file.
    """

    st_filename = Str(iotype='in')
    beamprops = VarTree(BeamStructureVT(), iotype='out')

    def execute(self):
        """  
        The format of the file should be:
        main_s[0] dm[1] x_cg[2] y_cg[3] ri_x[4] ri_y[5] x_sh[6] y_sh[7] E[8] ...\n
        G[9] I_x[10] I_y[11] K[12] k_x[13] k_y[14] A[15] pitch[16] x_e[17] y_e[18]

        Sub-classes can overwrite this function to change the reader's behaviour.
        """
        print 'reading blade structure'
        if self.st_filename is not '':
            try: 
                st_data = np.loadtxt(self.st_filename)
            except:
                raise RuntimeError('Error reading file %s, %s'% (self.st_filename))

        if st_data.shape[1] < 19:
            raise RuntimeError('Blade planform data: expected dim = 10, got dim = %i,%s'%(st_data.shape[1]))

        self.beamprops.s = st_data[:, 0]
        self.beamprops.dm = st_data[:, 1]
        self.beamprops.x_cg = st_data[:, 2]
        self.beamprops.y_cg = st_data[:, 3]
        self.beamprops.ri_x = st_data[:, 4]
        self.beamprops.ri_y = st_data[:, 5]
        self.beamprops.x_sh = st_data[:, 6]
        self.beamprops.y_sh = st_data[:, 7]
        self.beamprops.E = st_data[:, 8]
        self.beamprops.G = st_data[:, 9]
        self.beamprops.I_x = st_data[:, 10]
        self.beamprops.I_y = st_data[:, 11]
        self.beamprops.J = st_data[:, 12]
        self.beamprops.k_x = st_data[:, 13]
        self.beamprops.k_y = st_data[:, 14]
        self.beamprops.A = st_data[:, 15]
        self.beamprops.pitch = st_data[:, 16]
        self.beamprops.x_e = st_data[:, 17]
        self.beamprops.y_e = st_data[:, 18]


@implement_base(ModifyBladeStructureBase)
class SplinedBladeStructure(Assembly):
    """
    Class for building a complete spline parameterized
    representation of the blade structure.

    Outputs a BladeStructureVT3D vartree with a discrete
    representation of the structural geometry.

    Interface with a BladeStructureBuilder class for generating code specific
    inputs.
    """

    x = Array(iotype='in', desc='spanwise resolution of blade')
    span_ni = Int(20, iotype='in', desc='Number of discrete points along span')
    nC = Int(8, iotype='in', desc='Number of spline control points along span')
    Cx = Array(iotype='in', desc='spanwise distribution of spline control points')
    st3dIn = VarTree(BladeStructureVT3D(), iotype='in',
                                         desc='Vartree containing initial discrete definition of blade structure')
    st3dOut = VarTree(BladeStructureVT3D(), iotype='out',
                                         desc='Vartree containing re-splined discrete definition of blade structure')

    def __init__(self):
        """
        initialize the blade structure

        parameters
        -----------
        nsec: int
            total number of sections in blade
        """
        super(SplinedBladeStructure, self).__init__()

        self._nsec = 0

        self.add('pf', RedistributedBladePlanform())
        self.driver.workflow.add('pf')
        self.create_passthrough('pf.pfIn')
        self.create_passthrough('pf.pfOut')
        self.connect('x', 'pf.x')

    def configure_bladestructure(self):
        """
        method for trawling through the st3dIn vartree
        and initializing all spline curves in the assembly
        """

        if self.x.shape[0] == 0:
            self.x = np.linspace(0, 1, self.span_ni)
        else:
            self.span_ni = self.x.shape[0]
        if self.Cx.shape[0] == 0:
            self.Cx = np.linspace(0, 1, self.nC)
        else:
            self.nC = self.Cx.shape[0]

        self.st3dOut = self.st3dIn.copy()
        self.connect('x', 'st3dOut.x')

        sec = self.st3dIn
        nr = len(sec.regions)
        for ip in range(nr + 1):
            dpname = 'DP%02d' % ip
            # division point spline
            DPc = self.add(dpname, FFDSplineComponentBase(self.nC))
            self.driver.workflow.add(dpname)
            # DPc.log_level = logging.DEBUG
            x = getattr(sec, 'x')
            DP = getattr(sec, dpname)
            self.connect('x', '%s.x' % dpname)
            self.connect('Cx', dpname + '.Cx')
            DPc.xinit = x
            DPc.Pinit = DP
            self.connect(dpname + '.P', '.'.join(['st3dOut', dpname]))
            self.create_passthrough(dpname + '.C', alias=dpname + '_C')
            # regions
            if ip < nr:
                rname = 'region%02d' % ip
                region = getattr(sec, rname)
                for lname in region.layers:
                    layer = getattr(region, lname)
                    lcname = 'r%02d%s' % (ip, lname)
                    # thickness spline
                    lcomp = self.add(lcname+'T', FFDSplineComponentBase(self.nC))
                    self.driver.workflow.add(lcname+'T')
                    # lcomp.log_level = logging.DEBUG
                    self.connect('x', '%s.x' % (lcname + 'T'))
                    lcomp.xinit = sec.x
                    lcomp.Pinit = layer.thickness
                    self.connect('Cx', lcname+'T' + '.Cx')
                    self.connect('%sT.P'%lcname, '.'.join(['st3dOut', rname, lname, 'thickness']))
                    # angle spline
                    lcomp = self.add(lcname+'A', FFDSplineComponentBase(self.nC))
                    self.driver.workflow.add(lcname+'A')
                    # lcomp.log_level = logging.DEBUG
                    self.connect('x', '%s.x' % (lcname + 'A'))
                    self.create_passthrough(lcname+'T' + '.C', alias=lcname+'T' + '_C')
                    lcomp.xinit = sec.x
                    lcomp.Pinit = layer.angle
                    self.connect('Cx', lcname+'A' + '.Cx')
                    self.connect('%sA.P'%lcname, '.'.join(['st3dOut', rname, lname, 'angle']))
                    self.create_passthrough(lcname+'A' + '.C', alias=lcname+'A' + '_C')
        # shear webs
        for wname in sec.webs:
            web = getattr(sec, wname)
            for lname in web.layers:
                layer = getattr(web, lname)
                lcname = '%s%s' % (wname, lname)
                # thickness spline
                lcomp = self.add(lcname+'T', FFDSplineComponentBase(self.nC))
                # lcomp.log_level = logging.DEBUG
                self.driver.workflow.add(lcname+'T')
                self.connect('x', '%s.x' % (lcname + 'T'))
                lcomp.xinit = sec.x
                lcomp.Pinit = layer.thickness
                self.connect('Cx', lcname+'T' + '.Cx')
                self.connect('%sT.P'%lcname, '.'.join(['st3dOut', wname, lname, 'thickness']))
                self.create_passthrough(lcname+'T' + '.C', alias=lcname+'T' + '_C')
                # angle spline
                lcomp = self.add(lcname+'A', FFDSplineComponentBase(self.nC))
                # lcomp.log_level = logging.DEBUG
                self.driver.workflow.add(lcname+'A')
                self.connect('x', '%s.x' % (lcname + 'A'))
                lcomp.xinit = sec.x
                lcomp.Pinit = layer.angle
                self.connect('Cx', lcname+'A' + '.Cx')
                self.connect('%sA.P'%lcname, '.'.join(['st3dOut', wname, lname, 'angle']))
                self.create_passthrough(lcname+'A' + '.C', alias=lcname+'A' + '_C')
        
        # copy materials to output VT
        self.st3dOut.materials = self.st3dIn.materials.copy()



    def _post_execute(self):
        """
        update all thicknesses and region widths
        """
        super(SplinedBladeStructure, self)._post_execute()

        for i, rname in enumerate(self.st3dOut.regions):
            region = getattr(self.st3dOut, rname)
            DP0 = getattr(self.st3dOut, 'DP%02d' % i)
            DP1 = getattr(self.st3dOut, 'DP%02d' % (i + 1))
            width = DP1 - DP0
            for ix in range(width.shape[0]):
                if width[ix] < 0.:
                    DPt = DP0[ix]
                    DP0[ix] = DP1[ix]
                    DP1[ix] = DPt
                    width[ix] *= -1.
                    self._logger.warning('switching DPs %i %i for section %i' %
                                         (i, i + 1, ix))
            region.width = width * self.pf.pfOut.chord * self.pfOut.blade_length
            region.thickness = np.zeros(self.st3dOut.x.shape)
            for layer in region.layers:
                region.thickness += np.maximum(0., getattr(region, layer).thickness)

        for i, rname in enumerate(self.st3dOut.webs):
            region = getattr(self.st3dOut, rname)
            region.thickness = np.zeros(self.st3dOut.x.shape)
            for layer in region.layers:
                region.thickness += np.maximum(0., getattr(region, layer).thickness)


@base
class BladeStructureBuilderBase(Component):
    """
    base class for components that can interpret the BladeStructure3DVT
    vartree and generate input for specific types of codes.
    """

    surface = VarTree(BladeSurfaceVT(), iotype='in', desc='Stacked blade surface object')
    st3d = VarTree(BladeStructureVT3D(), iotype='in', desc='Blade structure definition')

    def execute(self):

        raise NotImplementedError('%s.execute needs to be overwritten by derived classes' % self.get_pathname())

    def get_material(self, name):
        """
        retrieve a material by its name
        
        parameters
        ----------
        name: string
            name of material

        returns
        -------
        mat: object
            MaterialProps VariableTree object
        """

        # strip integers from name to be safe
        st = ''.join(i for i in name if i.isalpha())
        try:
            return self.st3d.materials[st]
        except:
            return None


@implement_base(BladeStructureBuilderBase)
class BladeStructureCSBuilder(BladeStructureBuilderBase):
    """
    Class that generates a series of 2D cross-sectional property
    vartrees (CrossSectionStructureVT) used by structural codes like BECAS
    """

    blade_length = Float(1., iotype='in')
    surface = VarTree(BladeSurfaceVT(), iotype='in', desc='Stacked blade surface object')
    st3d = VarTree(BladeStructureVT3D(), iotype='in', desc='Blade structure definition')

    cs2d = List(iotype='out', desc='List of cross-sectional properties'
                                         'vartrees')

    def execute(self):
        """
        generate cross sections at every spanwise node of the st3d vartree
        """

        # clear list of outputs!
        self.cs2d = []

        ni = self.st3d.x.shape[0]
        for i in range(ni):
            x = self.st3d.x[i]
            # print 'adding section at r/R = %2.2f' % x 
            st2d = CrossSectionStructureVT()
            st2d.s = x * self.blade_length
            st2d.DPs = []
            try:
                airfoil = self.surface.interpolate_profile(x)[:, [0, 1]] * self.blade_length
                st2d.airfoil.initialize(airfoil)
            except:
                pass
            for ir, rname in enumerate(self.st3d.regions):
                reg = getattr(self.st3d, rname)
                if reg.thickness[i] == 0.:
                    print 'zero thickness region!', rname
                    # continue
                DP0 = getattr(self.st3d, 'DP%02d' % ir)
                DP1 = getattr(self.st3d, 'DP%02d' % (ir + 1))
                r = st2d.add_region(rname.upper())
                st2d.DPs.append(DP0[i])
                r.s0 = DP0[i]
                r.s1 = DP1[i]
                for lname in reg.layers:
                    lay = getattr(reg, lname)
                    if lay.thickness[i] > 1.e-5: 
                        l = r.add_layer(lname)
                        # try:
                        lnamebase = lname.translate(None, digits)
                        st2d.add_material(lnamebase, self.get_material(lname).copy())
                        # except:
                            # raise RuntimeError('Material %s not in materials list' % lname)
                        l.materialname = lnamebase
                        l.thickness = max(0., lay.thickness[i])
                        try:
                            l.angle = lay.angle[i]
                        except:
                            l.angle = 0.

            st2d.DPs.append(DP1[i])
            for ir, rname in enumerate(self.st3d.webs):
                reg = getattr(self.st3d, rname)
                if reg.thickness[i] == 0.:
                    continue
                r = st2d.add_web(rname.upper())
                try:
                    DP0 = getattr(self.st3d, 'DP%02d' % self.st3d.iwebs[ir][0])
                except:
                    DP0 = getattr(self.st3d, 'DP%02d' % (len(self.st3d.regions) + self.st3d.iwebs[ir][0] + 1))
                try:
                    DP1 = getattr(self.st3d, 'DP%02d' % self.st3d.iwebs[ir][1])
                except:
                    DP1 = getattr(self.st3d, 'DP%02d' % (len(self.st3d.regions) + self.st3d.iwebs[ir][1] + 1))
                r.s0 = DP0[i] 
                r.s1 = DP1[i]
                for lname in reg.layers:
                    lay = getattr(reg, lname)
                    if lay.thickness[i] > 1.e-5:
                        l = r.add_layer(lname)
                        try:
                            lnamebase = lname.translate(None, digits)
                            st2d.add_material(lnamebase, self.get_material(lname).copy())
                        except:
                            raise RuntimeError('Material %s not in materials list' % lname)
                        l.materialname = lnamebase
                        l.thickness = max(0., lay.thickness[i])
                        try:
                            l.angle = lay.angle[i]
                        except:
                            l.angle = 0.

            self.cs2d.append(st2d)


@base
class BeamStructureCSCode(Component):
    """
    Base class for computing beam structural properties using a cross-sectional
    code such as PreComp, BECAS or VABS.

    The analysis assumes that the list of CrossSectionStructureVT's and the
    BladePlanformVT are interpolated onto the structural grid, and that
    the code itself is responsible for the meshing of the cross sections.
    """

    cs2d = List(CrossSectionStructureVT, iotype='in', desc='Blade cross sectional structure geometry')
    pf = VarTree(BladePlanformVT(), iotype='in', desc='Blade planform discretized according to'
                                                      'the structural resolution')

    beam_structure = VarTree(BeamStructureVT(), iotype='out', desc='Structural beam properties')


@base
class StressRecoveryCSCode(Component):
    """
    Base class for performing cross sectional failure analysis
    using codes like BECAS and VABS.

    This analysis will typically be in a workflow preceeded by
    a call to a BeamStructureCSCode. It is assumed that the list of
    LoadVectorCaseList vartrees are interpolated onto the structural grid.

    Note that the failure criterium and material safety factors are specified
    for each individual material in the MaterialProps variable tree.
    """

    load_cases = List(LoadVectorCaseList, iotype='in', 
                           desc='List of lists of section load vectors for each radial section'
                                'used to perform failure analysis')

    failure = Array(iotype='out', desc='Failure parameter. Shape: ((len(load_cases), n_radial_sections))')

