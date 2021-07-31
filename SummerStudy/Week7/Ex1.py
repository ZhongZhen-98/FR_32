### 저장한 csv파일들 backtrader에 추가하고 대상으로 백테스팅하기 PART 2 ###
# => 데이터 클리닝과 기간 설정 / 리밸런싱 함수 이용한 보다 현실적인 백테스팅

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from datetime import datetime as dt
import backtrader as bt

from os import listdir
from os.path import isfile, join

import heapq

import pandas as pd
import yfinance as yf

## DATA CLEANING ##

# 종목별 엑셀 파일들 가져오기
dir = './SummerStudy/Week6/us_stocks_db/'
file_names = [f for f in listdir(dir) if isfile(join(dir, f))]

# NaN값 포함된 행들은(날짜들은) 모두 삭제
datalist = []
for i in range(len(file_names)):
    ticker = file_names[i][0:-4]
    # print(ticker)
    ## 이 부분이 시가총액 작은 애들 빼주는 부분 -> 시간이 너무 오래걸려서 일단 생략 ##
    # try:
    #     market_cap = yf.Ticker(ticker).info['marketCap']
    #     if market_cap >= 100000000:
    #         datalist.append((pd.read_csv(dir + '/' + file_names[i]).dropna(), ticker))
    # except Exception as e:
    #     print(e)
    datalist.append((pd.read_csv(dir + '/' + file_names[i]).dropna(), ticker))

# 우리가 정한 백테스팅 기간(18, 19년도 2년치)에 누락된 날짜 및 데이터 있는지 확인
# AAPL(애플) 데이터를 기준으로... -> 누락 없으면 새로 선정된 애들 db(selected_db 디렉터리)에 저장
standard_data = pd.read_csv(dir + '/AAPL.csv').dropna()
standard_data = standard_data.loc['2017-10-02':]
for i in range(len(datalist)):
    try:
        adjusted_data = datalist[i][0].loc['2017-10-02':]
        if adjusted_data.index.equals(standard_data.index):
            adjusted_data.index = adjusted_data['Date']
            adjusted_data = adjusted_data.drop(['Date'], axis=1)
            # print(adjusted_data)
            adjusted_data.to_csv('./SummerStudy/Week7/selected_db/' + datalist[i][1] + '.csv')
    except Exception as e:
        print(e)

## REBALANCING 함수 기존 백테스팅 코드에 적용 ##

# 6주차 코드 (multiple data feeds) import -> import '파일명'
import backtrader_multiple_stocks_augmented_data as part1

# 기존 전략 클래스 상속 -> 내부에서 바꿀 부분 바꾸어주기 위해
class RebalAdjusted(part1.MeanRev_PB_SalesG):

    # 리밸런싱 함수 이용하여 매매 로직 더 깔끔하게 재구성
    # backtrader의 order_target_percent() 함수 이용
    def next(self):
        rebalance = False

        cur_month = int(self.datas[0].datetime.date(0).strftime("%m"))

        # 리밸런싱 날짜인지 확인
        if cur_month in self.rebal_months:
            if int(self.datas[0].datetime.date(-1).strftime("%m")) == cur_month - 1:
                rebalance = True

        # 리밸런싱 날짜인 경우 진행
        if rebalance:
            self.log('rebal date')

            # 조건 맞는 상위 5개 종목 선별
            # 조건 부합 종목 4개 이하면 전부 선택 & 비율 그에 맞게 (1/n)
            selected = {}  # 종목 : sales growth qoq 값
            for d in self.datas:
                if d.close[0] <= 0.8 * self.inds[d]['60sma'][0] and d.pb[0] < 1:
                    selected[d] = d.sales_growth_qoq
            # heapq.nlargest로 가장 큰 value 5개의 해당 key값들 list로 반환
            # 만약 key값이 4개 이하면 전부 반환됨
            buylist = heapq.nlargest(5, selected, key=selected.get)  # 살 종목 리스트

            if len(buylist):  # 선택된 종목이 없는 경우 pass

                for d in self.datas: # 종목 마다 체크
                    dn = d._name # 종목명 (티커)
                    pos = self.getposition(d).size # 현재 보유량 (없으면 0)

                    # buylist에 이미 포지션 있는 종목 있는지 확인
                    # => 있으면 비중 조절 / 없으면 전부 매도
                    if pos:
                        if d in buylist:
                            self.order_target_percent(d, target=1/len(buylist))
                        else:
                            self.log('%s SELL CREATE, %.2f' % (dn, d.close[0]))
                            self.sell(data=d, size=pos)

                    # buylist의 종목 중 포지션 없었던 것 새로 진입
                    else:
                        if d in buylist:
                            self.order_target_percent(d, target=1/len(buylist))

        # 일별 포트폴리오 총가치 log
        self.log('PORTFOLIO VALUE: %.2f' % self.broker.getvalue())

# import한 module이 run하지 않게끔 컨트롤 (해당 module의 실행코드에도 정의)
if __name__ == "__main__":
    # 백테스팅 실행
    startcash = 100000

    cerebro = bt.Cerebro()

    cerebro.addstrategy(RebalAdjusted)

    # 파일명 불러와서 (파일주소, 종목명) 형태로 datalist에 저장
    dir = './SummerStudy/Week7/selected_db//'
    file_names_2 = [f for f in listdir(dir) if isfile(join(dir, f))]

    final_datalist = []
    for i in range(len(file_names_2)): # 종목명 명시 -> backtest log볼때 거래기록 보기 편리
        final_datalist.append((dir + '/' + file_names_2[i], file_names_2[i][0:-4]))

    # backtrader의 데이터 feed에 datalist의 항목들 모두 추가
    for i in range(len(final_datalist)):
        # 설정 기간이 존재 범위 벗어나면 자동으로 최대범위로 고정시켜줌
        # 60sma계산 위해 60일 일찍 시작
        data = part1.MyCSVData(dataname=final_datalist[i][0], fromdate=dt(2017, 10, 1), todate=dt(2019, 12, 31))
        cerebro.adddata(data, name=final_datalist[i][1])

    cerebro.broker.setcash(startcash)

    cerebro.broker.setcommission(commission=0.0015) # 0.15%

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    cerebro.run()

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())