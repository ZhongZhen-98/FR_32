import pandas as pd
import numpy as np

KOSPI200 = pd.read_csv('SummerStudy\Project\HestonModel\KOSPI_200_option.csv', dtype=object)
KOSPI200 = KOSPI200.drop(['종목명'], axis=1)
Strike = [400.0, 410.0, 420.0, 430.0, 440.0]
Edate = ['202109', '202110', '202111', '202112']
KOSPI200CP = KOSPI200
KOSPI200CP = KOSPI200CP.set_index(KOSPI200['콜 풋']).drop(['콜 풋'], axis=1)
KOSPI200C = KOSPI200CP[:'C']
KOSPI200P = KOSPI200CP['P':]
KOSPI200CD = KOSPI200C.set_index(KOSPI200C['만기일']).drop(['만기일'], axis=1)
KOSPI200PD = KOSPI200P.set_index(KOSPI200P['만기일']).drop(['만기일'], axis=1)
DateCount = len(Edate)
StrikeCount = len(Strike)
Data = np.zeros((DateCount, StrikeCount))
for i in range(DateCount):
  s1 = "KOSPI200C{} = KOSPI200CD['{}':'{}']".format(Edate[i],Edate[i],Edate[i])
  exec(s1)
  s2 = "KOSPI200C{} = KOSPI200C{}.set_index(KOSPI200C{}['strike']).drop(['strike'], axis=1)".format(Edate[i],Edate[i],Edate[i])
  exec(s2)
  for j in range(StrikeCount):
    s3 = "Data[{}, {}] = KOSPI200C{}['{}':'{}']['EUREX 정산가'].values".format(i, j, Edate[i], Strike[j], Strike[j])
    exec(s3)
# # 예시
# expiration_dates = [ql.Date(14,9,2021), ql.Date(14,10,2021), ql.Date(14,11,2021), ql.Date(14,12,2021)]
# strikes = [440.0, 442.5, 445.0, 447.5, 450.0]
# data = [
# [0.34, 0.23, 0.16, 0.11, 0.08],
# [1.49, 1.18, 0.94, 0.74, 0.59],
# [2.98, 2.78, 2.40, 1.92, 1.69],
# [6.31, 6.95, 5.43, 5.62, 2.72]]