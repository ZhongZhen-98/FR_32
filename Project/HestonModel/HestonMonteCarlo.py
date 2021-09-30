# http://gouthamanbalaraman.com/blog/variance-reduction-hull-white-quantlib.html

import QuantLib as ql
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import cumtrapz

# option data
maturity_date = ql.Date(15, 1, 2016) # 만기일 (일, 월, 년) check
spot_price = 127.62 # 현물가격 check
strike_price = 130 # 행사가 check
volatility = 0.20 # the historical vols for a year 기초 주식의 변동성
dividend_rate =  0.0163 # 배당수익률
option_type = ql.Option.Call

risk_free_rate = 0.001 # 무위험 이자율
day_count = ql.Actual365Fixed()
calendar = ql.UnitedStates()

calculation_date = ql.Date(8, 5, 2015) # 평가 기준일
ql.Settings.instance().evaluationDate = calculation_date

payoff = ql.PlainVanillaPayoff(option_type, strike_price)
exercise = ql.EuropeanExercise(maturity_date)
european_option = ql.VanillaOption(payoff, exercise)

v0 = volatility*volatility  # spot variance
kappa = 0.1
theta = v0
sigma = 0.1
rho = -0.75

spot_handle = ql.QuoteHandle(
    ql.SimpleQuote(spot_price)
)
flat_ts = ql.YieldTermStructureHandle(
    ql.FlatForward(calculation_date, risk_free_rate, day_count)
)
dividend_yield = ql.YieldTermStructureHandle(
    ql.FlatForward(calculation_date, dividend_rate, day_count)
)
heston_process = ql.HestonProcess(flat_ts,
                                  dividend_yield,
                                  spot_handle,
                                  v0,
                                  kappa,
                                  theta,
                                  sigma,
                                  rho)

timestep = 360
length = 30 # in years

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

num_paths = 128
time, paths = generate_paths(num_paths, timestep)
for i in range(num_paths):
    plt.plot(time, paths[i, :], lw=0.8, alpha=0.6)
plt.title("Heston Model Short Rate Simulation")
plt.show()