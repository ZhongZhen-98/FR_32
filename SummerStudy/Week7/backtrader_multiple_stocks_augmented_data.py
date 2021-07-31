### 저장한 csv파일들 backtrader에 추가하고 대상으로 백테스팅하기 ###

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from datetime import datetime as dt
import backtrader as bt

from os import listdir
from os.path import isfile, join

import heapq # dictionary sorting 용 -> 사이즈 커져도 효율적

## 5 & 6 & 7
# 2017년 이전 데이터 & 2020년 데이터 존재하는 종목들 모두 csv파일들 저장시킨 상태 가정한 코드

# 커스텀 CSV 데이터 클래스 제작
# (backtrader의 GenericCSVData 클래스 기능들 상속, 변경)
class MyCSVData(bt.feeds.GenericCSVData):
    params = (
        # 디폴트 2개
        ('nullvalue', float('NaN')),
        ('dtformat', '%Y-%m-%d'),

        # 아래 항목 모두 csv파일 상 몇번째 칼럼인지 명시
        ('datetime', 0),
        ('time', -1),
        ('open', 1),
        ('high', 2),
        ('low', 3),
        ('close', 4),
        ('volume', 5),
        ('openinterest', -1),

        ('net_profit', 6),
        ('sales_growth_qoq', 7),
        ('pb', 8),
    )

    # backtrader가 인식할 수 있는 data feed line에 추가하기
    lines = ('net_profit', 'sales_growth_qoq', 'pb')

# 전략 구성 (예시)
class MeanRev_PB_SalesG(bt.Strategy):

    rebal_months = [2, 5, 8, 11]

    # 백테스팅이 진행될때 타임스탬프마다 메시지 출력
    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)  # 현재 시간 표시
        print('%s, %s' % (dt.isoformat(), txt))  # 현재시간 & input 메시지 출력

    # 백테스팅시 사용될 대상 데이터 & 거래액션 관련 변수들 정의
    def __init__(self):

        # 딕셔너리로 관리
        self.inds = dict() # 전체 딕셔너리

        for d in self.datas: # 종목마다
            self.inds[d] = dict() # 종목별 추가지표 관리 딕셔너리
            self.inds[d]['60sma'] = bt.ind.SMA(period=60) # 60 이평선
            # self.inds[d]['close'] = d.close # 종가
            # self.inds[d]['pb'] = d.pb # pb 값
            # self.inds[d]['sg_qoq'] = d.sales_growth_qoq # sales growth qoq 값

    # buy, sell 함수 호출 후 실제 매매과정(주문) 처리 후 기록 및 log
    def notify_order(self, order):

        # 주문 접수중 -> 아무 액션 안취해도 됨
        if order.status in [order.Submitted, order.Accepted]:
            return

        # 주문 체결시 매매기록 logging
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    '%s BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.data._name,
                     order.executed.price,
                     order.executed.value,
                     order.executed.comm))

            else:
                self.log('%s SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.data._name,
                          order.executed.price,
                          order.executed.value,
                          order.executed.comm))

        # 주문에 문제 생긴 경우 (체결x)
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

    # 포지션 마감시 발생 수익 log
    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('%s OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.data._name, trade.pnl, trade.pnlcomm))

    # timestep마다 모니터링 -> buy, sell 함수 호출
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
            selected = {} # 종목 : sales growth qoq 값
            for d in self.datas:
                if d.close[0] <= 0.8 * self.inds[d]['60sma'][0] and d.pb[0] < 1:
                        selected[d] = d.sales_growth_qoq
            # heapq.nlargest로 가장 큰 value 5개의 해당 key값들 list로 반환
            # 만약 key값이 4개 이하면 전부 반환됨
            buylist = heapq.nlargest(5, selected, key=selected.get) # 살 종목 리스트

            if len(buylist): # 선택된 종목이 없는 경우 pass

                for d in self.datas: # 종목 마다 체크
                    dn = d._name # 종목명 (티커)
                    pos = self.getposition(d).size # 현재 보유량 (없으면 0)

                    # buylist에 이미 포지션 있는 종목 있는지 확인
                    # => 있으면 비중 조절 / 없으면 전부 매도
                    if pos:
                        if d in buylist:
                           rebal_val = self.broker.getvalue() // len(buylist) - pos * d.close[0]
                           rebal_amt = abs(rebal_val) // d.close[0]
                           if rebal_val > 0:
                               self.log('%s BUY CREATE, %.2f' % (dn, d.close[0]))
                               self.buy(data=d, size=rebal_amt)
                           elif rebal_val < 0:
                               self.log('%s SELL CREATE, %.2f' % (dn, d.close[0]))
                               self.sell(data=d, size=rebal_amt)
                        else:
                            self.log('%s SELL CREATE, %.2f' % (dn, d.close[0]))
                            self.sell(data=d, size=pos)

                    # buylist의 종목 중 포지션 없었던 것 새로 진입
                    else:
                        if d in buylist:
                            rebal_amt = (self.broker.getvalue() // len(buylist)) // d.close[0]
                            self.log('%s BUY CREATE, %.2f' % (dn, d.close[0]))
                            self.buy(data=d, size=rebal_amt)

        # 일별 포트폴리오 총가치 log
        self.log('PORTFOLIO VALUE: %.2f' % self.broker.getvalue())

startcash = 100000

cerebro = bt.Cerebro()

cerebro.addstrategy(MeanRev_PB_SalesG)

# 파일명 불러와서 (파일주소, 종목명) 형태로 datalist 에 저장
dir = './SummerStudy/Week6/us_stocks_db'
file_names = [f for f in listdir(dir) if isfile(join(dir, f))]

datalist = []
for i in range(51): # 종목명 명시 -> backtest log볼때 거래기록 보기 편리
    datalist.append((dir + '/' + file_names[i], file_names[i][0:-4]))

## 중요: cerebro 엔진은 자동으로 모든 csv파일의 데이터가 존재하는 날짜부터 돌아감 !!
# ADTM 중간데이터 누락 (52번째) - 날짜 & 거래량 데이터만 있고 나머지 없는 구간 존재
# ADV 중간데이터 누락 (55번째) - 날짜 데이터 자체가 함께 누락된 구간 존재
# -> 중간데이터 확인까지 해주는 코드 추가 필요...

# backtrader의 데이터 feed에 datalist의 항목들 모두 추가
for i in range(len(datalist)):
    # 설정 기간이 존재 범위 벗어나면 자동으로 최대범위로 고정시켜줌
    data = MyCSVData(dataname=datalist[i][0], # 60sma계산 위해 60일 일찍 시작
                     fromdate=dt(2017, 10, 1), todate=dt(2019, 12, 31))
    cerebro.adddata(data, name=datalist[i][1])

cerebro.broker.setcash(startcash)

# cerebro.broker.setcommission(commission=0.0015) # 0.15%
# => 수수료 고려 한다면 next부분에서 주문 수량 넣는 부분 바꾸어주어야함
# => https://backtest-rookies.com/2020/05/09/backtrader-portfolio-rebalancing-with-alpha-vantage/
# -> 이 예시의 self.order_target_percent 함수로 간단하게 리밸런싱 하는 방법 참조

print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

cerebro.run()

print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())