# http://gouthamanbalaraman.com/blog/heston-calibration-scipy-optimize-quantlib-python.html

import QuantLib as ql
from math import pow, sqrt
import numpy as np
from scipy.optimize import root

day_count = ql.Actual365Fixed()
calendar = ql.UnitedStates()
calculation_date = ql.Date(18, 11, 2021)

spot = 1.13370
ql.Settings.instance().evaluationDate = calculation_date

risk_free_rate = 0.0005
dividend_rate = -0.00558
yield_ts = ql.YieldTermStructureHandle(
    ql.FlatForward(calculation_date, risk_free_rate, day_count))
dividend_ts = ql.YieldTermStructureHandle(
    ql.FlatForward(calculation_date, dividend_rate, day_count))

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
    summary = "Average Abs Error (%%) : %5.9f" % (avg)
    print(summary)
    return avg

def setup_model(_yield_ts, _dividend_ts, _spot, 
                init_condition=(0.02,0.2,0.5,0.1,0.01)):
    theta, kappa, sigma, rho, v0 = init_condition
    process = ql.HestonProcess(_yield_ts, _dividend_ts, 
                           ql.QuoteHandle(ql.SimpleQuote(_spot)), 
                           v0, kappa, theta, sigma, rho)
    model = ql.HestonModel(process)
    engine = ql.AnalyticHestonEngine(model) 
    return model, engine
summary= []


model1, engine1 = setup_model(
    yield_ts, dividend_ts, spot, 
    init_condition=(0.02,0.2,0.5,0.1,0.01))
heston_helpers1, grid_data1 = setup_helpers(
    engine1, expiration_dates, strikes, data, 
    calculation_date, spot, yield_ts, dividend_ts
)
initial_condition = list(model1.params())

lm = ql.LevenbergMarquardt(1e-8, 1e-8, 1e-8)
model1.calibrate(heston_helpers1, lm, 
                 ql.EndCriteria(500, 300, 1.0e-8,1.0e-8, 1.0e-8))
theta, kappa, sigma, rho, v0 = model1.params()
print("theta = %f, kappa = %f, sigma = %f, rho = %f, v0 = %f" % \
    (theta, kappa, sigma, rho, v0))
error = calibration_report(heston_helpers1, grid_data1)
summary.append(["QL LM1", error] + list(model1.params()))

model1, engine1 = setup_model(
    yield_ts, dividend_ts, spot, 
    init_condition=(0.07,0.5,0.1,0.1,0.1))
heston_helpers1, grid_data1 = setup_helpers(
    engine1, expiration_dates, strikes, data, 
    calculation_date, spot, yield_ts, dividend_ts
)
initial_condition = list(model1.params())

lm = ql.LevenbergMarquardt(1e-8, 1e-8, 1e-8)
model1.calibrate(heston_helpers1, lm, 
                 ql.EndCriteria(500, 300, 1.0e-8,1.0e-8, 1.0e-8))
theta, kappa, sigma, rho, v0 = model1.params()
print("theta = %f, kappa = %f, sigma = %f, rho = %f, v0 = %f" % \
    (theta, kappa, sigma, rho, v0))
error = calibration_report(heston_helpers1, grid_data1)
summary.append(["QL LM2", error] + list(model1.params()))

model2, engine2 = setup_model(
    yield_ts, dividend_ts, spot, 
    init_condition=(0.02,0.2,0.5,0.1,0.01))
heston_helpers2, grid_data2 = setup_helpers(
    engine2, expiration_dates, strikes, data,
    calculation_date, spot, yield_ts, dividend_ts
)
initial_condition = list(model2.params())

cost_function = cost_function_generator(model2, heston_helpers2)
sol = root(cost_function, initial_condition, method='lm')
theta, kappa, sigma, rho, v0 = model2.params()
print("theta = %f, kappa = %f, sigma = %f, rho = %f, v0 = %f" % \
    (theta, kappa, sigma, rho, v0))
error = calibration_report(heston_helpers2, grid_data2)
summary.append(["Scipy LM1", error] + list(model2.params()))

model2, engine2 = setup_model(
    yield_ts, dividend_ts, spot,
    init_condition=(0.07,0.5,0.1,0.1,0.1))
heston_helpers2, grid_data2 = setup_helpers(
    engine2, expiration_dates, strikes, data,
    calculation_date, spot, yield_ts, dividend_ts
)
initial_condition = list(model2.params())

cost_function = cost_function_generator(model2, heston_helpers2)
sol = root(cost_function, initial_condition, method='lm')
theta, kappa, sigma, rho, v0 = model2.params()
print("theta = %f, kappa = %f, sigma = %f, rho = %f, v0 = %f" % \
    (theta, kappa, sigma, rho, v0))
error = calibration_report(heston_helpers2, grid_data2)
summary.append(["Scipy LM2", error] + list(model2.params()))

from scipy.optimize import least_squares

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
error = calibration_report(heston_helpers3, grid_data3)
summary.append(["Scipy LS1", error] + list(model3.params()))

