from scipy.stats import vonmises, gamma
from numpy.random import weibull
import numpy.random as npr
from math import pi, isnan, exp
from numpy import mean
import numpy as np

def draw_weibull(shape, scale, nsamples):
    x = scale * weibull(shape, nsamples)
    return x

def draw_gamma(shape, scale, nsamples):
    x = gamma.rvs(shape, loc=0, scale=scale, size=nsamples)
    return x

def draw_vonmises(kappa, loc, nsamples):
#    print "kappa, loc: ", kappa, loc
#    x = 180/pi * vonmises.rvs(kappa, loc=loc, size=nsamples)
    x = vonmises.rvs(kappa, loc=loc, size=nsamples)
    return x

############

def prob_weibull(x, shape, scale):
    p = (shape/scale)*(x/scale)**(shape-1)*exp(-(x/scale)**shape)
    return p

def prob_gamma(x, shape, scale):
    p = gamma.pdf(x,shape, loc=0, scale=scale)
    return p

def prob_vonmises(x, kappa, loc):
#    print "kappa, loc: ", kappa, loc
#    p = vonmises.pdf(x*pi/180.0,kappa, loc=loc)
#    p = [vonmises.pdf(x*pi/180.0 + m,kappa, loc=loc) for m in [-2*pi, 0, 2*pi]]
    p = [vonmises.pdf(x + m,kappa, loc=loc) for m in [-2*pi, 0, 2*pi]]
    p = max(p)
    return p

########

def interp_tab1(fname):
    from scipy import interpolate
    dat = file(fname).readlines()
    dat = np.array([dat[i].split() for i in range(1,len(dat))])
    x = [float(s) for s in dat[:,0]]
    y = [float(s) for s in dat[:,1]]
    f = interpolate.interp1d(x, y, kind='linear')
    return f,[min(x), max(x)]

def myfloat(s):
    f = float(s)
    if isnan(f):
        f = 1
    return f

def interp_tab2(fname):
##    import scipy.interpolate.RectBivariateSpline as rbs
##    tab = rbs(x,y,z)
    from scipy import interpolate
    dat = file(fname).readlines()
    dat = np.array([dat[i].split() for i in range(0,len(dat))])
    y = [float(s) for s in dat[0,1:]]
    x = [float(s) for s in dat[1:,0]]
#    print len(x), x
#    print len(y), y
#    print len(dat)
#    z1 = [float(s) for s in dat[14][1:]]
#    print len(z1), z1
    z = np.array([  [myfloat(s) for s in dat[i][1:]] for i in range(1,len(x)+1)])
    xx, yy = np.meshgrid(y,x)
#    print xx,yy,z
#    print xx.shape, yy.shape,z.shape
    f = interpolate.interp2d(xx, yy, z, kind='linear')
    return f


class Context(object):
    def __init__(self,dim=4):
        npr.seed(1)

        self.WindDirKappaTab,self.Vbounds = interp_tab1("windwavedistn/WindDir_kappa.txt")
        self.WindDirLocTab,dummy = interp_tab1("windwavedistn/WindDir_loc.txt")
        self.HsShapeTab = interp_tab2("windwavedistn/Hs_shape.txt")
        self.HsScaleTab = interp_tab2("windwavedistn/Hs_scale.txt")
        self.TpShapeTab = interp_tab2("windwavedistn/Tp_shape.txt")
        self.TpScaleTab = interp_tab2("windwavedistn/Tp_scale.txt")

        # these are hand tuned at this point based on FAST. ugly, no?
        # should be outside of whatever FAST actually runs, so we can always compute probability if we want
        # but should be inside of what FAST _can_ run, so we don't generate illegal (ie crash-causing) samples
        # Real issue is the _lower_ bounds. (and both for winddir). These match "design_load_case.py"
        self.WindDirBounds = [-179.999, 179.999]
        self.HsBounds = [0.001, 20]
        self.TpBounds = [0.001, 30]
        self.Vbounds = [0,30]

        self.dim = dim # mostly for testing, sample less dimensions in order:Vhub, WindDir, Hs,Tp 
        self.Hs0 = 3  # defaults for testing of sampling for only two params.
        self.Tp0 = 2
        self.WindDir0 = 0
    
    def sample(self,ns):
    #    WaveDir = draw_vonmises( 0.844272129,-0.477919589, ns)
        Vhub = []
        WaveDir = []
        Hs = []
        Tp = []
        Prob = []
        dim = self.dim
    #    shape = HsShapeTab(10,110)
    #    print shape
    #    vtest = draw_weibull (2.120, 9.767, 20)
    #    print vtest
        i = 0
#        fweib = file("weibull.dat", "w")
        while i < ns:
            hg = self.Hs0
            tg = self.Tp0
            wd = self.WindDir0
            phg = 1
            ptg = 1
            pwd = 1
            v = draw_weibull (2.120, 9.767, 1)  # hard coded east coast vals
            v = v[0]
            pv = prob_weibull(v, 2.120, 9.767)
#            fweib.write("%f\n" % v)  ## record ALL Weibull samples
    #        print "v=",v
            got_sample = False
            if (dim <= 1):
                got_sample = True
            elif (v< self.Vbounds[0] or v>self.Vbounds[1]):
                got_sample = False
            else:
#                print "v, bounds", v, self.Vbounds
                k = self.WindDirKappaTab(v)
                l = self.WindDirLocTab(v)
    #            print "k,l", k,l
                wd = draw_vonmises(k, l, 1)
                wd = wd[0]
                pwd = prob_vonmises(wd, k, l)
