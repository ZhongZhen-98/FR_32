import QuantLib as ql
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import cumtrapz

sigma = 0.01
a = 0.001
timestep = 360
length = 30 # in years
forward_rate = 0.05
day_count = ql.Thirty360()
todays_date = ql.Date(15, 1, 2015)

ql.Settings.instance().evaluationDate = todays_date

yield_curve = ql.FlatForward(
  todays_date, 
  ql.QuoteHandle(ql.SimpleQuote(forward_rate)), 
  day_count)
spot_curve_handle = ql.YieldTermStructureHandle(yield_curve)

hw_process = ql.HullWhiteProcess(spot_curve_handle, a, sigma)
rng = ql.GaussianRandomSequenceGenerator(
    ql.UniformRandomSequenceGenerator(
        timestep, 
        ql.UniformRandomGenerator(125)))
seq = ql.GaussianPathGenerator(hw_process, length, timestep, rng, False)

def generate_paths(num_paths, timestep):
    arr = np.zeros((num_paths, timestep+1))
    for i in range(num_paths):
        sample_path = seq.next()
        path = sample_path.value()
        time = [path.time(j) for j in range(len(path))]
        value = [path[j] for j in range(len(path))]
        arr[i, :] = np.array(value)
    return np.array(time), arr

num_paths = 128
time, paths = generate_paths(num_paths, timestep)
for i in range(num_paths):
    plt.plot(time, paths[i, :], lw=0.8, alpha=0.6)
plt.title("Hull-White Short Rate Simulation")
plt.show()

def stoch_df(paths, time):
    return np.mean(
        np.exp(-cumtrapz(paths, time, initial=0.)),axis=0
    )
B_emp = stoch_df(paths, time)
logB_emp = np.log(B_emp)
B_yc = np.array([yield_curve.discount(t) for t in time])
logB_yc = np.log(B_yc)

deltaT = time[1:] - time[:-1]
deltaB_emp = logB_emp[1:]-logB_emp[:-1]
deltaB_yc = logB_yc[1:] - logB_yc[:-1]

new_paths = paths.copy()
new_paths[:,1:] += (deltaB_emp/deltaT - deltaB_yc/deltaT)

plt.plot(time,
         stoch_df(paths, time),"r-.", 
         label="Original", lw=2)
plt.plot(time,
         stoch_df(new_paths, time),"g:",
         label="Corrected", lw=2)
plt.plot(time,B_yc, "k--",label="Market", lw=1)
plt.title("Zero Coupon Bond Price")
plt.legend()
plt.show()

def alpha(forward, sigma, a, t):
    return forward + 0.5* np.power(sigma/a*(1.0 - np.exp(-a*t)), 2)

avg = [np.mean(paths[:, i]) for i in range(timestep+1)]
new_avg = [np.mean(new_paths[:, i]) for i in range(timestep+1)]
plt.plot(time, avg, "r-.", lw=3, alpha=0.6, label="Original")
plt.plot(time, new_avg, "g:", lw=3, alpha=0.6, label="Corrected")
plt.plot(time,alpha(forward_rate, sigma, a, time), "k--", lw=2, alpha=0.6, label="Model")
plt.title("Mean of Short Rates")
plt.legend(loc=0)
plt.show()