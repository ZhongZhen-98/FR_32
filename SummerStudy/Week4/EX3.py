import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import yfinance as yf
import mpl_finance
import matplotlib.dates as mpl_dates

# pd.set_option("display.max_rows", None, "display.max_columns", None)

def getKOScode():
    # 종목코드 정보가 있는 링크의 테이블을 데이터프레임으로 가져오기
    kospi_codes = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&marketType=stockMkt', header=0)[0]
    kosdaq_codes = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&marketType=kosdaqMkt', header=0)[0]
    # 종목코드가 6자리이기 때문에 6자리를 맞춰주기 위해 설정해줌
    kospi_codes.종목코드 = kospi_codes.종목코드.map('{:06d}'.format)
    kosdaq_codes.종목코드 = kosdaq_codes.종목코드.map('{:06d}'.format)
    # 우리가 필요한 것은 회사명과 종목코드이기 때문에 필요없는 column들은 제외해준다.
    kospi_codes = kospi_codes[['회사명', '종목코드']]
    kosdaq_codes = kosdaq_codes[['회사명', '종목코드']]

    kospi_codes["시장구분"] = 'KS'
    kosdaq_codes["시장구분"] = 'KQ'

    code_df = pd.concat([kospi_codes, kosdaq_codes], axis=0, keys=['회사명', '종목코드', '시장구분'])

    # print(code_df)
    return code_df

def getData(code, mkt):
    print(code, mkt)
    if mkt == "KS":
        ticker = code + ".KS"
    if mkt == "KQ":
        ticker = code + ".KQ"

    data = yf.Ticker(ticker)
    data = data.history(start=start, end=end)

    data = data[data['Volume'] != 0]

    ma5 = data['Close'].rolling(window=5).mean()
    ma20 = data['Close'].rolling(window=20).mean()

    data.insert(len(data.columns), "ma5", ma5)
    data.insert(len(data.columns), "ma20", ma20)

    data = data[19:]

    # print(data)

    df_dict[code] = data

def crossBacktest(weights):

    # 종목별 가중치(할당금액) 초기화
    for k in range(len(weights)):
        alloc[k] = cash[0] * weights[k]

    # timestep (일) 마다
    for i in range(1, l):

        # 기본가정 hold에서 시작 (timestep별 총 현금 & 총 수익)
        cash[i] = cash[i - 1]
        profit[i] = profit[i - 1]

        wCount = 0
        # 종목별
        for data in df_dict.values():
            data5 = data["ma5"]
            data20 = data["ma20"]

            port = portfolio['port'][str(code_df['종목코드'][wCount])]

            # 기본가정 hold에서 시작 (종목별 보유단가 & 보유량)
            port[i] = port[i - 1]

            if data5[i-1] <= data20[i-1] and data5[i] > data20[i] and alloc[wCount] > 0: #골드크로스(buy)
                num = alloc[wCount] // data['Close'][i]
                cash[i] = cash[i] - num * data['Close'][i]
                port[i][0] = data['Close'][i]
                port[i][1] = num

                temp = []
                temp.append(i)
                temp.append(data['Close'][i])
                gold[str(code_df['종목코드'][wCount])].append(temp)

                alloc[wCount] -= num * data['Close'][i]

            elif data5[i-1] >= data20[i-1] and data5[i] < data20[i] and port[i-1][1] != 0: #데드크로스(sell)
                cash[i] = cash[i] + port[i-1][1] * data['Close'][i]
                alloc[wCount] += port[i-1][1] * data['Close'][i]
                profit[i] = profit[i] + port[i - 1][1] * (data['Close'][i] - port[i - 1][0])

                temp = []
                temp.append(i)
                temp.append(data['Close'][i])
                dead[str(code_df['종목코드'][wCount])].append(temp)

                port[i][0] = 0
                port[i][1] = 0

            portfolio['port'][str(code_df['종목코드'][wCount])] = port

            wCount += 1

    portfolio['cash'] = cash
    portfolio['profit'] = profit
    portfolio['allocation'] = alloc

start = dt.datetime(2020, 7, 1)
end = dt.datetime(2021, 7, 1)

code_df = getKOScode()
df_dict = {}

