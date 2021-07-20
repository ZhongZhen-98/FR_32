from pandas.core.frame import DataFrame
import requests
import pandas as pd
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import numpy as np
# import mpl_finance
import mplfinance as mpf

# 종목코드 정보가 있는 링크의 테이블을 데이터프레임으로 가져오기
code_df = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13', header=0)[0]
# 종목코드가 6자리이기 때문에 6자리를 맞춰주기 위해 설정해줌
code_df.종목코드 = code_df.종목코드.map('{:06d}'.format)
# 우리가 필요한 것은 회사명과 종목코드이기 때문에 필요없는 column들은 제외해준다.
code_df = code_df[['회사명', '종목코드']]
# 한글로된 컬럼명을 영어로 바꿔준다.
code_df = code_df.rename(columns={'회사명': 'name', '종목코드': 'code'})

# 종목명 in -> 해당 url out
def get_url(item_name, code_df):
    code = code_df.query("name=='{}'".format(item_name))['code'].to_string(index=False)
    url = 'http://finance.naver.com/item/sise_day.nhn?code=' + code
    # print("요청 URL = {}".format(url))
    return url

item_name='삼성전자' # 원하는 종목명으로 검색 (Naver Finance)
url = get_url(item_name, code_df)

df = pd.DataFrame() # 일별시세 담을 데이터프레임 선언

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'}

for page in range(1, 31): # 페이지 숫자만큼 반복
    pg_url = '{url}&page={page}'.format(url=url, page=page)

    res = requests.get(pg_url, headers=headers)
    soup = BeautifulSoup(res.content, 'lxml')
    table = soup.select("table")[0]
    df = df.append(pd.read_html(str(table), header=0)[0], ignore_index=True)

df = df.dropna() # NaN값 제외처리
df = df.set_index("날짜")
df = df.loc[::-1]

df.index = pd.to_datetime(df.index, format="%Y.%m.%d") 
fig = plt.figure(figsize=(10,10))
ax = fig.add_subplot(1,1,1)
mpf.plot(df[:100],type='candle')
# print(df)

# # plt.plot(df.index, df['종가'])
# # plt.show()

# mpl_finance.candlestick2_ohlc(ax, df['시가'], df['고가'], df['저가'], df['종가'], width=0.5, colorup='r', colordown='b')

# plt.show()
