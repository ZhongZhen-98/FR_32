## http://gouthamanbalaraman.com/blog/volatility-smile-heston-model-calibration-quantlib-python.html

import QuantLib as ql
import math
import numpy as np
from mpl_toolkits import mplot3d
import matplotlib.pyplot as plt
from matplotlib import cm

day_count = ql.Actual365Fixed()
calendar = ql.UnitedStates()

calculation_date = ql.Date(14, 8, 2021)

spot = 659.37
ql.Settings.instance().evaluationDate = calculation_date

dividend_yield = ql.QuoteHandle(ql.SimpleQuote(0.0))
risk_free_rate = 0.01
dividend_rate = 0.0
flat_ts = ql.YieldTermStructureHandle(
    ql.FlatForward(calculation_date, risk_free_rate, day_count))
dividend_ts = ql.YieldTermStructureHandle(
    ql.FlatForward(calculation_date, dividend_rate, day_count))

expiration_dates = [ql.Date(14,9,2021), ql.Date(14,10,2021), ql.Date(14,11,2021), ql.Date(14,12,2021)]
strikes = [440.0, 442.5, 445.0, 447.5, 450.0]
data = [
[0.34, 0.23, 0.16, 0.11, 0.08],
[1.49, 1.18, 0.94, 0.74, 0.59],
[2.98, 2.78, 2.40, 1.92, 1.69],
[6.31, 6.95, 5.43, 5.62, 2.72]]

implied_vols = ql.Matrix(len(strikes), len(expiration_dates))
for i in range(implied_vols.rows()):
    for j in range(implied_vols.columns()):
        implied_vols[i][j] = data[j][i]

black_var_surface = ql.BlackVarianceSurface(
    calculation_date, calendar, 
    expiration_dates, strikes, 
    implied_vols, day_count)


strike = 416.06
expiry = 0.3333 # years
print(black_var_surface.blackVol(expiry, strike))

strikes_grid = np.arange(strikes[0], strikes[-1],10)
expiry = 1.0 # years
implied_vols = [black_var_surface.blackVol(expiry, s) 
                for s in strikes_grid] # can interpolate here
actual_data = data[11] # cherry picked the data for given expiry
fig, ax = plt.subplots()
ax.plot(strikes_grid, implied_vols, label="Black Surface")
ax.plot(strikes, actual_data, "o", label="Actual")
ax.set_xlabel("Strikes", size=12)
ax.set_ylabel("Vols", size=12)
legend = ax.legend(loc="upper right")

plot_years = np.arange(0, 2, 0.1)
plot_strikes = np.arange(535, 750, 1)
fig = plt.figure()
ax = plt.axes(projection='3d')
X, Y = np.meshgrid(plot_strikes, plot_years)
YearsStrikesArray = np.array([(y,x) for xr, yr in zip(X,Y) for x, y in zip(xr,yr)])
BlackData = []
for y,x in YearsStrikesArray:
  BlackData.append(black_var_surface.blackVol(y, x))
Z = np.array(BlackData).reshape(len(X), len(X[0]))

surf = ax.plot_surface(X,Y,Z, rstride=1, cstride=1, cmap=cm.coolwarm, linewidth=0.1)
fig.colorbar(surf, shrink=0.5, aspect=5)

local_vol_surface = ql.LocalVolSurface(
    ql.BlackVolTermStructureHandle(black_var_surface), 
    flat_ts, 
    dividend_ts, 
    spot)

plot_years = np.arange(0, 2, 0.1)
plot_strikes = np.arange(535, 750, 1)
fig = plt.figure()
ax = plt.axes(projection='3d')
LocalData = []
X, Y = np.meshgrid(plot_strikes, plot_years)
for y,x in YearsStrikesArray:
  LocalData.append(local_vol_surface.localVol(y, x))
Z = np.array(LocalData).reshape(len(X), len(X[0]))

surf = ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap=cm.coolwarm, 
                linewidth=0.1)
fig.colorbar(surf, shrink=0.5, aspect=5)

# black_var_surface.setInterpolation("bicubic")
# local_vol_surface = ql.LocalVolSurface(
#     ql.BlackVolTermStructureHandle(black_var_surface), 
#     flat_ts, 
#     dividend_ts, 
#     spot)
# plot_years = np.arange(0, 2, 0.15)
# plot_strikes = np.arange(535, 750, 10)
# fig = plt.figure()
# ax = plt.axes(projection='3d')
# X, Y = np.meshgrid(plot_strikes, plot_years)
# for y,x in YearsStrikesArray:
#   LocalData.append(local_vol_surface.localVol(y, x))
# Z = np.array(LocalData).reshape(len(X), len(X[0]))

# surf = ax.plot_surface(Y,X, Z, rstride=1, cstride=1, cmap=cm.coolwarm, 
#                 linewidth=0.1)
# fig.colorbar(surf, shrink=0.5, aspect=5)

# NOTE The correct pricing of local volatility surface requires an arbitrage free implied volatility surface. If the input implied volatility surface is not arbitrage free, this can lead to negative transition probabilities and/or negative local volatilities and can give rise to mispricing. Refer to Fengler's arbtirage free smoothing [1] which QuantLib currently lacks.

plt.show()
