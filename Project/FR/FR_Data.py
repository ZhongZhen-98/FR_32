import pandas as pd
import numpy as np
import csv

Data = pd.read_csv("Project\FR\OpFuData.csv", header=0, index_col="date")
Data.index = pd.to_datetime(Data.index, format="%Y/%m/%d") # dtype = 'datetime64[ns]'로 나오고 1926-07-01처럼 일도 나옴
Data.index = Data.index.to_period("d") # dtype='period[M]'으로 나오고 1926-07까지 나옴 / to_period를 쓰기 위해서 to_datetime으로 바꾼 뒤 사용
print(Data)
