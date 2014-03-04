# combine and streamline sampler.py and distn_input.py




"""
We want generic rep. of rows in Table 1, 88_329

What is being represented?
distributions of wind/wave environment parameters.

Assume these all boil down to distributions of _numerical_ parameters.

A twist is that some of the parameters depend on eachother.  But this is just a certain type of
joint distribution.
Simple equality (e.g., assignment x = 7) is also a distribution: unif({y})

So in principle all we need to say is
{v_i} ~ D_k ({p_j})

some cases:
x = 7
x ~ unif({7})

x ~ N(0,1)
y = x
y ~ delta(x)

x = 7
y = E[y|x] = \int{ p(y|x) dy }
requires
p(y|x), eg
y|x ~ N(2x/7, 1)

x,y "jointly distributed"
x,y ~ N([0,0], [[sigmx, covxy],[covxy,sigy]])

Given these specifications, we can then sample the distn's however we want
ie we end up with variables like
d = Distn()
d.type = "gaussian"
d.var = "x"
d.mean = 7
d.var = 11

d = Distn()
d.type = "joint_gaussian"
d.var = ["x","y"]
d.mean = [mux, muy]
d.varcovar = [[etc.][]]

or then a whole class hierarchy for distributions
d = JointGaussian(variables, means, varcovarmatrix)
d = JointUniform(vars,[[x1,x2][y1,y2])
d = DiscreteUniform(var, {a,b,c})   (for enumerations)

or special d = Enumeration(var, {a,b,c})

There are enumerations and distributions
Enumerations have fixed set of values returned by d.sample()
Distributions have a number of samples returned by d.sample()

Then we take 
d1.sample() X d2.sample() X ...
until all the relevant variables are specified

"""
teststr = """
x ~ {7,8}
sigy = 1
y = N(2*x, sigy)
"""

import re, random, numpy as np, numpy.random as npr
from copy import deepcopy

from scipy.stats import vonmises, gamma
# this is not available until scipy 0.14:
#from scipy.stats import  multivariate_normal
# so we have to us numpy.multivariate_normal (at least on my mac)
from numpy.random import weibull
import scipy.linalg as linalg
from math import *
import math
from numpy import matrix
from math import pi, isnan, exp
from numpy import mean
from scipy.stats import vonmises, gamma

def draw_uniform(x0,x1):
    val = npr.uniform(x0,x1)
    return val

def draw_normal(mu, sigma):            
    val = npr.normal(mu, sigma)
    return val

def draw_weibull(shape, scale, nsamples=1):
    x = scale * weibull(shape, nsamples)
    return x

def draw_gamma(shape, scale, nsamples=1):
#    print "gamma params:", shape, scale
    shape = max(1e-3,shape)
    scale = max(1e-3,scale)
    x = gamma.rvs(shape, loc=0, scale=scale, size=nsamples)
    return x

def draw_vonmises(kappa, loc, nsamples=1):
#    print "kappa, loc: ", kappa, loc
#    x = 180/pi * vonmises.rvs(kappa, loc=loc, size=nsamples)
    x = vonmises.rvs(kappa, loc=loc, size=nsamples)
    return x

def draw_multivariate_normal(mean, cov):
    val = npr.multivariate_normal(mean, cov)
#    val = multivariate_normal.rvs(mean, cov)
    return val

############

def prob_uniform(x,x0,x1):
    return 1/float(x1-x0)

def prob_normal(x, mu, sigma):
    val = 1/(sigma * np.sqrt(2 * np.pi)) * np.exp( - (x - mu)**2 / (2 * sigma**2))
    return val    

def prob_weibull(x, shape, scale):
    p = (shape/scale)*(x/scale)**(shape-1)*exp(-(x/scale)**shape)
    return p

def prob_gamma(x, shape, scale):
    shape = max(1e-1,shape)
    p = gamma.pdf(x,shape, loc=0, scale=scale)
    if (p > 1):
        print "weird gamma:p, x, shape, scale", p, x, shape, scale
    return p

def prob_vonmises(x, kappa, loc):
#    print "kappa, loc: ", kappa, loc
#    p = vonmises.pdf(x*pi/180.0,kappa, loc=loc)
#    p = [vonmises.pdf(x*pi/180.0 + m,kappa, loc=loc) for m in [-2*pi, 0, 2*pi]]
    p = [vonmises.pdf(x + m,kappa, loc=loc) for m in [-2*pi, 0, 2*pi]]
    p = max(p)
    return p

