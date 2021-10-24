# http://gouthamanbalaraman.com/blog/heston-calibration-scipy-optimize-quantlib-python.html

import QuantLib as ql
from math import pow, sqrt
import numpy as np
from scipy.optimize import least_squares

def setup_model(_yield_ts, _dividend_ts, _spot, 
                init_condition=(0.02,0.2,0.5,0.1,0.01)):
    theta, kappa, sigma, rho, v0 = init_condition
    process = ql.HestonProcess(_yield_ts, _dividend_ts, 
                           ql.QuoteHandle(ql.SimpleQuote(_spot)), 
                           v0, kappa, theta, sigma, rho)
    model = ql.HestonModel(process)
    engine = ql.AnalyticHestonEngine(model) 
    return model, engine

def setup_helpers(engine, expiration_dates, strikes, 
                  data, ref_date, spot, yield_ts, 
                  dividend_ts):
    heston_helpers = []
    grid_data = []
    for i, date in enumerate(expiration_dates):
        for j, s in enumerate(strikes):
            t = (date - ref_date )
            p = ql.Period(t, ql.Days)
            vols = data[i][j]
            helper = ql.HestonModelHelper(
                p, calendar, spot, s, 
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
    print("Average Abs Error (%%) : %5.9f" % (avg))
    return avg

# EUR/USD 옵션: 날짜 계산 방법
day_count = ql.Actual365Fixed()
calendar = ql.UnitedStates()
calculation_date = ql.Date(25, 10, 2021)

spot = 11656.5
ql.Settings.instance().evaluationDate = calculation_date

risk_free_rate = 0.01
dividend_rate = 0.0
yield_ts = ql.YieldTermStructureHandle(
    ql.FlatForward(calculation_date, risk_free_rate, day_count))
dividend_ts = ql.YieldTermStructureHandle(
    ql.FlatForward(calculation_date, dividend_rate, day_count))

# MATRIXXX
expiration_dates = [ql.Date(5,11,2021), ql.Date(3,12,2021), ql.Date(7,1,2022),
                    ql.Date(4,2,2022), ql.Date(4,3,2022), ql.Date(8,4,2022), 
                    ql.Date(6,5,2022), ql.Date(3,6,2022), ql.Date(8,7,2022),
                    ql.Date(5,8,2022), ql.Date(9,9,2022), ql.Date(7,10,2022), 
                    ql.Date(4,11,2022), ql.Date(9,12,2022), ql.Date(3,3,2023),
                    ql.Date(9,6,2023), ql.Date(8,9,2023)]

# https://www.cmegroup.com/markets/fx/g10/euro-fx.quotes.options.html#optionProductId=8116&strikeRange=ALL&expiration=8116-X1&overrideFuture=6EX1

strikes = [527.50, 560.46, 593.43, 626.40, 659.37, 692.34, 725.31, 758.28]
data = [
[0.37819, 0.34177, 0.30394, 0.27832, 0.26453, 0.25916, 0.25941, 0.26127],
[0.3445, 0.31769, 0.2933, 0.27614, 0.26575, 0.25729, 0.25228, 0.25202],
[0.37419, 0.35372, 0.33729, 0.32492, 0.31601, 0.30883, 0.30036, 0.29568],
[0.37498, 0.35847, 0.34475, 0.33399, 0.32715, 0.31943, 0.31098, 0.30506],
[0.35941, 0.34516, 0.33296, 0.32275, 0.31867, 0.30969, 0.30239, 0.29631],
[0.35521, 0.34242, 0.33154, 0.3219, 0.31948, 0.31096, 0.30424, 0.2984],
[0.35442, 0.34267, 0.33288, 0.32374, 0.32245, 0.31474, 0.30838, 0.30283],
[0.35384, 0.34286, 0.33386, 0.32507, 0.3246, 0.31745, 0.31135, 0.306],
[0.35338, 0.343, 0.33464, 0.32614, 0.3263, 0.31961, 0.31371, 0.30852],
[0.35301, 0.34312, 0.33526, 0.32698, 0.32766, 0.32132, 0.31558, 0.31052],
[0.35272, 0.34322, 0.33574, 0.32765, 0.32873, 0.32267, 0.31705, 0.31209],
[0.35246, 0.3433, 0.33617, 0.32822, 0.32965, 0.32383, 0.31831, 0.31344],
[0.35226, 0.34336, 0.33651, 0.32869, 0.3304, 0.32477, 0.31934, 0.31453],
[0.35207, 0.34342, 0.33681, 0.32911, 0.33106, 0.32561, 0.32025, 0.3155],
[0.35171, 0.34327, 0.33679, 0.32931, 0.3319, 0.32665, 0.32139, 0.31675],
[0.35128, 0.343, 0.33658, 0.32937, 0.33276, 0.32769, 0.32255, 0.31802],
[0.35086, 0.34274, 0.33637, 0.32943, 0.3336, 0.32872, 0.32368, 0.31927]]



model3, engine3 = setup_model(
    yield_ts, dividend_ts, spot, 
    init_condition=(0.02,0.2,0.5,0.1,0.01))
heston_helpers3, grid_data3 = setup_helpers(
    engine3, expiration_dates, strikes, data,
    calculation_date, spot, yield_ts, dividend_ts
)
initial_condition = list(model3.params())

cost_function = cost_function_generator(model3, heston_helpers3)
sol = least_squares(cost_function, initial_condition)
theta, kappa, sigma, rho, v0 = model3.params()
print("theta = %f, kappa = %f, sigma = %f, rho = %f, v0 = %f" % \
    (theta, kappa, sigma, rho, v0))
error = calibration_report(heston_helpers3, grid_data3, detailed=0)

# ## 여기는 필요할까. Pricing
# maturity_date = ql.Date(15, 1, 2016) # 만기일 (일, 월, 년) check
# strike_price = 130 # 행사가 check
# option_type = ql.Option.Call
# payoff = ql.PlainVanillaPayoff(option_type, strike_price)
# exercise = ql.EuropeanExercise(maturity_date)
# european_option = ql.VanillaOption(payoff, exercise)
# european_option.setPricingEngine(engine3)
# h_price = european_option.NPV()
# print("The Heston model price is",h_price)