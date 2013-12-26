import os, copy
import numpy as np
from math import pi

"""
DLC -> IECDLC
DLC -> RunCase -> FASTRunCase
               -> HAWC2RunCase 
We might argue for a level between DLC and IECDLC called StudyCase, b/c not all multi-run
cases are IEC, but not all DLC's are multi-run.
"""

from distn_input import DistnParser

###############################
###### Design load case, no need for openMDAO
class DesignLoadCase(object):
    """ base class for design load case representing a whole study 
    (e.g., but not limite to, one row of table 1,  88_329).
    In particular, will be probably more than one run of the underlying aerodode."""
    def __init__(self, case):
        self.name = case
        pass

        
class IECDesignLoadCase(DesignLoadCase):
    """ one IEC case, e.g. IEC1.4. """
    def __init__(self, case, params):        
        """ case is a string 
        params is a dict of parameters for this case
        """
        super(IECDesignLoadCase,self).__init__(case)
        self.params = params # dict of parameters for this case

    def genGenericCases(self):
        """ An IEC Design Load Case is one row of table 1, 88_329 
        This fn is to generate subcases.
        """
        ### this fn was mostly for testing, XXXRunCaseBuilder, below
        gcases = []
        # as a test, will hard code wind speed and random seed
        winds = [10,20]
        rs = [1,2,3]
        for w in winds:
            for r in rs:
                g = WindRandomSeedRunCase(self, w, r)
                gcases.append(g)
        return gcases
        
class GenericIECDesignLoadCase(DesignLoadCase):
    """ one IEC case, e.g. IEC1.4. """
    def __init__(self, case, params, parser):        
        """ case is a string 
        params is a dict of parameters for this case
        """
        super(GenericIECDesignLoadCase,self).__init__(case)
        self.params = params # dict of parameters for this case
        self.parser = parser # distn_parser object able to generate samples for this case

class RunCase(DesignLoadCase):
    """ a single RUN of the aerocode.
    The params are meant to be the non-turbine driving parameters like wind speed,
    wave period, direction, etc. ie "environment"

    This is _one run_ of the underlying wind code. An IECDesignLoadCase is composed of many RunCases.
    """
    def __init__(self, parent):
        super(RunCase,self).__init__(parent)
        self.parent = parent
        
class WindRandomSeedRunCase(RunCase):
    """ a single run of the aerocode.
        meant to be the non-turbine driving parameters like wind speed,
        wave period, direction, etc. ie "environment"
    """
    def __init__(self, parent, windspeed, randomseed):
        super(WindRandomSeedRunCase,self).__init__(parent)
        self.ws = windspeed
        self.randomseed = randomseed
        self.windfile = os.path.join(WaveCaseLoc,"%s%.2d.bts" % (WaveNameBase, randomseed))  ## already FAST specific !
        self.name = "%s-ws%.1f.rs%d" % (parent.name, windspeed, randomseed)
        

class FASTRunCase(WindRandomSeedRunCase):
    """ FAST specific single run of the aerocode.
    """
    def __init__(self, parent, windspeed, randomseed, fst_params):
        super(FASTRunCase,self).__init__(parent, windspeed, randomseed)
        self.fst_params = copy.deepcopy(fst_params) # dict of FAST keywords/values to override
        # override name for uniqueness
        for p in fst_params:
            self.name += "%s.%.1f" % (p[0:3],fst_params[p])

class RawDesignLoadCase(DesignLoadCase):
    """ Like Run case, but only base key value info"""
    def __init__(self,casename, param_names, ln):
        super(RawDesignLoadCase,self).__init__(casename)
        self.x = np.array(ln)
        self.param_names = param_names
        self.name = casename
        

        
