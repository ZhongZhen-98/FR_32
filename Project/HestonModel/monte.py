import QuantLib as ql
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import cumtrapz

v0 = 1  # spot variance
kappa = 9
theta = v0
sigma = 0.3
rho = -0.5
risk_free_rate = 0.001 # 무위험 이자율
dividend_rate =  0.0163 # 배당수익률

a = 0.001
timestep = 360
length = 50 # in years
forward_rate = 1
day_count = ql.Thirty360()
todays_date = ql.Date(12, 8, 2021)

ql.Settings.instance().evaluationDate = todays_date

yield_curve = ql.FlatForward(
    todays_date, 
    ql.QuoteHandle(ql.SimpleQuote(forward_rate)), 
    day_count)
spot_curve_handle = ql.YieldTermStructureHandle(yield_curve)

flat_ts = ql.YieldTermStructureHandle(
    ql.FlatForward(todays_date, risk_free_rate, day_count)
)
dividend_yield = ql.YieldTermStructureHandle(
    ql.FlatForward(todays_date, dividend_rate, day_count)
)
heston_process = ql.HestonProcess(flat_ts, dividend_yield, spot_curve_handle, v0, kappa, theta, sigma, rho)
                                
# hw_process = ql.HullWhiteProcess(spot_curve_handle, a, sigma)
rng = ql.GaussianRandomSequenceGenerator(
    ql.UniformRandomSequenceGenerator(
        timestep, 
        ql.UniformRandomGenerator(125)))
seq = ql.GaussianPathGenerator(heston_process, length, timestep, rng, False)

def generate_paths(num_paths, timestep):
    arr = np.zeros((num_paths, timestep+1))
    for i in range(num_paths):
        sample_path = seq.next()
        path = sample_path.value()
        time = [path.time(j) for j in range(len(path))]
        value = [path[j] for j in range(len(path))]
        arr[i, :] = np.array(value)
    return np.array(time), arr

num_paths = 12
time, paths = generate_paths(num_paths, timestep)
for i in range(num_paths):
    plt.plot(time, paths[i, :], lw=0.8, alpha=0.6)
plt.title("Hull-White Short Rate Simulation")
plt.show()