## NOTE http://gouthamanbalaraman.com/blog/valuing-european-option-heston-model-quantLib.html

import QuantLib as ql
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import simps, cumtrapz, romb

# option data
maturity_date = ql.Date(3, 12, 2021)
spot_price = 11597.5 
strike_price = 10600.0 
# volatility = 0.20 
dividend_rate =  0.0 
option_type = ql.Option.Call
risk_free_rate = 0.001 
day_count = ql.Actual365Fixed()
calendar = ql.UnitedStates()
calculation_date = ql.Date(2, 11, 2021) # 평가 기준일
ql.Settings.instance().evaluationDate = calculation_date
# construct the European Option
payoff = ql.PlainVanillaPayoff(option_type, strike_price)
exercise = ql.EuropeanExercise(maturity_date)
european_option = ql.VanillaOption(payoff, exercise)
# construct the Heston process
v0 = .0104529950 
kappa = 0.859031
theta = 0.285867
sigma = 2.616803
rho = -0.168253

spot_handle = ql.QuoteHandle(ql.SimpleQuote(spot_price))
flat_ts = ql.YieldTermStructureHandle(ql.FlatForward(calculation_date, risk_free_rate, day_count))
dividend_yield = ql.YieldTermStructureHandle(ql.FlatForward(calculation_date, dividend_rate, day_count))
heston_process = ql.HestonProcess(flat_ts,
                                  dividend_yield,
                                  spot_handle,
                                  v0,
                                  kappa,
                                  theta,
                                  sigma,
                                  rho)

## Heston Model Pricing
engine = ql.AnalyticHestonEngine(ql.HestonModel(heston_process),0.1, 1000)
european_option.setPricingEngine(engine)
h_price = european_option.NPV()
print(strike_price)
print("The Heston model price is",h_price)

## Black Scholes Pricing
flat_vol_ts = ql.BlackVolTermStructureHandle(
    ql.BlackConstantVol(calculation_date, calendar, volatility, day_count)
)
bsm_process = ql.BlackScholesMertonProcess(spot_handle, 
                                           dividend_yield, 
                                           flat_ts, 
                                           flat_vol_ts)
european_option.setPricingEngine(ql.AnalyticEuropeanEngine(bsm_process))
bs_price = european_option.NPV()
print("The Black-Scholes-Merton model price is ", bs_price)