class NREL13_88_329Input(object):
    """ format made up by P Graf, closely following spec in 88_329 doc, but also mimicing some aspects
    of RunIEC.pl input format.  like a csv/excel version.
e.g. 
DLC,   @WindSpeeds,   NumSeeds,  NumWavePer, TotProbReq, TStart, AnalTime
DLC1.1,  12.3 14.5  ,  1   ,     1  , 	     N/A, 	 20.0 ,  60.0
DLC1.2,  14.3 19.5  ,  1   ,     1  ,	     0.54321,    20.0 ,  60.0
    """
    def __init__(self):
        super(NREL13_88_329Input, self).__init__()
    
    def initFromFile(self, filename, verbose =True):
        """ make design load cases from simple line by line spec """    
        fin = file(filename).readlines()
        lzero=True
        self.cases = []
        for ln in fin:
            ln = [stuff.strip() for stuff in ln.strip().split(",")]
            if (len(ln) > 0 and not ln[0] =='' and not ln[0][0] == "#"):
                if (lzero):
                    print "header line: ", ln
                    # header line
                    fields = [s.strip(",") for s in ln[1:]]
                    lzero=False
                else:
                    print "real line: ", ln
                    dlc = ln[0]
                    d = {fields[i]:ln[i+1].strip("\"").strip("\t").strip() for i in range(len(fields))}
                    self.cases.append(IECDesignLoadCase(dlc, d))
        print "88_329 cases = ", [[c.name, c.params] for c in self.cases]


class NREL13_88_329FromDistn(object):
    """ format made up by P Graf, closely following spec in 88_329 doc,
    but making us a generic "distribution format specification" as implemented in
    distn_input.py.
    distn_input.py already accepts block of lines that can represent ONE design load case.
    Just need separator lines.  ok, let's say:
    "--DLCX.X--"
    at start of line begins a new block
    """
    def __init__(self):
        super(NREL13_88_329FromDistn, self).__init__()
    
    def initFromFile(self, filename, verbose =True):
        """ make design load cases from simple line by line spec """    
        fin = file(filename).readlines()
#       print "lines: ", fin
        thiscase = []
        casename = ""
        self.cases = []
        for iln in range(len(fin)):
            ln = fin[iln]
#            print ln
            if (iln == len(fin)-1 or fin[iln+1][0:5] == "--DLC"):
                # found new case.  first finish up the old one:
                if (casename == ""):
                    print "no casename, skipping these lines"
                else:
                    thiscase.append(ln)
                    dparser = DistnParser()
                    dparser.parse(thiscase)
                    self.cases.append(GenericIECDesignLoadCase(casename, {}, dparser))
            elif (ln[0:5] == "--DLC"):
                casename = ln.strip().strip("-")
                thiscase = []
                print "got new case name ", casename
            else:
                thiscase.append(ln)
        print "generic 88_329 cases = ", [[c.name, c.parser] for c in self.cases]

class RawCases(object):
    def __init__(self):
        super(RawCases, self).__init__()

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
                self.cases.append(RawDesignLoadCase(casename, param_names, ln))
            

#-----------------------------------------------
##### stub so far;  needs to get actual results from run ###
## also no need for openMDAO
class DLCResult(object):
    """ class to modularize collecting the results of all the runs, will have to use the
    Dispatcher and AeroCode to find and parse them, resp."""
    def __init__(self, aerocode):
        self.aerocode = aerocode

    def save(self):
        pass

class FASTDLCResult(DLCResult):
    def __init__(self, aerocode):
        super(FASTDLCResult,self).__init__(aerocode)
        rawfast = aerocode.rawfast
    

#-------------------------#############################-------------------------#
"""
 hard coded, FAST-specific (in exact form) constants and stuff.
lots will come from input file, just not DLC sections.  TODO later, parse them from more
complex file (e.g. sample.riec). for now,
adding them here AS NEEDED
"""

Vref = 50
Vref_95 = 0.95 * Vref
WaveCaseLoc = "/Users/pgraf/work/wese/RunIEC/materials/Environment/Wind/FF_Wind/1.6_37x51_3600s/"
WaveNameBase = "SimLength_NTM_3600s_04.0V0_S"
 