#                print v, wd, pwd, k,l
                if (dim <= 2):
                    got_sample = True                    
                else:
                    hshape = self.HsShapeTab(v,wd)
                    hscale = self.HsScaleTab(v,wd)
                    if (hshape < 0 or hscale < 0): 
                        got_sample = False
                    else:
                        hg = draw_gamma(hshape, hscale, 1)
                        hg = hg[0]
                        phg = prob_gamma(hg, hshape, hscale)

                    tshape = self.TpShapeTab(v,wd)
                    tscale = self.TpScaleTab(v,wd)
                #       print "shape, scale", tshape, tscale
                    if (tshape < 0 or tscale < 0): 
                        got_sample = False
                    else:
#                        print tshape, tscale
                        tg = draw_gamma(tshape, tscale, 1)
                        tg = tg[0]
                        ptg = prob_gamma(tg, tshape, tscale)
                        got_sample = True

            if (got_sample):
# and (hshape > 0 and hscale > 0 and tshape > 0 and tscale > 0): 
 #                   if (hg >= self.HsBounds[0] and hg <=self.HsBounds[1] and
 #                       tg >= self.TpBounds[0] and tg <=self.TpBounds[1] and
  #                      wd >= self.WindDirBounds[0] and wd <= self.WindDirBounds[1]):
                    # finally we have a sample with nonzero prob.
                Hs.append(hg)
                Vhub.append(v)
                WaveDir.append( wd )
                Tp.append(tg)
                Prob.append(pv*pwd*phg*ptg)
                i += 1
#        fweib.close()

        self.Hs = Hs
        self.Vhub = Vhub
        self.WaveDir = WaveDir
        self.Tp = Tp
        self.Prob = Prob

    def write_samples(self, write_prob = False, gdict = {}):
        fout = file("dlcsamples.txt", "w")
        for key in gdict:
            fout.write("%s " % key)
        fout.write("Vhub WaveDir Hs Tp")
        if (write_prob):
            fout.write(" Prob")
        fout.write("\n")
        for i in range(len(self.Vhub)):
            for key in gdict:
                fout.write("%e " % gdict[key])
            fout.write("%.16e %.16e %.16e %.16e" % (self.Vhub[i], self.WaveDir[i], self.Hs[i], self.Tp[i]))
            if (write_prob):
#                y = [self.Vhub[i], self.WaveDir[i], self.Hs[i], self.Tp[i]]
#                s = ["%.2f" % yf for yf in y]
#                x = [float(ss) for ss in s]
#                p2 = self.calc_prob(x)
#                p3 = self.calc_prob(y)
                fout.write(" %.16e" % (self.Prob[i]))
            fout.write("\n")
        fout.close()


    def calc_prob(self, x):
        v=x[0]
        pv = prob_weibull(v, 2.120, 9.767)
        if (self.dim == 1):
            return pv
        if (v>= self.Vbounds[0] and v<=self.Vbounds[1]):
            wd = x[1]
            k = self.WindDirKappaTab(v)
            l = self.WindDirLocTab(v)
            pwd = prob_vonmises(wd, k, l)
            if (self.dim == 2):
                prob = pv * pwd
#                print v, k, l, wd, pv, pwd, prob
                return prob
            else:
                hg = x[2]
                tg = x[3]
                hshape = self.HsShapeTab(v,wd)
                hscale = self.HsScaleTab(v,wd)
                if (hshape > 0 and hscale > 0): 
                    phg = prob_gamma(hg, hshape, hscale)
                tshape = self.TpShapeTab(v,wd)
                tscale = self.TpScaleTab(v,wd)
                if (tshape > 0 and tscale > 0): 
                    ptg = prob_gamma(tg, tshape, tscale)

                if (hshape > 0 and hscale > 0 and tshape > 0 and tscale > 0): 
                    if (hg >= self.HsBounds[0] and hg <=self.HsBounds[1] and
                        tg >= self.TpBounds[0] and tg <=self.TpBounds[1] and
                        wd >= self.WindDirBounds[0] and wd <= self.WindDirBounds[1]):
                        # finally we have a sample with nonzero prob.
                            prob = pv*pwd*phg*ptg
                            return prob[0]
#        print "returning 0 prob, out of bounds ", x
        return 0

def get_options():
    from optparse import OptionParser
    parser = OptionParser()    
    parser.add_option("-p", "--writeprob", dest="writeprob", help="include prob in sample list", action="store_true", default=False)
    
    (options, args) = parser.parse_args()
    return options, args



if __name__=="__main__":
    ctx = Context()
    options, args = get_options()
    V = 13
    k = ctx.WindDirKappaTab(V)
    l = ctx.WindDirLocTab(V)
#    print "test:"
#    print "v k loc"
#    print V, k,l

    print ctx.Vbounds

    ns  = 4
    ctx.sample(ns)


#    print "Vhub= " , mean(Vhub), Vhub 
#    print "WaveDir= ", mean(WaveDir), WaveDir
#    print "Hs= ", mean(Hs), Hs
#    print "Tp= ", mean(Tp), Tp
    print "\nSampled %d times,   overall mean, min, max:" % ns
    print "Vhub= " , mean(ctx.Vhub), min(ctx.Vhub), max(ctx.Vhub) 
    print "WaveDir= ", mean(ctx.WaveDir), min(ctx.WaveDir), max(ctx.WaveDir)
    print "Hs= ", mean(ctx.Hs), min(ctx.Hs), max(ctx.Hs)
    print "Tp= ", mean(ctx.Tp), min(ctx.Tp), max(ctx.Tp)


    global_dict = {'AnalTime': 12}
    ctx.write_samples(write_prob = options.writeprob, gdict=global_dict)


