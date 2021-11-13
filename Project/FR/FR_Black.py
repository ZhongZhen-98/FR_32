import QuantLib as ql

valuationDate = ql.Date(12, 11, 2021)
expiryDate = ql.Date(3, 12, 2021)
strikePrice = 1.11100
underlying_qt = ql.SimpleQuote(1.14535)
foreignrate_qt = ql.SimpleQuote(0.072)
riskfreerate_qt = ql.SimpleQuote(0.0583)
volatility_qt = ql.SimpleQuote(0.0)
mkt_price = 0.00025
option_type = ql.Option.Put

ql.Settings.instance().evaluationDate = valuationDate
calendar = ql.UnitedStates()
dayCount = ql.ActualActual()

u_qhd = ql.QuoteHandle(underlying_qt)
q_qhd = ql.QuoteHandle(foreignrate_qt)
r_qhd = ql.QuoteHandle(riskfreerate_qt)
v_qhd = ql.QuoteHandle(volatility_qt)

r_ts = ql.FlatForward(valuationDate, r_qhd, dayCount)
d_ts = ql.FlatForward(valuationDate, q_qhd, dayCount)
v_ts = ql.BlackConstantVol(valuationDate, calendar, v_qhd, dayCount)

r_thd = ql.YieldTermStructureHandle(r_ts)
d_thd = ql.YieldTermStructureHandle(d_ts)
v_thd = ql.BlackVolTermStructureHandle(v_ts)

process = ql.BlackScholesMertonProcess(u_qhd, d_thd, r_thd, v_thd)
engine = ql.AnalyticEuropeanEngine(process)
exercise = ql.EuropeanExercise(expiryDate)
payoff = ql.PlainVanillaPayoff(option_type, strikePrice)
option = ql.VanillaOption(payoff, exercise)
option.setPricingEngine(engine)

# implied volatility
implied_volaitility = option.impliedVolatility(mkt_price, process)
volatility_qt.setValue(implied_volaitility)
print('Option Premium = ', option.NPV())
print('Option Delta = ', option.delta())
print('Option Gamma = ', option.gamma())
print('Option Theta = ', option.thetaPerDay())
print('Option Vega = ', option.vega() / 100)
print('Option Rho = ', option.rho() / 100)
print('\n')
