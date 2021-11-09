import QuantLib as ql

valuationDate = ql.Date(29, 10, 2021)
ql.Settings.instance().evaluationDate = valuationDate

calendar = ql.UnitedStates()
dayCount = ql.ActualActual()

# Simple Quote Objects
underlying_qt = ql.SimpleQuote(1.1561)
dividend_qt = ql.SimpleQuote(0.0)
riskfreerate_qt = ql.SimpleQuote(0.05)
volatility_qt = ql.SimpleQuote(0.0101)
# Quote Handle Objects
u_qhd = ql.QuoteHandle(underlying_qt)
q_qhd = ql.QuoteHandle(dividend_qt)
r_qhd = ql.QuoteHandle(riskfreerate_qt)
v_qhd = ql.QuoteHandle(volatility_qt)
# Term-Structure Objects
r_ts = ql.FlatForward(valuationDate, r_qhd, dayCount)
d_ts = ql.FlatForward(valuationDate, q_qhd, dayCount)
v_ts = ql.BlackConstantVol(valuationDate, calendar, v_qhd, dayCount)
# Term-Structure Handle Objects
r_thd = ql.YieldTermStructureHandle(r_ts)
d_thd = ql.YieldTermStructureHandle(d_ts)
v_thd = ql.BlackVolTermStructureHandle(v_ts)
# Process & Engine
process = ql.BlackScholesMertonProcess(u_qhd, d_thd, r_thd, v_thd)
engine = ql.AnalyticEuropeanEngine(process)
# Option Objects
option_type = ql.Option.Put
strikePrice = 1.1650
expiryDate = ql.Date(3, 12, 2021)
exercise = ql.EuropeanExercise(expiryDate)
payoff = ql.PlainVanillaPayoff(option_type, strikePrice)
option = ql.VanillaOption(payoff, exercise)
# Pricing
option.setPricingEngine(engine)
print('Option Premium = ', option.NPV())
print('Option Delta = ', option.delta())
print('Option Gamma = ', option.gamma())
print('Option Theta = ', option.thetaPerDay())
print('Option Vega = ', option.vega() / 100)
print('Option Rho = ', option.rho() / 100)
print('\n')