def prob_multivariate_normal(x, mu, sigma):
## not in scipy < 0.14:
#    p = multivariate_normal.pdf(x,mean,cov)
#    return p
# instead:
    x = np.array(x)
    mu = np.array(mu)
    sigma = matrix(sigma)
    size = len(x)
    if size == len(mu) and (size, size) == sigma.shape:
        det = linalg.det(sigma)
        if det == 0:
            raise NameError("The covariance matrix can't be singular")
        norm_const = 1.0/ ( math.pow((2*pi),float(size)/2) * math.pow(det,1.0/2) )
        x_mu = matrix(x - mu)
        inv = sigma.I        
        result = math.pow(math.e, -0.5 * (x_mu * inv * x_mu.T))
        return norm_const * result
    else:
        raise NameError("The dimensions of the input don't match")


###############################
###############################

#def math_op(op,v1,v2):
#    if (op == "+"):
#        return v1+v2
#    elif (op == "-"):
#        return v1-v2
#    elif (op == "*"):
#        return v1*v2
#    elif (op == "/"):
#        return v1/v2
#    else:
#        raise ValueError, "unknown math op %s" % op

def is_float(s):
    try:
        v = float(s)
        return True
    except:
        return False


def parse_arg(a):
    from shlex import shlex
    obj = shlex(a)
    obj.wordchars += "." # enables parsing decimals
    alist = list(obj)
#    print "parsed ", a, "to ", alist
#eg: parsed  10 + Vhub/100 - 0.02*(WaveDir+1) to  ['10', '+', 'Vhub', '/', '100', '-', '0.02', '*', '(', 'WaveDir', '+', '1', ')']
    return alist

def merge_dicts(d1,d2):
    d =  {key:d1[key] for key in d1}
    for key in d2:
        d[key] = d2[key]
    return d


class Distribution(object):
    def __init__(self, vstr, ctx):
        self.vstr = vstr # what variable is being defined
        self.ctx = ctx

    def get_bounds(self):
        pass
    def get_partitions(self):
        pass
    def get_name(self):
        return self.vstr
    def calc_prob(self, x):
        return 1
    
    
class EnumDistn(Distribution):
    """ class for distributions that are just list of numbers or single numbers,
    'sampling' is just going to return all values"""
    def __init__(self, vstr, items, ctx):
        super(EnumDistn, self).__init__(vstr, ctx)
        self.items = items

    def sample(self):
#        res = []
#        for i in range(nsample):
#        res.append(random.choice(self.items))
        res = random.choice(self.items)
        res = self.ctx.resolve_value(res)
        return res

    def get_bounds(self):
        """ assumes numbers """
        nums = [float(i[0]) for i in self.items]
        return [min(nums), max(nums)]

    def get_partitions(self):
        return (len(self.items) - 1)
        
    

class FnDistn(Distribution):
    """ class for 'real' distributions like Gaussians, etc. 
    the keys in 'items' are the names of the distributions, assumed to be known 
    and sample-able. items = e.g. {"N": ["2x","sig1"} """
    def __init__(self, vstr, fn, args, ctx):
        super(FnDistn, self).__init__(vstr,ctx)
        self.fn = fn
        self.args = args

    def sample(self):
        argvals = []
        for i in range(len(self.args)):
            a = self.args[i]
            argvals.append(self.ctx.resolve_value(a))

        if (self.fn == "N"):
#            print " need to sample normal with args = ", argvals
            val = draw_normal(argvals[0], argvals[1])
        elif (self.fn == "N2"):
#            print " need to sample 2D normal with args = ", argvals
            val = draw_multivariate_normal([argvals[0], argvals[1]], [[argvals[2], argvals[4]],[argvals[4], argvals[3]]])
        elif (self.fn == "U"):
#            print " need to sample uniform with args = ", argvals
            val = draw_uniform(argvals[0], argvals[1])
        elif (self.fn == "G"):
#            print " need to sample gamma with args = ", argvals
            val = draw_gamma(argvals[0], argvals[1])
        elif (self.fn == "VM"):
