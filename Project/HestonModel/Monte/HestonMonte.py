# https://blog.quantinsti.com/heston-model/

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime 
import random
from math import sqrt, exp
import QuantLib as ql


# set the style for graphs
plt.rcParams["figure.figsize"] = (10, 7)
plt.style.use('seaborn-darkgrid')

# Payoff function inputs are option type and strike price
strike_price = 100
option_type = ql.Option.Call

call_payoff = ql.PlainVanillaPayoff(option_type, strike_price) 

# Exercise function takes maturity date of the option as input
day_count = ql.Actual365Fixed()
calendar = ql.UnitedStates()
maturity = ql.Date(3, 8, 2021)
today = ql.Date(4, 8,2020)

call_exercise = ql.EuropeanExercise(maturity)

# Function inputs are striked type payoff and exercise
option = ql.VanillaOption(call_payoff, call_exercise)

# Option input values
spot_price = 105
strike_price = 100
yearly_historical_volatility = 0.1
riskfree_rate = 0.0
dividend = 0

variance = 0.01 # Initial variance is square of volatility
kappa = 2       # Speed of mean reversion 
theta = 0.01    # Long-run variance
epsilon = 0.1   # Volatility of volatility
rho = 0.0       # Correlation  

initial_value = ql.QuoteHandle(ql.SimpleQuote(spot_price))

# Setting up flat risk free curves
discount_curve = ql.YieldTermStructureHandle(ql.FlatForward(today, riskfree_rate,day_count))
dividend_yield = ql.YieldTermStructureHandle(ql.FlatForward(today, dividend, day_count))

heston_process = ql.HestonProcess(discount_curve,dividend_yield, initial_value,variance,kappa,theta,epsilon,rho)

# Inputs used for the engine are model, Tolerance level, maximum evaluations
engine = ql.AnalyticHestonEngine(ql.HestonModel(heston_process),0.001,1000)
option.setPricingEngine(engine)
price = option.NPV()
print ("option_price", round(price,2))

# Montecarlo simulation
random.seed(5000)# Set the random seed
N = 1000         # Number of small sub-steps (time)
n = 100000       # Number of Monte carlo paths

S_0 = 105       # Initial stock price
K = 100         # Strike price 
V_0 = 0.01      # Initial variance is square of volatility
kappa = 2       # kappa mean reversion speed
theta = 0.01    # Long-run variance
epsilon = 0.1   # volatility of volatility
rho = 0         # correlation 
T = 1           # time to maturity
dt = T/N        # No. of Time step

# Parameters for Heston process
variance = 0.01 # Initial variance is square of volatility
kappa = 2       # Speed of mean reversion 
theta = 0.01    # Long-run variance
epsilon = 0.1   # Volatility of volatility
rho = 0.0       # Correlation  

# Integrate equations: Euler method, Montecarlo vectorized
V_t = np.ones(n) * V_0
S_t = np.ones(n) * S_0

# Generate Montecarlo paths
for t in range(1,N):  
  # Random numbers for S_t and V_t 
  Z_s = np.random.normal(size=n) 
  Z_v = rho * Z_s + np.sqrt(1 - rho**2) * np.random.normal(size=n) 

  # Euler integration
  V_t = np.maximum(V_t, 0)
  S_t = S_t * np.exp( np.sqrt(V_t * dt) * Z_s - V_t * dt / 2)                     # Stock price process
  V_t = V_t + kappa * (theta - V_t) * dt + epsilon * np.sqrt(V_t * dt) * Z_v      # Volatility process

option_price = np.mean(np.maximum(S_t - K, 0))

print(round(option_price,3))