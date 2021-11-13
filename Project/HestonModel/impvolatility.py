import numpy as np
from calcbsimpvol import calcbsimpvol
S = np.asarray(1.1452) # underlying
K = np.asarray([1.1100]) # strike
tau = np.asarray([21/365]) # time to maturity
r = np.asarray(.583) # interest
q = np.asarray(.72) # 외국
cp = np.asarray(1) # option
P = np.asarray([0.04670]) # 시장가

imp_vol = calcbsimpvol(dict(cp=cp, P=P, S=S, K=K, tau=tau, r=r, q=q))
print(imp_vol)
