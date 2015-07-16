
import numpy as np
from openmdao.main.api import Component
from openmdao.lib.datatypes.api import List, Array, VarTree, Float, Str

from fusedwind.interface import base, implement_base
from fusedwind.turbine.rotoraero_vt import LoadVectorArray, LoadVectorArrayCaseList, LoadVectorCaseList


@base
class LoadCaseReaderBase(Component):
    """
    base for reading load case data
    """

    load_cases = VarTree(LoadVectorArrayCaseList(), iotype='out', desc='Load case arrays')


@implement_base(LoadCaseReaderBase)
class LoadCaseReader(Component):

    case_files = List(iotype='in', desc='List of load case files')
    case_filter = List(iotype='in', desc='List of cases indices to include, if empty all are used')
    blade_length = Float(86.366, iotype='in')

    load_cases = VarTree(LoadVectorArrayCaseList(), iotype='out', desc='Load case arrays')

    def execute(self):

        for name in self.case_files:
            fid = open(name, 'r')
            case_id = fid.readline().split()[1]
            data = np.loadtxt(fid)
            lc = LoadVectorArray()
            lc._fromarray(data)
            self.load_cases.cases.append(lc.copy())


@implement_base(LoadCaseReaderBase)
class DTU10MWLoadCaseReader(Component):
    """
    reads the published DTU 10MW extreme load tables into a LoadVectorCaseArray

    The DTU 10MW RWT extreme load cases are written as one file per
    radial section with rows of cases with the following header

    ## ##############################################
    ## Section 001 at r=2.8 m
    ## ##############################################
    """

    case_files = List(iotype='in', desc='List of load case files')
    case_filter = List(iotype='in', desc='List of cases indices to include, if empty all are used')
    blade_length = Float(86.366, iotype='in')

    load_cases = VarTree(LoadVectorArrayCaseList(), iotype='out', desc='Load case arrays')

    def execute(self):

        rdata = []

        r = []
        for name in self.case_files:
            fid = open(name, 'r')
            fid.readline()
            radius = fid.readline().split()[4]
            radius = float(radius.strip('r='))
            r.append(radius)
            fid.readline()
            rdata.append(np.loadtxt(fid))

        isort = np.argsort(r)
        r = np.asarray(r)[isort]
        r = (r - r[0]) / self.blade_length
        rdata = np.asarray(rdata)[isort]

        if len(self.case_filter) == 0:
            self.case_filter = range(rdata.shape[1])

        for i in self.case_filter:
            c = np.zeros((rdata.shape[0], 9))
            c[:, 0] = r
            c[:, 1:] = rdata[:, i, :] * 1.e6
            v = LoadVectorArray()
            try:
                v.case_id = cases[i]
            except:
                v.case_id = 'case%03d' % i
            v._fromarray(c)
            self.load_cases.cases.append(v)


class LoadCaseInterpolator(Component):
    """
    interpolates in a LoadVectorCaseArray at given radial positions
    """

    s = Array(iotype='in', desc='radial positions to interpolate load cases onto')
    lcIn = VarTree(LoadVectorArrayCaseList(), iotype='in', desc='Load case arrays')

    lcOut = List(LoadVectorCaseList, iotype='out', desc='List of 2D cases interpolated onto s')

    def execute(self):

        self.lcOut = []
        for i, s in enumerate(self.s):
            self.lcOut.append(self.lcIn._interp_s(s))


class LoadCaseWriter(Component):

    file_base = Str('extreme_loads', iotype='in')
    load_cases = VarTree(LoadVectorArrayCaseList(), iotype='in', desc='Load case arrays')

    def execute(self):

        for i, case in enumerate(self.load_cases.cases):

            fid = file(self.file_base + '%03d.dat' % i, 'w')
            fid.write('# %s\n' % case.case_id)
            lc2d = case._toarray()
            np.savetxt(fid, lc2d[:, :])