"""
 cases in RunIEC.pl, loops are over:
1.1: windspeed, seed, waveper 
1.2: windspeed, seed, wavecases
1.3: windspeed, seed, waveper
1.4: windcases, seed, waveper
1.5: windspeed, sheertype(windcases), seed, waveper
1.6a: windspeed, seed, waveper
2.1: windspeed, seed, waveper
2.3: windcases, seed, waveper
6.1a: (fixedwind), seed, waveper, nacyaw, wavedir
6.2a: (fixedwind), seed, waveper, nacyaw, wavedir
6.3a: (fixedwind), seed, waveper, nacyaw, wavedir
6.4: (fixedwind), seed, wavecases
7.1a: (fixedwind), seed, waveper, nacyaw, wavedir
"""

""" encode part of Table 1 of ODR 88_329e 
casename, wind, waves, directionality
This will tell us _what to expect_ in the input dictionaries
"""
Table1 = {'default': ['windspeed'],
          'DLC1.1': ['windspeed', 'waveper'],
          'DLC1.2': ['windspeed', 'wavecases'],
          'DLC1.3': ['windspeed', 'waveper']
          };

def fix_name(name):
    if (name not in Table1):
        name = "default"
    return name

def has_key(name, key):
    name = fix_name(name)
    if (name in Table1):
        if key in Table1[name]:
            return True
    return False

def has_windspeed(name):
    return (has_key(name, 'windspeed'))

def has_waveper(name):
    return (has_key(name, 'waveper'))
    
def has_wavecases(name):
    return (has_key(name, 'wavecases'))

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

def save_run_cases(casename, cases):
    # write in file like sampler writes
    fout = file("dlcscanpoints.txt" , "w")
    fout.write("Vhub WaveDir Hs Tp \n")
    for i in range(len(cases)):
        case = cases[i]
        fst = case.fst_params
#        import pdb; pdb.set_trace()
        fout.write("%f %f %f %f\n" % (case.ws, pi/180.0 * fst['WaveDir'], fst['WaveHs'], fst['WaveTp']))
    fout.close()
    


class DLCRunCaseBuilder(object):
    """ superclass for run cases, ie a single aerodcode run.
    Anything in common to build toward here ??? 
    We want to push anything that is not specific to a certain aerocode to be set up here """

    WSPitch    =   np.array([0.0, 11.0, 12.0, 25.0])
    Pitch      =   np.array([0.0,  0.0,  4.0, 22.0])
    WSRpm      =   np.array([0.0, 10.2, 11.4])
    Rpm        =   np.array([6.0, 10.0, 12.1])

    def __init__(self):
        pass

    @staticmethod
    def GetPitch(ws):
        return np.interp(ws, FASTRunCaseBuilder.WSPitch, FASTRunCaseBuilder.Pitch)

    @staticmethod
    def GetRotSpd(ws):
        return np.interp(ws, FASTRunCaseBuilder.WSRpm, FASTRunCaseBuilder.Rpm)


def sample2FASTparams(sample):
    params = {}
    s = -1 # random seed, not used
    if ('Vhub' in sample):
        w = sample['Vhub']
        blpitch1 = DLCRunCaseBuilder.GetPitch(w)
        rotspeed = DLCRunCaseBuilder.GetRotSpd(w)
        params['RotSpeed'] = rotspeed
        params['BlPitch1'] = blpitch1
        params['BlPitch2'] = blpitch1
        params['BlPitch3'] = blpitch1
            ## these b/c some FAST files (that might be the template) use parens:
        params['BlPitch(1)'] = blpitch1  
        params['BlPitch(2)'] = blpitch1
        params['BlPitch(3)'] = blpitch1
        
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
    return w,s,params

