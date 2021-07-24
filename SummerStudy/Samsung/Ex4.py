import pandas as pd
from sklearn.datasets import  load_breast_cancer
from sklearn.linear_model import LogisticRegression

X, y = load_breast_cancer(return_X_y=True)

print(y[:30])

print(X[:2])

logistic = LogisticRegression(max_iter=10000)
logistic.fit(X, y)
print('logistic coef:\n', logistic.coef_) 
print('\nlogistic intercept:\n', logistic.intercept_) 

print(logistic.predict(X))

print(logistic.predict_proba(X))

print(logistic.predict_log_proba(X))

print(logistic.score(X, y))