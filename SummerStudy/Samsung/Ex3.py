import pandas as pd
from sklearn.datasets import load_boston
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import Ridge, Lasso, ElasticNet

x, y = load_boston(return_X_y=True)
lr = LinearRegression()
lr.fit(x,y)
print('regression coef: \n', lr.coef_) 
print('\nregression intercept:\n', lr.intercept_)

elastic_net = ElasticNet()
elastic_net.fit(x,y)
print('Elastic_Net coef:\n ', elastic_net.coef_) 
print('\nElastic_Net intercept:\n', elastic_net.intercept_)