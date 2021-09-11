import QuantLib as ql
import pandas as pd

# option data
maturity_date = ql.Date(10, 2, 2022) # 만기일 (일, 월, 년)
spot_price = 1.1711 # 현물가격
strike_price = 130 # 행사가
volatility = 0.20 # the historical vols for a year 기초 주식의 변동성
dividend_rate =  0.0163 # 배당수익률
option_type = ql.Option.Call

risk_free_rate = 0.001 # 무위험 이자율
day_count = ql.Actual365Fixed()
calendar = ql.UnitedStates()

calculation_date = ql.Date(11, 8, 2021) # 평가 기준일
ql.Settings.instance().evaluationDate = calculation_date

# construct the European Option
payoff = ql.PlainVanillaPayoff(option_type, strike_price)
exercise = ql.EuropeanExercise(maturity_date)
european_option = ql.VanillaOption(payoff, exercise)



# dummy parameters
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

process = ql.HestonProcess(flat_ts,
                           dividend_yield,
                           spot_handle,
                           v0,
                           kappa,
                           theta,
                           sigma,
                           rho)

model = ql.HestonModel(process)
engine = ql.AnalyticHestonEngine(model)

# engine = ql.AnalyticHestonEngine(ql.HestonModel(heston_process),0.01, 1000)

heston_helpers = []

data = [
    [1.1500, 5.75],
    [1.1600, 5.66],
    [1.1700, 5.60],
    [1.1800, 5.58],
    [1.1900, 5.58],
    [1.2000, 5.61],
    [1.2100, 5.67]
]

tenor = ql.Period('6M')
for strike, vol in data:
    helper = ql.HestonModelHelper(tenor, ql.TARGET(), spot_price,
                                  strike, ql.QuoteHandle(ql.SimpleQuote(vol / 100)), flat_ts, dividend_yield )
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
        data[i][0],
        opt.marketValue(), 
        opt.modelValue(), 
        100.0*(opt.modelValue()/opt.marketValue() - 1.0)))
    avg += abs(err)
avg = avg*100.0/len(heston_helpers)

print("Average Abs Error (%%) : %5.3f" % (avg))
df = pd.DataFrame(
    summary,
    columns=["Strikes", "Market value", "Model value", "Relative error (%)"],
    index=['']*len(summary))