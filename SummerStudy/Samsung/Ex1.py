from matplotlib.colors import LinearSegmentedColormap
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.datasets import load_boston
from sklearn.linear_model import LinearRegression

boston_dataset = load_boston()

x = pd.DataFrame(boston_dataset.data, columns=boston_dataset.feature_names)
x_rm = pd.DataFrame(x['RM'][:500])
x_rm_test = pd.DataFrame(x['RM'][500:])
print(x_rm)
print(x_rm_test)

y = pd.DataFrame(boston_dataset.target[:500], columns=[['MEDV']])


print(pd.concat([y, x_rm], axis=1).corr())

lr = LinearRegression()
lr.fit(x_rm, y)
print(lr.coef_)
print(lr.intercept_)
print(lr.score(x_rm, y))

print(lr.predict(x_rm_test))

# lr2 = LinearRegression()
# lr2.fit(x, y)

# print(lr2.coef_)
# print(lr2.intercept_)
# print(lr2.score(x, y))