code = "FB"
start = 1593761968
end = 1625297968
a = ("https://query1.finance.yahoo.com/v7/finance/download/{}?period1={}&period2={}&interval=1d&events=history&includeAdjustedClose=true").format(code, start, end)
print(a)