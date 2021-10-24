## 여기에서 그릭스 구하는거 사용!!
import QuantLib as ql

# NOTE 입력 필요
valuationDate = ql.Date(25, 10, 2021)
ql.Settings.instance().evaluationDate = valuationDate

# NOTE 여기 바꿔주기
calendar = ql.SouthKorea()
dayCount = ql.ActualActual()

# Simple Quote Objects
# NOTE 입력 필요
underlying_qt = ql.SimpleQuote(1.16565)
dividend_qt = ql.SimpleQuote(0.0)
riskfreerate_qt = ql.SimpleQuote(0.01)
volatility_qt = ql.SimpleQuote(0.0019)

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
# NOTE 입력 필요
option_type = ql.Option.Call
strikePrice = 1.0100
expiryDate = ql.Date(3, 12, 2021)
exercise = ql.EuropeanExercise(expiryDate)
payoff = ql.PlainVanillaPayoff(option_type, strikePrice)
option = ql.VanillaOption(payoff, exercise)

# Pricing
option.setPricingEngine(engine)

# Price & Greeks Results
print('Option Premium = ', round(option.NPV(), 2))
print('Option Delta = ', round(option.delta(), 4))
print('Option Gamma = ', round(option.gamma(), 4))
print('Option Theta = ', round(option.thetaPerDay(), 4))
print('Option Vega = ', round(option.vega() / 100, 4))
print('Option Rho = ', round(option.rho() / 100, 4))
print('\n')

print('Option Premium = ', option.NPV())
print('Option Delta = ', option.delta())
print('Option Gamma = ', option.gamma())
print('Option Theta = ', option.thetaPerDay())
print('Option Vega = ', option.vega() / 100)
print('Option Rho = ', option.rho() / 100)
print('\n')

# # Automatic Re-Pricing
# underlying_qt.setValue(275)
# print('Option Premium = ', round(option.NPV(), 2))
# print('Option Delta = ', round(option.delta(), 4))
# print('Option Gamma = ', round(option.gamma(), 4))
# print('Option Theta = ', round(option.thetaPerDay(), 4))
# print('Option Vega = ', round(option.vega() / 100, 4))
# print('Option Rho = ', round(option.rho() / 100, 4))
# print('\n')

# # Implied Volatility
# underlying_qt.setValue(270.48)
# mkt_price = 8.21
# implied_volatility = option.impliedVolatility(mkt_price, process)
# volatility_qt.setValue(implied_volatility)
# print('Option Premium = ', round(option.NPV(), 2))
# print('Option Delta = ', round(option.delta(), 4))
# print('Option Gamma = ', round(option.gamma(), 4))
# print('Option Theta = ', round(option.thetaPerDay(), 4))
# print('Option Vega = ', round(option.vega() / 100, 4))
# print('Option Rho = ', round(option.rho() / 100, 4))
# print('\n')
