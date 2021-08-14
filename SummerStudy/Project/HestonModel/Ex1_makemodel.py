## NOTE http://gouthamanbalaraman.com/blog/valuing-european-option-heston-model-quantLib.html

import QuantLib as ql
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import simps, cumtrapz, romb
import math

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

# construct the European Option
payoff = ql.PlainVanillaPayoff(option_type, strike_price)
exercise = ql.EuropeanExercise(maturity_date)
european_option = ql.VanillaOption(payoff, exercise)

# construct the Heston process
## NOTE 이 부분은 어디서 가지고 오는 내용인가? 
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

## Heston Model로 실행해 본 가격
engine = ql.AnalyticHestonEngine(ql.HestonModel(heston_process),0.01, 1000)
european_option.setPricingEngine(engine)
h_price = european_option.NPV()
print("The Heston model price is",h_price)
## NOTE 가격이 의미하는 것은?

## 블랙숄즈로 계산한 가격
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
