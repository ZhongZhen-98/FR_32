import QuantLib as ql

valuationDate = ql.Date(12, 11, 2021) # 평가일
expiryDate = ql.Date(3, 12, 2021) # 만기일
strikePrice = 1.1650 # 행사가
underlying_qt = ql.SimpleQuote(1.14500) # 기초자산 가격
volatility_qt = ql.SimpleQuote(0.0462) # 변동성

riskfreerate_qt = ql.SimpleQuote(0.0005) # 미국 무위험 이자율(3개월 T-bill)
foreignrate_qt = ql.SimpleQuote(-0.00562) # 유로 무위험 이자율(EuLibor)

mkt_price = 0.0214 # 시장가
option_type = ql.Option.Put # 옵션 타입(콜, 풋)

ql.Settings.instance().evaluationDate = valuationDate
calendar = ql.UnitedStates()
dayCount = ql.ActualActual()

u_qhd = ql.QuoteHandle(underlying_qt)
r_thd = ql.YieldTermStructureHandle(ql.FlatForward(valuationDate, ql.QuoteHandle(riskfreerate_qt), dayCount))
d_thd = ql.YieldTermStructureHandle(ql.FlatForward(valuationDate, ql.QuoteHandle(foreignrate_qt), dayCount))
v_thd = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(valuationDate, calendar, ql.QuoteHandle(volatility_qt), dayCount))

process = ql.BlackScholesMertonProcess(ql.QuoteHandle(underlying_qt), d_thd, r_thd, v_thd)
engine = ql.AnalyticEuropeanEngine(process)
exercise = ql.EuropeanExercise(expiryDate)
payoff = ql.PlainVanillaPayoff(option_type, strikePrice)
option = ql.VanillaOption(payoff, exercise)
option.setPricingEngine(engine)

# Historical volatility
print(option.NPV()) # 역사적변동성 적용한 옵션가
print(option.delta()) # Delta
print(option.gamma()) # Gamma
print(option.theta()) # Theta
print(option.vega() / 100) # Vega
print(option.rho() / 100) # Rho
print('\n')

# implied volatility
implied_volaitility = option.impliedVolatility(mkt_price, process)
volatility_qt.setValue(implied_volaitility)
print(implied_volaitility)

print(option.NPV()) # 내재변동성 적용한 옵션가
print(option.delta()) # Delta
print(option.gamma()) # Gamma
print(option.theta()) # Theta
print(option.vega() / 100) # Vega
print(option.rho() / 100) # Rho
print('\n')