class ParamDesignLoadCaseBuilder(DLCRunCaseBuilder):
    """ build sample from x, for use with the RunCaseBuilders """

    @staticmethod
    def buildRunCase_x(x, names, dlc):
        sample = {names[i]:x[i] for i in range(len(x))}

        name = dlc.name
        print "setting up dlc name %s" % name

        w,s,params = sample2FASTparams(sample)
        print "got params", params
        print "from sample", sample
        subcase = FASTRunCase(dlc,w,s,params)

        return subcase

class GenericFASTRunCaseBuilder(DLCRunCaseBuilder):
    # generic parser and sampler, but then we still fill a FAST-specific dictionary

    @staticmethod
    def genRunCases(dlc):

        # first let the dlc's parser generate a list of cases (samples), each of which is a dictionary
        parser = dlc.parser
        slist = parser.multi_sample(parser.get_num_samples(),expand_enums=True)

        name = dlc.name
        print "setting up dlc name %s" % name
        cases = []

        for sample in slist:
            w,s,params = sample2FASTparams(sample)
            subcase = FASTRunCase(dlc,w,s,params)
            cases.append(subcase)
        
        return cases


class FASTRunCaseBuilder(DLCRunCaseBuilder):
    """ setting up a single FAST run.
    relies on some specific variable like windspeed, otherwise a dictionary overriding 
    line by line the entries in the template .fst file 
    """

    @staticmethod
    def genRunCases(parent, dlc):
        """ given dlc spec (ie 1.1, and its params(as dict)), build list of
        separate runs required, for use in case iterator

        dlc is a dict., all entries are strings b/c they are parsed generically from csv

        We need to consider loops over (some specifics from spec):
        -- wind speed (all-{6.1a,6.2a,6.3a,7.1a})
          ++ just speed:
          ++ "wind conditions" (wind files):1.4,2.3
          ++ speed & sheer: 1.5
          -- fixed speed: 6.1a,6.2a,6.3a,7.1a
        -- random seed (for stats) (all)
        -- wave periods (all)
        -- yaw (6.1a,6.2a,6.3a,7.1a)
        -- wave direction(6.1a,6.2a,6.3a,7.1a)
        """
        name = parent.name
        cases = []
        params = {}
        print "setting up dlc name %s" % name

        ws = None
        wp = None
        wc = None
        seeds = None
        if (has_windspeed(name)):
            ws = dlc["@WindSpeeds"] # a string of space separated numbers
            ws = ws.split()  
            ws = [float(f) for f in ws]
        else:
            ws = [Vref_95]

        # a dictionary to stort line by line substitutions in .fst file.
        params['TStart'] = float(dlc['TStart'])
        params['TMax'] = params['TStart'] + float(dlc['AnalTime'])

        if (has_waveper(name)):
            wp = int(dlc['NumWavePer'])
            print wp
        if (has_wavecases(name)):
            # This is encoded by 'TotProbReq', then call to get wave cases
            tpr = float(dlc['TotProbReq'])
            print tpr
            
## when it's ready, use these checks.  But for now we haven't completed table
#        if (not wp==None and not wc==None):
#            raise ValueError, "both wave period and wave cases supplied"
#        if (wp==None and wc==None):
#            raise ValueError, "neither wave period nor wave cases supplied"
                
        seeds = int(dlc['NumSeeds']) # all cases have this
        seedlist = range(1,seeds+1)
                
        for w in ws:
            blpitch1 = RunCaseBuilder.GetPitch(w)
            rotspeed = RunCaseBuilder.GetRotSpd(w)
            params['RotSpeed'] = rotspeed
            params['BlPitch1'] = blpitch1
            params['BlPitch2'] = blpitch1
            params['BlPitch3'] = blpitch1
            ## these b/c some FAST files (that might be the template) use parens:
            params['BlPitch(1)'] = blpitch1  
            params['BlPitch(2)'] = blpitch1
            params['BlPitch(3)'] = blpitch1

            for s in seedlist:
                subcase = FASTRunCase(parent,w,s,params)
                cases.append(subcase)
        
        return cases

