# http://gouthamanbalaraman.com/blog/heston-calibration-scipy-optimize-quantlib-python.html

import QuantLib as ql
from math import pow, sqrt
import numpy as np
from scipy.optimize import root, least_squares
from scipy.integrate import simps, cumtrapz, romb


day_count = ql.Actual365Fixed()
calendar = ql.UnitedStates()
calculation_date = ql.Date(15, 11, 2015)
maturity_date = ql.Date(3, 12, 2021)
spot_price = 1.14535
strike_price = 1.06000 
option_type = ql.Option.Call
ql.Settings.instance().evaluationDate = calculation_date

risk_free_rate = 0.0583
foreign_rate = 0.072
yield_ts = ql.YieldTermStructureHandle(
    ql.FlatForward(calculation_date, risk_free_rate, day_count))
foreignrate_ts = ql.YieldTermStructureHandle(
    ql.FlatForward(calculation_date, foreign_rate, day_count))

expiration_dates = [ql.Date(22,11,2021), ql.Date(29,11,2021), ql.Date(14,12,2021),
                    ql.Date(14,1,2022), ql.Date(14,2,2022), ql.Date(12,5,2022), 
                    ql.Date(14,11,2022)]
strikes = [1.1420, 1.1430, 1.1440, 1.1450, 1.1460, 1.1470, 1.1480, 1.1490]
data = [
[0.0537819, 0.0534177, 0.0530394, 0.0527832, 0.0526453, 0.0525916, 0.0525941, 0.5026127],
[0.0534450, 0.0531769, 0.0529330, 0.0527614, 0.0526575, 0.0525729, 0.0525228, 0.5025202],
[0.0537419, 0.0535372, 0.0533729, 0.0532492, 0.0531601, 0.0530883, 0.0530036, 0.5029568],
[0.0537498, 0.0535847, 0.0534475, 0.0533399, 0.0532715, 0.0531943, 0.0531098, 0.5030506],
[0.0535941, 0.0534516, 0.0533296, 0.0532275, 0.0531867, 0.0530969, 0.0530239, 0.5029631],
[0.0535521, 0.0534242, 0.0533154, 0.0532190, 0.0531948, 0.0531096, 0.0530424, 0.5029840],
[0.0535442, 0.0534267, 0.0533288, 0.0532374, 0.0532245, 0.0531474, 0.0530838, 0.5030283]]

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
    init_condition=(0.02,0.2,0.5,0.1,0.01)
)
heston_helpers, grid_data = setup_helpers(
    heston_engine, expiration_dates, strikes, data,
    calculation_date, spot_price, yield_ts, foreignrate_ts
)
initial_condition = list(heston_model.params())

cost_function = cost_function_generator(heston_model, heston_helpers)
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
