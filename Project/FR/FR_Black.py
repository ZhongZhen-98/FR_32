import QuantLib as ql

valuationDate = ql.Date(19, 11, 2021) # 평가일
expiryDate = ql.Date(3, 12, 2021) # 만기일
strikePrice = 1.1275 # 행사가
underlying_qt = ql.SimpleQuote(1.12870) # 기초자산 가격
volatility_qt = ql.SimpleQuote(0.0506) # 변동성

riskfreerate_qt = ql.SimpleQuote(0.0005) # 미국 무위험 이자율(3개월 T-bill)
foreignrate_qt = ql.SimpleQuote(-0.00559) # 유로 무위험 이자율(EuLibor)

mkt_price = 0.00680 # 시장가
option_type = ql.Option.Call # 옵션 타입(콜, 풋)

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

print("Market Price ", 0.00680)
# Historical volatility
print("Option price(Historical Volatility) ", option.NPV()) # 역사적변동성 적용한 옵션가
print("Option delta(Historical Volatility) ", option.delta()) # Delta
print("Option gamma(Historical Volatility) ", option.gamma()) # Gamma
print("Option Theta(Historical Volatility) ", option.theta()) # Theta
print("Option Vega(Historical Volatility) ", option.vega() / 100) # Vega
print("Option Rho(Historical Volatility) ", option.rho() / 100) # Rho
print('\n')


# implied volatility
implied_volaitility = option.impliedVolatility(mkt_price, process)
volatility_qt.setValue(implied_volaitility)
print("Implied Volaitility ", implied_volaitility)
print("Option price(Implied Volaitility) ", option.NPV()) # 내재변동성 적용한 옵션가
print("Option delta(Implied Volaitility) ", option.delta()) # Delta
print("Option gamma(Implied Volaitility) ", option.gamma()) # Gamma
print("Option theta(Implied Volaitility) ", option.theta()) # Theta
print("Option vega(Implied Volaitility) ", option.vega() / 100) # Vega
print("Option rho(Implied Volaitility) ", option.rho() / 100) # Rho
print('\n')