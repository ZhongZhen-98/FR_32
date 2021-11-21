# http://gouthamanbalaraman.com/blog/heston-calibration-scipy-optimize-quantlib-python.html

import QuantLib as ql
from math import pow, sqrt
import numpy as np
from scipy.optimize import root, least_squares
from scipy.integrate import simps, cumtrapz, romb


day_count = ql.Actual365Fixed()
calendar = ql.UnitedStates()
calculation_date = ql.Date(18, 11, 2021)
maturity_date = ql.Date(3, 12, 2021)
spot_price = 1.13370
strike_price = 1.1650
option_type = ql.Option.Call
ql.Settings.instance().evaluationDate = calculation_date

risk_free_rate = 0.0005
foreign_rate = -0.00558
yield_ts = ql.YieldTermStructureHandle(
    ql.FlatForward(calculation_date, risk_free_rate, day_count))
foreignrate_ts = ql.YieldTermStructureHandle(
    ql.FlatForward(calculation_date, foreign_rate, day_count))

expiration_dates = [ql.Date(3,12,2021), ql.Date(7,1,2022),
                    ql.Date(4,2,2022), ql.Date(4,3,2022), ql.Date(8,4,2022), 
                    ql.Date(6,5,2022), ql.Date(3,6,2022), ql.Date(8,7,2022),
                    ql.Date(5,8,2022), ql.Date(9,9,2022), ql.Date(7,10,2022), 
                    ql.Date(4,11,2022)]

strikes = [1.10000, 1.11000, 1.12000, 1.13000, 1.14000, 1.15000, 1.16000, 1.17000, 1.18000, 1.19000, 1.20000]
data = [
[0.0259, 0.0636, 0.0628, 0.0649, 0.0620, 0.0651, 0.0655, 0.0818, 0.0787, 0.0943, 0.1067],
[0.0653, 0.0597, 0.0627, 0.0612, 0.0600, 0.0607, 0.0620, 0.0624, 0.0628, 0.0682, 0.0741],
[0.0647, 0.0641, 0.0625, 0.0613, 0.0598, 0.0596, 0.0593, 0.0612, 0.0628, 0.0645, 0.0679],
[0.0644, 0.0630, 0.0614, 0.0598, 0.0593, 0.0593, 0.0588, 0.0605, 0.0601, 0.0614, 0.0645],
[0.0650, 0.0631, 0.0619, 0.0603, 0.0595, 0.0590, 0.0588, 0.0594, 0.0593, 0.0610, 0.0624],
[0.0675, 0.0659, 0.0643, 0.0627, 0.0618, 0.0609, 0.0606, 0.0605, 0.0610, 0.0622, 0.0628],
[0.0664, 0.0649, 0.0634, 0.0621, 0.0609, 0.0605, 0.0601, 0.0605, 0.0608, 0.0610, 0.0618],
[0.0697, 0.0675, 0.0659, 0.0640, 0.0627, 0.0618, 0.0610, 0.0609, 0.0611, 0.0617, 0.0622],
[0.0687, 0.0670, 0.0650, 0.0637, 0.0623, 0.0613, 0.0610, 0.0608, 0.0610, 0.0612, 0.0618],
[0.0678, 0.0659, 0.0644, 0.0630, 0.0622, 0.0613, 0.0609, 0.0585, 0.0606, 0.0609, 0.0614],
[0.0660, 0.0646, 0.0631, 0.0621, 0.0610, 0.0603, 0.0598, 0.0596, 0.0597, 0.0602, 0.0606],
[0.0655, 0.0640, 0.0627, 0.0616, 0.0607, 0.0601, 0.0596, 0.0595, 0.0596, 0.0600, 0.0603]]

def setup_helpers(engine, expiration_dates, strikes, 
                  data, ref_date, spot_price, yield_ts, 
                  dividend_ts):
    heston_helpers = []
    grid_data = []
    for i, date in enumerate(expiration_dates):
        for j, s in enumerate(strikes):
            t = (date - ref_date )
            p = ql.Period(t, ql.Days)
            vols = data[i][j]
            helper = ql.HestonModelHelper(
                p, calendar, spot_price, s, 
                ql.QuoteHandle(ql.SimpleQuote(vols)),
                yield_ts, dividend_ts)
            helper.setPricingEngine(engine)
            heston_helpers.append(helper)
            grid_data.append((date, s))
    return heston_helpers, grid_data

def cost_function_generator(model, helpers,norm=False):
    def cost_function(params):
        params_ = ql.Array(list(params))
        model.setParams(params_)
        error = [h.calibrationError() for h in helpers]
        if norm:
            return np.sqrt(np.sum(np.abs(error)))
        else:
            return error
    return cost_function

def calibration_report(helpers, grid_data, detailed=False):
    avg = 0.0
    if detailed:
        print("%15s %25s %15s %15s %20s" % (
            "Strikes", "Expiry", "Market Value", 
             "Model Value", "Relative Error (%)"))
        print("="*100)
    for i, opt in enumerate(helpers):
        err = (opt.modelValue()/opt.marketValue() - 1.0)
        date,strike = grid_data[i]
        if detailed:
            print("%15.2f %25s %14.5f %15.5f %20.7f " % (
                strike, str(date), opt.marketValue(), 
                opt.modelValue(), 
                100.0*(opt.modelValue()/opt.marketValue() - 1.0)))
        avg += abs(err)
    avg = avg*100.0/len(helpers)
    if detailed:
      print("-"*100)
    summary = "Average Abs Error (%%) : %5.9f" % (avg)
    print(summary)
    return avg

def setup_model(_yield_ts, _dividend_ts, _spot_price, 
                init_condition=(0.02,0.2,0.5,0.1,0.01)):
    theta, kappa, sigma, rho, v0 = init_condition
    process = ql.HestonProcess(_yield_ts, _dividend_ts, 
                           ql.QuoteHandle(ql.SimpleQuote(_spot_price)), 
                           v0, kappa, theta, sigma, rho)
    model = ql.HestonModel(process)
    engine = ql.AnalyticHestonEngine(model) 
    return model, engine

heston_model, heston_engine = setup_model(
    yield_ts, foreignrate_ts, spot_price, 
    init_condition=(0.005,10,0.05,0.1,0.005)
)
# init_condition=(0.02,1.0,0.5,0.1,0.01)
heston_helpers, grid_data = setup_helpers(
    heston_engine, expiration_dates, strikes, data,
    calculation_date, spot_price, yield_ts, foreignrate_ts
)
initial_condition = list(heston_model.params())

cost_function = cost_function_generator(heston_model, heston_helpers)

# print(np.isfinite(np.atleast_1d(cost_function(initial_condition)))) # sol 이 잘 되는지 확인 

sol = least_squares(cost_function, initial_condition)

theta, kappa, sigma, rho, v0 = heston_model.params()
print("theta = %f, kappa = %f, sigma = %f, rho = %f, v0 = %f" % \
    (theta, kappa, sigma, rho, v0))
error = calibration_report(heston_helpers, grid_data)

# construct the European Option
payoff = ql.PlainVanillaPayoff(option_type, strike_price)
exercise = ql.EuropeanExercise(maturity_date)
european_option = ql.VanillaOption(payoff, exercise)

## Heston Model Pricing
european_option.setPricingEngine(heston_engine)
h_price = european_option.NPV()
print("The Heston model price is",h_price)
