### 저장한 csv파일들 backtrader에 추가하고 대상으로 백테스팅하기 PART 3 ###
# => Backtrader에서 Multiple TimeFrames(월, 주, 일, 분) 이용하기 - 한종목 대상 (AAPL)

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from datetime import datetime as dt
import backtrader as bt

## 간단한 전략 실험용 - momentum strategy
class MultiTimeFrame(bt.Strategy):

    # 바꿀 수 있는 파라미터들
    params = ( # 여기서는 모멘텀 매수 결정 비율
        ('k', 0.5),
    )

    # 일별 데이터 모으기
    day_bars = dict()

    # 다음 날로 넘어갔는지 확인
    new_day = False

    # 백테스팅이 진행될때 타임스탬프마다 메시지 출력
    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)  # 현재 시간 표시
        print('%s, %s' % (dt.isoformat(), txt))  # 현재시간 & input 메시지 출력

    # 백테스팅시 사용될 대상 데이터 & 거래액션 관련 변수들 정의
    def __init__(self):
        self.min_data = self.datas[0]
        self.day_data = self.datas[1]  # 분별로 진행하면서 얘는 계속 업뎃 되는식
        # -> 따로 모아줘서 일봉 데이터 만들어놓아야 전날 데이터 접근 용이

    # buy, sell 함수 호출 후 실제 매매과정(주문) 처리 후 기록 및 log
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

    # 포지션 마감시 발생 수익 log
    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    # timestep마다 모니터링 -> buy, sell 함수 호출
    def next(self):

        self.log(str(len(self)))

        # 다음날로 넘어갈시
        if self.min_data.datetime.date(0) != self.min_data.datetime.date(-1):
            self.new_day = True
            # 일봉 데이터 업뎃
            self.day_bars = {'high' : self.day_data.high[-1], 'low' : self.day_data.low[-1]}

        # 새로운 매매일로 넘어간 경우 -> 매수 조건 확인
        elif self.new_day:
            # 모멘텀 매수 조건 확인
            if self.min_data.close[0] > self.day_data.open[0] + self.params.k * (self.day_bars['high'] - self.day_bars['low']):
                self.log('BUY CREATE, %.2f' % self.min_data.close[0])
                self.buy(size=400, price=self.min_data.close[0], exectype=bt.Order.Stop) # 순간 만족한 분봉 종가에 매수
            self.new_day = False

        # 매도 조건 확인
        if self.position and len(self) % 13 == 12: 
            self.log('SELL CREATE, %.2f' % self.min_data.close[0]) # 주문 생성은 일별로 마지막에서 2번째 분봉에 생성
            self.sell(size=400, exectype=bt.Order.Close) # 주문 체결은 일별로 마지막 분봉의 종가에서 체결

## 백테스팅 실행
startcash = 100000

cerebro = bt.Cerebro()

cerebro.addstrategy(MultiTimeFrame)

dir = '본인 디렉터리' # 분데이터 파일이어야 함

# Smaller Timeframe 데이터 먼저 추가 (분별)
data = bt.feeds.YahooFinanceCSVData(dataname=dir + '/본인 파일명', fromdate=dt(2021, 5, 1), todate=dt(2021, 6, 30))
cerebro.adddata(data)

# Larger Timeframe 데이터 추가 (일별)
cerebro.resampledata(data, timeframe=bt.TimeFrame.Days)

cerebro.broker.setcash(startcash)

cerebro.broker.setcommission(commission=0.0015) # 0.15%

print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

cerebro.run()

print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())