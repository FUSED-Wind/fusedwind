from openruniec import final_load_calc as flc
import sampler
sctx = sampler.Context()
[cnt,lsum,psum] = flc(sctx, "dlcproto.out", True, 20)