#            print " need to sample von Mises with args = ", argvals
            val = draw_vonmises(argvals[0], argvals[1])
        elif (self.fn == "W"):
#            print " need to sample Wiebull with args = ", argvals
            val = draw_vonmises(argvals[0], argvals[1])
        else:
            raise ValueError,  "unknown distribution %s" % self.fn

        return val

    def calc_prob(self, x):
        argvals = []
        for i in range(len(self.args)):
            a = self.args[i]
            argvals.append(self.ctx.resolve_value(a))

        if (self.fn == "N"):
            val = prob_normal(x,argvals[0], argvals[1])
        elif (self.fn == "N2"):
            val = prob_multivariate_normal(x,[argvals[0], argvals[1]], [[argvals[2], argvals[4]],[argvals[4], argvals[3]]])
        elif (self.fn == "U"):
            val = prob_uniform(x,argvals[0], argvals[1])
        elif (self.fn == "G"):
            val = prob_gamma(x,argvals[0], argvals[1])
        elif (self.fn == "VM"):
            val = prob_vonmises(x,argvals[0], argvals[1])
        elif (self.fn == "W"):
            val = prob_vonmises(x,argvals[0], argvals[1])
        else:
            raise ValueError,  "unknown distribution %s" % self.fn
        
        if (math.isnan(val) or val > 1):
            print "NAN", val, x, self.fn, argvals
        return val


class DistnParser(object):
    def __init__(self):
        self.vars = []
        self.dlist = []
        self.dlist_map = {}
        
    def parse_file(self,fname):
        mystr = file(fname).readlines()
        return self.parse(mystr)

    def parse(self, mystr):
        for ln in mystr:
            ln = ln.strip()
            newdist = None
            if (len(ln) > 0 and ln[0] != "#"):
                # first get rid of anything past any "#" on the right
                ln = ln.split("#")[0]
 #               print "your line: ", ln
                # separate vars from the distn
                tok = ln.split("=")
                if len(tok) > 1:
#                    print "found distn: ", tok                
                    vtok = tok[0].split(",")
                    # parse out the vars in question:
                    vstr = ""
                    for v in vtok:
                        v = v.strip()
                        if (v in self.vars):
                            print "ERROR: Variable %s is doubly defined" %v
                        self.vars.append(v)
                        vstr = "%s" % v
                    # now parse the distn spec.
                    dspec = tok[1].strip()
#                    print "look at", dspec
                    q = re.match("([^(]+)(\(.*\))", dspec)
                    if (q != None):
                        # found a function-like defn
                        dist = q.group(1) 
                        args = q.group(2)
#                        print "split ", dspec , "into ", dist, args
                        #eg: split  G(10 + Vhub/100 - 0.02*(WaveDir+1),.25) into  G (10 + Vhub/100 - 0.02*(WaveDir+1),.25)
                        args=args.strip("(").strip(")").split(",")
                        args = [s.strip() for s in args]
                        # now parse variables out of expressions
                        # simple math allowed: <val> := <number> | <val> <op> <val> where <op> = +-*/
                        arglist = []
                        for a in args:
                            alist = parse_arg(a)
                            arglist.append(alist)    
#                        print "found dist=", dist, " arglist=", arglist
                        newdist = FnDistn(vstr,dist,arglist, self)
                        self.dlist.append(newdist)
                    elif dspec[0] == "{":
                        # found a set
                        args = [s.strip() for s in dspec.strip("{").strip("}").split(",")]
#                        args = [float(s) for s in args]
#                        print "found set ", args
                        args = [parse_arg(a) for a in args]
#                        print "FOUND set ", args
                        newdist = EnumDistn(vstr,args, self)
                        self.dlist.append(newdist)
                    else:
                        try:
                            arg = [parse_arg(dspec)]
                            # found a value. TODO: tuples
#                            print "found number ", arg
                            newdist = EnumDistn(vstr, arg, self)
                            self.dlist.append(newdist)
                        except:
                            print "cannot parse distribution spec ", dspec
                if (newdist != None):
                    self.dlist_map[vstr] = newdist
                        
        print "defined distns. for vars ", self.vars
