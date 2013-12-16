

from openruniec import test_convergence


test_convergence("dlcproto.5000samples.out", False, 100, 5000, 50)
test_convergence("dlcproto.5148scan.out", True, 150, 5150, 50)




