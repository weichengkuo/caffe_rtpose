from joblib import Parallel, delayed
import pdb

def run(x):
  return x,x*x

r = Parallel(n_jobs=5)(delayed(run)(x) for x in xrange(100))
print(r)
pdb.set_trace()
