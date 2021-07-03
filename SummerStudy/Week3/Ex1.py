import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import pandas_datareader as web
import datetime as dt

# 여러 종목 DataFrame 합치는 작업

index1 = "AMZN" # 아마존
index2 = "AAPL" # 애플
index3 = "005930.KS" # 삼성전자(코스피)
index4 = "068760.KQ" # 셀트리온제약(코스닥)

stockList = [] # 모든 종목 대해서는 미리 받아놓은 파일(csv등)을 이용하는 것이 용이
stockList.append(index1)
stockList.append(index2)
stockList.append(index3)
stockList.append(index4)

start = dt.datetime(2015, 6, 21)
end = dt.datetime.now()

data = web.DataReader(index1, 'yahoo', start, end)
print(data)

closeData = data['Close']
print(closeData)

i = 0
for index in stockList:
    if i != 0:
        temp = web.DataReader(index, 'yahoo', start, end)['Close']
        closeData = pd.concat([closeData, temp], axis=1)
    i += 1
closeData.columns = stockList

print(closeData) # '종가' 데이터만 갖고 있는 column들로 이루어진 DataFrame

# 아예 dataframe들 list?
df_list = []
for index in stockList:
    temp = web.DataReader(index, 'yahoo', start, end)
    df_list.append(temp)
print(df_list)

# 클래스 및 백테스팅과 함께 활용???
## -> 데이터(종목수?) 적으면 코드 실행(load time)시에도 가능 / 많다면 추가적인 DB 사용이 필요

# 데이터 클리닝 (합쳐진 상태에서 NaN 처리)

# df.dropna()도 이용가능
closeData.fillna(method='ffill')
print(closeData)
print(closeData.shape) # dimension을 의미 -> (1555, 4) = 1555 x 4 행렬

for i in range(1, closeData.shape[0]):
    for j in range(4): # 4 대신 closeData.shape[1] 가능!
        if np.isnan(closeData.values[i][j]):
            closeData.values[i][j] = closeData.values[i-1][j]

print(closeData)