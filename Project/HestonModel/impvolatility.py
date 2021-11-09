import numpy as np
from calcbsimpvol import calcbsimpvol
S = np.asarray(268.55)
K = np.asarray([275.0])
tau = np.asarray([9/365])
r = np.asarray(0.01)
q = np.asarray(0.00)
cp = np.asarray(1)
P = np.asarray([0.31])

imp_vol = calcbsimpvol(dict(cp=cp, P=P, S=S, K=K, tau=tau, r=r, q=q))
print(imp_vol)