#        print self.dlist       
#        print "dlist map = ", self.dlist_map

        return self.dlist

    def clear_values(self,):
        self.values = {}
    def set_value(self, s,v):
        self.values[s] = v
        # also deconstruct joint distribution values into their individual variables
        # e.g. Hs.Tp: [1,3] -> Hs: 1, Tp:3
        subv = s.split(".")
        if (len(subv) > 1):
            for i in range(len(subv)):
                self.values[subv[i]] = v[i]

    def set_values(self, e):
        for key in e:
            self.set_value(key, e[key])

    def sample(self):
        self.clear_values()
        for d in self.dlist:
            s = d.sample()
#            print "sampled ", d.vstr, " and got ", s
            self.set_value(d.vstr,s)

    def add_enum(self, slist, enum):
        """
        slist = list of samples we're building
        enum = distn with enum.items list of possible values
        output = slist X enum.items
        """
        newlist = []
#        print "add enum, slist, enum.items", slist, enum.items
        for s in slist: 
            for x in enum.items:
                item = {}
                for y in s:
                    item[y] = s[y]
                    self.set_value(y,s[y])
#                item[enum.vstr] = self.resolve_value(x)
                item[enum.vstr] = x  # not resolved yet!
                newlist.append(item)                
#                print "appended item to newlist" , item, newlist
#        print newlist
        return newlist

    def expand_enums(self):
        """ return list of dicts """
        self.clear_values()
        slist = [{}]
        for d in self.dlist:
            if (hasattr(d,"items")):  #### bad programming!
                slist = self.add_enum(deepcopy(slist), d)
        return slist

    def sample_fns(self):
        """ return list of dicts """
        for d in self.dlist:
            if (hasattr(d,"fn")):
                s = d.sample()
#                print "sampled ", d.vstr, " and got ", s
                self.set_value(d.vstr,s)
        return self.values

    def multi_sample(self, numsamples, expand_enums=False):
        slist = []
        if (expand_enums):
#            print "expanding set variables, then sampling %d times" % numsamples
            # make slist of product space of set vars.
            enum_list = self.expand_enums()
#            print "enum_list", enum_list
            for e in enum_list:
#                self.clear_values()
#                self.set_values(e)
                for i in range(numsamples):
                    # now truly sampled vars to each of them                    
                    # combine real samples to enum cases
                    self.clear_values()

                    for d in self.dlist:
 #                       print "scanning ", d.vstr
                        if (hasattr(d,"fn")):
                            s = d.sample()
                            #print "sampled ", d.vstr, " and got ", s
                            self.set_value(d.vstr,s)
                        
                        if (hasattr(d,"items")):  #### bad programming!
                            maxiter = len(e)
                            tries = 0
                            while (tries < maxiter):
                                for it in e:  # find this var and resolve it here
#                                    print it, e[it]
                                    # this is some crazy stuff: try (maybe out of order b/c of dict) until we succeed
                                    # to resolve everything
                                    try:
                                        val = self.resolve_value(e[it])
                                        self.set_value(it,val)
#                                        print "succes resolving ", e[it]
                                    except:
#                                        print "failed resolving ", e[it]
                                        pass
                                    tries += 1
                    slist.append(self.values)

#                    vals = self.sample_fns()
#                    print vals, e
#                    vals = merge_dicts(vals, e)
#                    slist.append(vals)
        else:            
#            print "sampling %d times" % numsamples
            for i in range(numsamples):
                self.clear_values()
                vals = self.sample()
#                print "sample %d = " % i, self.values
                slist.append(self.values)
        
        return slist

    def resolve_one_value(self,a):
#        print "resolve_one_value()", a        
        if (is_float(a)):
            return float(a)
        else:
            for d in self.dlist:
                if a == d.vstr:
                    return self.values[a]
#            raise ValueError, "did not find variable:%s: in dlist" % a 
        return a

    def resolve_value(self,a):
#        print "resolving:", a
        vals = [self.resolve_one_value(x) for x in a]
#        print vals
        s = ""
        for v in vals:
            if is_float(v):
                s = "%s %f" % (s, v)
            else:
                s = "%s %s" % (s, v)
#        print "evaluating:", s
        val = eval(s)
#        print "= ", val
        return val
