

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

def math_op(op,v1,v2):
    if (op == "+"):
        return v1+v2
    elif (op == "-"):
        return v1-v2
    elif (op == "*"):
        return v1*v2
    elif (op == "/"):
        return v1/v2
    else:
        raise ValueError, "unknown math op %s" % op

def is_float(s):
    try:
        v = float(s)
        return True
    except:
        return False


def parse_arg(a):
    z = re.match("([^+\-*/]*)([+\-*/])(.*)", a)
    if (z != None):
        z1 = z.group(1).strip()
        z2 = z.group(2).strip()
        z3 = z.group(3).strip()
#        print "found complex arg:", z1, z2, z3 
        alist = [z1,z2,z3]
    else:
#        print "found simple arg:", a
        alist = [a.strip()]
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


class FnDistn(Distribution):
    """ class for 'real' distributions like Gaussians, etc. 
    the keys in 'items' are the names of the distributions, assumed to be known 
    and sample-able. items = e.g. {"N": ["2x","sig1"} """
    def __init__(self, vstr, fn, args, ctx):
        super(FnDistn, self).__init__(vstr,ctx)
        self.fn = fn
        self.args = args

    def sample(self):
        print "sampling fnDistn"
        argvals = []
        for i in range(len(self.args)):
            a = self.args[i]
            argvals.append(self.ctx.resolve_value(a))
        if (self.fn == "N"):
            print " need to sample N with args = ", argvals
            val = npr.normal(argvals[0], argvals[1])
            return val
        elif (self.fn == "N2"):
            print " need to sample N2 with args = ", argvals
            val = npr.multivariate_normal([argvals[0], argvals[1]], [[argvals[2], argvals[4]],[argvals[4], argvals[3]]])
            return val
        elif (self.fn == "U"):
            print " need to sample U with args = ", argvals
            val = npr.uniform(argvals[0], argvals[1])
            return val
        else:
            raise ValueError,  "unknown distribution %s" % self.fn

class DistnParser(object):
    def __init__(self):
        self.vars = []
        self.dlist = []

        
    def parse_file(self,fname):
        mystr = file(fname).readlines()
        return self.parse(mystr)

    def parse(self, mystr):
        for ln in mystr:
            ln = ln.strip()
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
                    q = re.match("([^(]*)(\([^)]*\))", dspec)
                    if (q != None):
                        # found a function-like defn
                        dist = q.group(1) 
                        args = q.group(2)
                        args=args.strip("(").strip(")").split(",")
                        args = [s.strip() for s in args]
                        # now parse variables out of expressions
                        # simple math allowed: <val> := <number> | <val> <op> <val> where <op> = +-*/
                        arglist = []
                        for a in args:
                            alist = parse_arg(a)
                            arglist.append(alist)    
#                        print "found dist=", dist, " arglist=", arglist
                        self.dlist.append(FnDistn(vstr,dist,arglist, self))
                    elif dspec[0] == "{":
                        # found a set
                        args = [s.strip() for s in dspec.strip("{").strip("}").split(",")]
#                        args = [float(s) for s in args]
#                        print "found set ", args
                        args = [parse_arg(a) for a in args]
#                        print "FOUND set ", args
                        self.dlist.append(EnumDistn(vstr,args, self))
                    else:
                        try:
                            arg = [parse_arg(dspec)]
                            # found a value. TODO: tuples
#                            print "found number ", arg
                            self.dlist.append(EnumDistn(vstr, arg, self))
                        except:
                            print "cannot parse distribution spec ", dspec
                        
        print 
        print "defined distns. for vars ", self.vars
        print self.dlist

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
                item[enum.vstr] = self.resolve_value(x)
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
                self.clear_values()
                self.set_values(e)
                for i in range(numsamples):
                    # now truly sampled vars to each of them                    
                    # combine real samples to enum cases
                    vals = self.sample_fns()
#                    print vals, e
                    vals = merge_dicts(vals, e)
                    slist.append(vals)
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


    def resolve_value(self,a):
        if (len(a) == 1):
            return self.resolve_one_value(a[0])
        else:
            v1 = self.resolve_one_value(a[0])
            v2 = self.resolve_one_value(a[2])
            op = a[1]
            return math_op(op, v1, v2)

    def get_num_samples(self):
        self.sample()  # kludge: sample once to get NumSamples set, if it exists
        if "NumSamples" in self.values:
            return int(self.values['NumSamples'])
        else:
            return 1

if __name__=="__main__":
    dparser = DistnParser()
    dparser.parse_file("table1_distns.txt")
    numsamples = 5 
    slist = dparser.multi_sample(numsamples, expand_enums = False)
    print "\n%d samples, SAMPLING set/enumeration variables:" % (numsamples)
    for i in range(len(slist)):
        print "sample %d = " % i, slist[i]
    slist = dparser.multi_sample(numsamples, expand_enums = True)
    print "\n%d samples X all values of set/enumeration variables:" % (numsamples)
    for i in range(len(slist)):
        print "sample %d = " % i, slist[i]

"""
    slist = []
    for i in range(numsamples):
        vals = dparser.sample()
        print "sample %d = " % i, dparser.values
        slist.append(dparser.values)
    print "\n%d samples:" % numsamples
    for i in range(numsamples):
        print "sample %d = " % i, slist[i]
"""        