portfolio = {'cash': [10000000],  # 1000만원 시작 가정
             'port': {},  # 각 종목별 매수단가&보유량 기록
             'profit': [0],
             'allocation': []}  # 시간따라 종목별 할당된 매수가능 금액 표시

stockNum = 5
for i in range(stockNum):
    getData(str(code_df['종목코드'][i]), str(code_df['시장구분'][i]))
    # print(len(df_dict[str(code_df['종목코드'][i])]))
    # timestep당 종목별 매수단가 & 보유량 초기화
    portfolio['port'][str(code_df['종목코드'][i])] = [[0, 0]] * len(df_dict[str(code_df['종목코드'][0])])

l = len(df_dict[str(code_df['종목코드'][0])])
# print(l)

# timestep당 현금 / 수익 / 종목별 할당 매수가능금액 초기화
portfolio['cash'] = [10000000]*l
portfolio['profit'] = [0]*l
portfolio['allocation'] = [0]*stockNum

cash = portfolio['cash']
profit = portfolio['profit']
alloc = portfolio['allocation']

# gold, dead cross 시점 & 가격 기록용 딕셔너리
gold = {}
dead = {}
for i in range(stockNum):
    gold[str(code_df['종목코드'][i])] = []
    dead[str(code_df['종목코드'][i])] = []

# 백테스트 & portfolio딕셔너리 update용 함수

weights = [0.2, 0.2, 0.2, 0.2, 0.2] # 종목별 분산 가중치

crossBacktest(weights)

# 백테스트 결과 timestep에 따른 종목별 buy&sell 지점 표시
dataPlot = []
for data in df_dict.values():

    data['Date'] = data.index
    data['Date'] = data['Date'].apply(mpl_dates.date2num)
    dataPlot.append(data.loc[:, ['Date', 'Open', 'High', 'Low', 'Close']])

print(gold)
print(dead)

for i in range(stockNum):
    fig, ax = plt.subplots()

    mpl_finance.candlestick_ohlc(ax, dataPlot[i].values, colorup='red', colordown='blue')
    ax.plot(df_dict[str(code_df['종목코드'][i])]['ma5'], color='green', label='ma5')
    ax.plot(df_dict[str(code_df['종목코드'][i])]['ma20'], color='yellow', label='ma20')

    for j, (day, price) in enumerate(gold[str(code_df['종목코드'][i])]):
        ax.plot(dataPlot[i]['Date'][day], price, color='red', marker='^', markersize=10)
    for j, (day, price) in enumerate(dead[str(code_df['종목코드'][i])]):
        ax.plot(dataPlot[i]['Date'][day], price, color='blue', marker='v', markersize=10)

    date_format = mpl_dates.DateFormatter("%d %b %Y")
    ax.xaxis.set_major_formatter(date_format)
    fig.autofmt_xdate

    ax.set_xlabel('Date')
    ax.set_ylabel('Price')
    ax.set_title(str(code_df['종목코드'][i]) + " Trade History")
    plt.legend(loc='best')

    plt.plot()


# 백테스트 결과 timestep에 따른 현금 / 수익 변화 시각화
# print(portfolio['cash'])
# print(portfolio['allocation'])
# print(portfolio['profit'])

fig2 = plt.figure()
ax1 = fig2.add_subplot(211)
ax2 = fig2.add_subplot(212)

date = df_dict[str(code_df['종목코드'][0])] # 첫번째 종목 날짜 데이터 기준... (날짜 서로 안맞는 예외 경우(*) 일단 제외)
date['Date'] = date.index
date['Date'] = date['Date'].apply(mpl_dates.date2num)

ax1.plot(date['Date'], portfolio['cash'])
ax2.plot(date['Date'], portfolio['profit'])

date_format = mpl_dates.DateFormatter('%d %b %Y')

ax1.xaxis.set_major_formatter(date_format)
ax2.xaxis.set_major_formatter(date_format)
fig2.autofmt_xdate # ()표시 뒤에 없어야 위,아래 그래프 모두 다 x축에 날짜가 제대로 표시됨

ax1.set_xlabel('Date')
ax1.set_ylabel('Cash')

ax2.set_xlabel('Date')
ax2.set_ylabel('Profit')

ax1.set_title("CASH")
ax2.set_title("PROFIT")

plt.show()