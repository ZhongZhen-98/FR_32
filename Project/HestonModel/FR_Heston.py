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
calculation_date = ql.Date(1, 11, 2021)

spot = 11580.5
ql.Settings.instance().evaluationDate = calculation_date

risk_free_rate = 0.0
dividend_rate = 0.0
yield_ts = ql.YieldTermStructureHandle(
    ql.FlatForward(calculation_date, risk_free_rate, day_count))
dividend_ts = ql.YieldTermStructureHandle(
    ql.FlatForward(calculation_date, dividend_rate, day_count))

# MATRIXXX
expiration_dates = [ql.Date(3,12,2021), ql.Date(7,1,2022),
                    ql.Date(4,2,2022), ql.Date(4,3,2022), ql.Date(8,4,2022), 
                    ql.Date(6,5,2022), ql.Date(3,6,2022), ql.Date(8,7,2022),
                    ql.Date(5,8,2022), ql.Date(9,9,2022), ql.Date(7,10,2022), 
                    ql.Date(9,12,2022), ql.Date(3,3,2023),
                    ql.Date(9,6,2023), ql.Date(8,9,2023)]

# https://www.cmegroup.com/markets/fx/g10/euro-fx.quotes.options.html#optionProductId=8116&strikeRange=ALL&expiration=8116-X1&overrideFuture=6EX1

strikes = [11000.0, 11100.0, 11200.0, 11300.0, 11400.0, 11500.0, 11600.0, 11700.0]
data = [
[0.0570, 0.0471, 0.0373, 0.0278, 0.0190, 0.0115, 0.0060, 0.0027],
[0.0601, 0.0504, 0.0409, 0.0319, 0.0236, 0.0164, 0.0105, 0.0063],
[0.0605, 0.0510, 0.0419, 0.0333, 0.0254, 0.0185, 0.0129, 0.0085],
[0.0611, 0.0519, 0.0430, 0.0346, 0.0270, 0.0202, 0.0146, 0.0101],
[0.0643, 0.0553, 0.0466, 0.0384, 0.0308, 0.0239, 0.0180, 0.0132],
[0.0657, 0.0569, 0.0485, 0.0405, 0.0331, 0.0264, 0.0205, 0.0155],
[0.0664, 0.0577, 0.0494, 0.0416, 0.0343, 0.0277, 0.0218, 0.0168],
[0.0699, 0.0613, 0.0530, 0.0451, 0.0377, 0.0310, 0.0251, 0.0199],
[0.0706, 0.0621, 0.0539, 0.0461, 0.0389, 0.0323, 0.0264, 0.0212],
[0.0713, 0.0629, 0.0549, 0.0473, 0.0402, 0.0337, 0.0278, 0.0226],
[0.0750, 0.0666, 0.0585, 0.0508, 0.0436, 0.0370, 0.0310, 0.0256],
[0.0765, 0.0683, 0.0604, 0.0529, 0.0459, 0.0394, 0.0334, 0.0281],
[0.0814, 0.0733, 0.0656, 0.0582, 0.0513, 0.0447, 0.0387, 0.0332],
[0.0872, 0.0792, 0.0715, 0.0642, 0.0572, 0.0507, 0.0445, 0.0389],
[0.0916, 0.0836, 0.0760, 0.0687, 0.0617, 0.0551, 0.0489, 0.0432]]


for i in range(len(data)):
  for j in range(len(data[i])):
    data[i][j] *=12500.0

model, engine = setup_model(
    yield_ts, dividend_ts, spot, 
    init_condition=(0.43,5,0.6,-0.5,0.5)) #dummy
heston_helpers, grid_data = setup_helpers(
    engine, expiration_dates, strikes, data,
    calculation_date, spot, yield_ts, dividend_ts
)
initial_condition = list(model.params())
cost_function = cost_function_generator(model, heston_helpers)
sol = least_squares(cost_function, initial_condition)
theta, kappa, sigma, rho, v0 = model.params()
print("theta = %f, kappa = %f, sigma = %f, rho = %f, v0 = %f" % \
    (theta, kappa, sigma, rho, v0))
error = calibration_report(heston_helpers, grid_data, detailed=0)