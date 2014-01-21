import numpy as np
from math import pi
import copy


class RunCaseBuilder(object):
    """ base class for run case builders.  only one we have is FAST 
    single aerodcode run.
    Anything in common to build toward here ??? 
    We want to push anything that is not specific to a certain aerocode to be set up here """
    pass

def myfixangle(theta):
    # maybe convert from radians
    # maybe wrap
    # maybe limit range
    v = theta * 180.0 / pi
    if (v < -180):
        v += 360
    if (v > 180):
        v -= 360
    v = max(v,-179.99)
    v = min(v, 179.99)
    return v

def sample2FASTparams(sample):
    """ the key FAST-specific function that converts purported univsersal input 
    variables into a python dictionary that maps 1-to-1 with actual FAST input
    parameters """
    params = {}
    if ('Vhub' in sample):
        w = sample['Vhub']
        blpitch1 = FASTRunCaseBuilder.GetPitch(w)
        rotspeed = FASTRunCaseBuilder.GetRotSpd(w)
        params['RotSpeed'] = rotspeed
        params['BlPitch1'] = blpitch1
        params['BlPitch2'] = blpitch1
        params['BlPitch3'] = blpitch1
            ## these b/c some FAST files (that might be the template) use parens:
        params['BlPitch(1)'] = blpitch1  
        params['BlPitch(2)'] = blpitch1
        params['BlPitch(3)'] = blpitch1
        params['Vhub'] = w
        
    params['TStart'] = 0
    if ('TStart' in sample):
        params['TStart'] = sample['TStart']
    if ('AnalTime' in sample):
       params['TMax'] = params['TStart'] + sample['AnalTime']
        
        # smallest values in case sampling produced bad results
    epsHs = 0.001  # TODO why did I set epsHs to certain value?
    epsTp = 0.001
    if ("Hs" in sample):
        params['WaveHs'] = max(epsHs,sample['Hs'])
    if ("Tp" in sample):
        params['WaveTp'] = max(epsTp,sample['Tp'])

    if ('WaveDir' in sample):
                ## wind-wave misalignment.  for RunIEC.pl, involves changing wave direction AND yaw.
        # but Jason's study just considers misalignment.  I start there, meaning no yaw changes yet
        params['WaveDir'] = myfixangle(sample['WaveDir'])
    return params



class FASTRunCaseBuilder(RunCaseBuilder):
    """ build FAST run case (dict) from generic run case (dict) """
    WSPitch    =   np.array([0.0, 11.0, 12.0, 25.0])
    Pitch      =   np.array([0.0,  0.0,  4.0, 22.0])
    WSRpm      =   np.array([0.0, 10.2, 11.4])
    Rpm        =   np.array([6.0, 9.0, 12.1])
#    Rpm        =   np.array([6.0, 10.0, 12.1])

    ignoreInName =['RotSpeed','BlPitch1','BlPitch2','BlPitch3','BlPitch(1)','BlPitch(2)','BlPitch(3)']

    def __init__(self):
        pass

    @staticmethod
    def GetPitch(ws):
        return np.interp(ws, FASTRunCaseBuilder.WSPitch, FASTRunCaseBuilder.Pitch)

    @staticmethod
    def GetRotSpd(ws):
        return np.interp(ws, FASTRunCaseBuilder.WSRpm, FASTRunCaseBuilder.Rpm)

    @staticmethod
    def buildRunCase_x(x, names, dlc):
        sample = {names[i]:x[i] for i in range(len(x))}

        name = dlc.name
        print "setting up dlc name %s" % name

        params = sample2FASTparams(sample)
        print "got params", params
        print "from sample", sample
        subcase = FASTRunCase(dlc.name, params, sample)
        return subcase


#///////////////////////////////////////////

class RunCase(object):
    """ base class for specific run case (one run) of a specific aero code"""
    def __init__(self, case, generic_sample):
        self.name = case
        self.sample = generic_sample

class FASTRunCase(RunCase):
    """ FAST specific single run of FAST.
    """
    def __init__(self, basename, fst_params, generic_sample):
        super(FASTRunCase,self).__init__(basename, generic_sample)
        self.fst_params = copy.deepcopy(fst_params) # dict of FAST keywords/values to override
        # override name for uniqueness
        for p in fst_params:
            if (p not in FASTRunCaseBuilder.ignoreInName):
                self.name += "%s.%.1f" % (p[0:3],fst_params[p])



#//////////////////////////////////////////////////

class GenericRunCase(object):
    """ Like Run case, but only base key value info
    still one run of aero code, just w.r.t. "universal" variables """
    def __init__(self,casename, param_names, ln):
        self.x = np.array(ln)
        self.param_names = param_names
        self.name = casename


class GenericRunCaseTable(object):
    """ basically a list of GenericRunCase's', including header"""
    def initFromFile(self, filename, start_at = 0, verbose =True):
        ## special "table"-like file: one line header of variable names then data only
        print "reading raw cases from ", filename
        fin = file(filename).readlines()
#       print "lines: ", fin
        casename = "raw_cases"
        self.cases = []
        param_names = fin[0].split()
        print "PNAMES",param_names
        for iln in range(1,len(fin)):
            if (iln > start_at):  # beware indexing: 0th sample is on line 1, after header, so we need line idex > start_at
                ln = fin[iln].strip().split()
#            print "parsing:", ln
                ln = [float(f) for f in ln]
                self.cases.append(GenericRunCase(casename, param_names, ln))
            


#///////////////////////////////////////////////////

class RunResult(object):
    """ class to modularize collecting the results of all the runs, may have to use the
    Dispatcher and AeroCode to find and parse them, resp."""
    ## Have yet to do anything useful with this class
    # so far I am just copying back my results and directly parsing them (see collect_output)
    ##
    def __init__(self, aerocode):
        self.aerocode = aerocode
    
class FASTRunResult(RunResult):
    def __init__(self, aerocode):
        super(FASTRunResult,self).__init__(aerocode)

    
