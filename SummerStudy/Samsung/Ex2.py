import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt

realgdp = sm.datasets.macrodata.load_pandas().data['realgdp']
realgdp.index = pd.period_range('1959Q1', '2009Q3', freq='Q')

print(realgdp)

cycle, trend = sm.tsa.filters.hpfilter(realgdp, 1600)

print(trend)

print(cycle)

realgdp.loc['2003-03-31':, ].plot()
trend.loc['2003-03-31':, ].plot()
plt.show()
