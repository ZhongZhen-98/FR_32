import QuantLib as ql
import pandas as pd

flat_ts = ql.YieldTermStructureHandle(
    ql.FlatForward(2, ql.NullCalendar(), 0.015, ql.Actual365NoLeap())
)
dividend_ts = ql.YieldTermStructureHandle(
    ql.FlatForward(2, ql.NullCalendar(), -0.0065, ql.Actual365NoLeap())
)
spot = 1.08417

# dummy parameters
v0 = 0.01; kappa = 0.2; theta = 0.02; rho = -0.75; sigma = 0.5;

process = ql.HestonProcess(flat_ts, dividend_ts, 
                           ql.QuoteHandle(ql.SimpleQuote(spot)), 
                           v0, kappa, theta, sigma, rho)
model = ql.HestonModel(process)
engine = ql.AnalyticHestonEngine(model)

heston_helpers = []

data = [
    [1.0953, 4.89],
    [1.111, 4.97],
    [1.1233, 5.12],
    [1.1404, 5.39],
    [1.1533, 5.595],
    [1.1745, 5.923]
]

tenor = ql.Period('6M')
for strike, vol in data:
    helper = ql.HestonModelHelper(tenor, ql.TARGET(), spot,
                                  strike, ql.QuoteHandle(ql.SimpleQuote(vol / 100)), flat_ts, dividend_ts )
    helper.setPricingEngine(engine)
    heston_helpers.append(helper)

lm = ql.LevenbergMarquardt(1e-8, 1e-8, 1e-8)
model.calibrate(heston_helpers, lm,  ql.EndCriteria(500, 50, 1.0e-8,1.0e-8, 1.0e-8))
theta, kappa, sigma, rho, v0 = model.params()

print(f"theta = {theta:.4f}, kappa = {kappa:.4f}, sigma = {sigma:.4f}, rho = {rho:.4f}, v0 = {v0:.4f}")

avg = 0.0

summary = []
for i, opt in enumerate(heston_helpers):
    err = (opt.modelValue()/opt.marketValue() - 1.0)
    summary.append((
        data[i][0], opt.marketValue(), 
        opt.modelValue(), 
        100.0*(opt.modelValue()/opt.marketValue() - 1.0)))
    avg += abs(err)
avg = avg*100.0/len(heston_helpers)

print("Average Abs Error (%%) : %5.3f" % (avg))
df = pd.DataFrame(
    summary,
    columns=["Strikes", "Market value", "Model value", "Relative error (%)"],
    index=['']*len(summary))