model3, engine3 = setup_model(
    yield_ts, dividend_ts, spot, 
    init_condition=(0.07,0.5,0.1,0.1,0.1))
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
error = calibration_report(heston_helpers3, grid_data3)
summary.append(["Scipy LS2", error] + list(model3.params()))

from scipy.optimize import differential_evolution

model4, engine4 = setup_model(yield_ts, dividend_ts, spot)
heston_helpers4, grid_data4 = setup_helpers(
    engine4, expiration_dates, strikes, data,
    calculation_date, spot, yield_ts, dividend_ts
)
initial_condition = list(model4.params())
bounds = [(0,1),(0.01,15), (0.01,1.), (-1,1), (0,1.0) ]

cost_function = cost_function_generator(
    model4, heston_helpers4, norm=True)
sol = differential_evolution(cost_function, bounds, maxiter=100)
theta, kappa, sigma, rho, v0 = model4.params()
print("theta = %f, kappa = %f, sigma = %f, rho = %f, v0 = %f" % \
     (theta, kappa, sigma, rho, v0))
error = calibration_report(heston_helpers4, grid_data4)
summary.append(["Scipy DE1", error] + list(model4.params()))

model4, engine4 = setup_model(yield_ts, dividend_ts, spot)
heston_helpers4, grid_data4 = setup_helpers(
    engine4, expiration_dates, strikes, data,
    calculation_date, spot, yield_ts, dividend_ts
)
initial_condition = list(model4.params())
bounds = [(0,1),(0.01,15), (0.01,1.), (-1,1), (0,1.0) ]

cost_function = cost_function_generator(
    model4, heston_helpers4, norm=True)
sol = differential_evolution(cost_function, bounds, maxiter=100)
theta, kappa, sigma, rho, v0 = model4.params()
print("theta = %f, kappa = %f, sigma = %f, rho = %f, v0 = %f" % \
     (theta, kappa, sigma, rho, v0))
error = calibration_report(heston_helpers4, grid_data4)
summary.append(["Scipy DE2", error] + list(model4.params()))

from scipy.optimize import basinhopping

class MyBounds(object):
     def __init__(self, xmin=[0.,0.01,0.01,-1,0], xmax=[1,15,1,1,1.0] ):
         self.xmax = np.array(xmax)
         self.xmin = np.array(xmin)
     def __call__(self, **kwargs):
         x = kwargs["x_new"]
         tmax = bool(np.all(x <= self.xmax))
         tmin = bool(np.all(x >= self.xmin))
         return tmax and tmin
bounds = [(0,1),(0.01,15), (0.01,1.), (-1,1), (0,1.0) ]

model5, engine5 = setup_model(
    yield_ts, dividend_ts, spot,
    init_condition=(0.02,0.2,0.5,0.1,0.01))
heston_helpers5, grid_data5 = setup_helpers(
    engine5, expiration_dates, strikes, data,
    calculation_date, spot, yield_ts, dividend_ts
)
initial_condition = list(model5.params())

mybound = MyBounds()
minimizer_kwargs = {"method": "L-BFGS-B", "bounds": bounds }
cost_function = cost_function_generator(
    model5, heston_helpers5, norm=True)
sol = basinhopping(cost_function, initial_condition, niter=5,
                   minimizer_kwargs=minimizer_kwargs,
                   stepsize=0.005,
                   accept_test=mybound,
                   interval=10)
theta, kappa, sigma, rho, v0 = model5.params()
print("theta = %f, kappa = %f, sigma = %f, rho = %f, v0 = %f" % \
    (theta, kappa, sigma, rho, v0))
error = calibration_report(heston_helpers5, grid_data5)
summary.append(["Scipy BH1", error] + list(model5.params()))

model5, engine5 = setup_model(
    yield_ts, dividend_ts, spot,
    init_condition=(0.07,0.5,0.1,0.1,0.1))
heston_helpers5, grid_data5 = setup_helpers(
    engine5, expiration_dates, strikes, data,
    calculation_date, spot, yield_ts, dividend_ts
)
initial_condition = list(model5.params())

mybound = MyBounds()
minimizer_kwargs = {"method": "L-BFGS-B", "bounds": bounds}
cost_function = cost_function_generator(
    model5, heston_helpers5, norm=True)
sol = basinhopping(cost_function, initial_condition, niter=5,
                   minimizer_kwargs=minimizer_kwargs,
                   stepsize=0.005,
                   accept_test=mybound,
                   interval=10)
theta, kappa, sigma, rho, v0 = model5.params()
print("theta = %f, kappa = %f, sigma = %f, rho = %f, v0 = %f" % \
    (theta, kappa, sigma, rho, v0))
error = calibration_report(heston_helpers5, grid_data5)
summary.append(["Scipy BH2", error] + list(model5.params()))

from pandas import DataFrame
DataFrame(
    summary,
    columns=["Name", "Avg Abs Error","Theta", "Kappa", "Sigma", "Rho", "V0"],
    index=['']*len(summary))