#        if (len(a) == 1):
#            return self.resolve_one_value(a[0])
#        else:
#            v1 = self.resolve_one_value(a[0])
#            v2 = self.resolve_one_value(a[2])
#            op = a[1]
#            print "2",a
#            v1 = self.resolve_one_value(a[-1])
#            v2 = self.resolve_value(a[:-2])
#            op = a[-2]
#            return math_op(op, v1, v2)

    def get_num_samples(self):
        self.sample()  # kludge: sample once to get NumSamples set, if it exists
        if "NumSamples" in self.values:
            return int(self.values['NumSamples'])
        else:
            return 1

    def get_bounds(self):
        """ assume all enum distns, get their bounds for conversion to dakota """
        bounds = []
        for d in self.dlist:
            bounds.append(d.get_bounds())
        low = [b[0] for b in bounds]
        high = [b[1] for b in bounds]
        return [low,high]

    def get_partitions(self):
        """ assume all enum, get their length, assume uniform incrs to convert to dakota """
        part = []
        for d in self.dlist:
            part.append(d.get_partitions())
        return part

    def get_names(self):
        """ get names of all the distn's (what vars are defined), for mapping from dakota variable list """
        part = []
        for d in self.dlist:
            part.append(d.get_name())
        return part

    def calc_prob(self, samp):
        """ calc probability of samp according to parsed distribution """
        self.clear_values()
        self.set_values(samp)        
        # for each key/value, need to find the distribution it belongs to
        # plan on using a pre-prepared mapping
        ptot = 1
        for var in self.values:
            if (var in self.dlist_map):
                dist = self.dlist_map[var]
                p = dist.calc_prob(self.values[var])
                ptot *= p
        return ptot


def get_options():
    from optparse import OptionParser
    parser = OptionParser()    
    parser.add_option("-i", "--input", dest="main_input",  type="string", default="runbatch-dist.txt",
                                    help="main input file describing distribution, ie cases to run")
    parser.add_option("-n", "--nsamples", dest="nsamples", help="how many samples to generate", type="int", default=5)
    parser.add_option("-o", "--output", dest="main_output",  type="string", default="runcases.txt",
                                    help="output file (where to write the run cases)")
    parser.add_option("-p", "--probfile", dest="old_samples",  type="string", default=None,
                                    help="an input file of samples whose probabilities we want to calculat w.r.t input distn")
            
    (options, args) = parser.parse_args()
    return options, args

def read_samples(fname):
    lines = file(fname).readlines()
    hdr = lines[0].split()
    dat = []
    for ln in lines[1:]:
        dat.append([float(x) for x in ln.split()])
    return hdr, dat

def gen_cases():
    options, args = get_options()
    
    dparser = DistnParser()
    dparser.parse_file(options.main_input)

    if (options.old_samples != None):
        # in this mode, we are given a distribution and, separately, a set of old samples.  Our job is to calculate the
        # probabilities for the samples w.r.t. the given distribution
        old_hdr, old_samples = read_samples(options.old_samples)
        pidx = old_hdr.index("Prob")
        new_samples = []
        for s in old_samples:
            samp = {old_hdr[i]:s[i] for i in range(len(s))}
            p = dparser.calc_prob(samp)
#            print "sample ", samp
#            print "prob ", p
            s[pidx] = p
            new_samples.append(s)

        fout = file(options.main_output, "w")
        for key in old_hdr:
            fout.write("%s " % key)
        fout.write("\n")
        for s in new_samples:
            for val in s:
                fout.write("%.16e " % val)
            fout.write("\n")
        fout.close()
    else:
        numsamples = options.nsamples
        slist = dparser.multi_sample(numsamples, expand_enums = True)
        print "%d samples, SAMPLING set/enumeration variables:" % (numsamples)
        fout = file(options.main_output, "w")
        s = slist[0]
        for key in s:
            fout.write("%s " % key)
        fout.write("Prob\n")
        for i in range(len(slist)):
            s = slist[i]
            p =  dparser.calc_prob(s)
    #        print "sample %d = " % i, s, p
            for key in s:
                fout.write("%.16e " % s[key])
            fout.write("   %.16e\n" % p)
        fout.close()
        print "wrote %d samples (run cases) from distribution in \'%s\' to \'%s\'" % (numsamples, options.main_input, options.main_output)


if __name__=="__main__":
    gen_cases()

