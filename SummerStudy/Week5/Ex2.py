# 먼저 기본적인 모듈들부터 import 합니다
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from datetime import datetime
import backtrader as bt

# 전략 클래스
class TestStrategy(bt.Strategy): # backtrader의 Strategy 클래스 상속 & 이용
    
	# 사용자가 초기에 설정 가능한 변수들 정의 (ex: 이평선 몇일짜리 쓸지 등)
	  params = (
      ('exitbars', 5),
    )

	# 백테스팅이 진행될때 타임스탬프마다 메시지 출력
def log(self, txt, dt=None, doprint=False):
    if doprint:
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))
# 백테스팅시 사용될 대상 데이터 & 거래액션 관련 변수들 정의
def __init__(self):
    # 종가데이터 모아놓은 변수 (리스트처럼 접근 가능)
    self.dataclose = self.datas[0].close
    # 주문 상태 & 매수가,수수료 (백테스팅 진행하며 업뎃할 변수들)
    self.order = None
    self.buyprice = None
    self.buycomm = None
# buy, sell 함수 호출 후 실제 매매과정 처리 후 기록 및 log
def notify_order(self, order):
    # 주문 접수 후 처리 중인 경우 -> pass
    if order.status in [order.Submitted, order.Accepted]:
        return
# 주문 완료시 (체결시) 백테스팅에 반영 (업뎃)
    if order.status in [order.Completed]:
        # 체결된 주문이 매수인 경우
        if order.isbuy():
            # 먼저 매수완료 메시지 & 정보 출력
            self.log(
                'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                (order.executed.price,
                order.executed.value,
                order.executed.comm))	
            # 매수가 & 수수료 업뎃
            self.buyprice = order.executed.price
            self.buycomm = order.executed.comm
        # 체결된 주문이 매도인 경우
        else:
            # 매도완료 메시지 & 정보 출력  
            self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                    order.executed.value,
                    order.executed.comm))
        # 주문 완료시 (체결시) 마지막 주문 체결 날짜 업뎃 (후에 사용 위해)
        self.bar_executed = len(self)
    # 주문에 이상 생긴 경우 예외처리 (ex: 예수금 부족 등)
    elif order.status in [order.Canceled, order.Margin, order.Rejected]:
        self.log('Order Canceled/Margin/Rejected')
    # 주문이 처리 or 취소되었으므로 주문 상태는 다시 None으로 수정
    self.order = None
# 포지션 마감시 발생 수익 log
def notify_trade(self, trade):
    # 포지션 마감 안되었으면 pass
    if not trade.isclosed:
        return
    
    # 포지션 마감 된 경우 수익 정보 출력
    self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' % (trade.pnl, trade.pnlcomm))
    # 모니터링 -> buy, sell 함수 호출
def next(self): # 매일(매 timestep)마다 반복
    # 종가 출력
    self.log('Close, %.2f' % self.dataclose[0])
    # self.order가 None이 아닐 시 (주문 접수 중이며 체결이 안되었으므로 추가 주문 안보냄)
    if self.order:
        return
    # 포지션이 없는 경우
    if not self.position:
        # 매수 조건1
        if self.dataclose[0] < self.dataclose[-1]:
                # 매수 조건2
                if self.dataclose[-1] < self.dataclose[-2]:
                    # 매수 주문 (접수) 출력
                    self.log('BUY CREATE, %.2f' % self.dataclose[0])
                    # 주문 상태 '매수'로 업뎃
                    self.order = self.buy()
    # 포지션 있는 경우
    else:
        # 매도 조건
        if len(self) >= (self.bar_executed + self.params.exitbars):
            # 매도 주문 (접수) 출력
            self.log('SELL CREATE, %.2f' % self.dataclose[0])
            # 주문 상태 '매도'로 업뎃
            self.order = self.sell()
    ### 이 함수에서 조건 설정 가능 !! ###
def stop(self):
        self.log('(Exitbars %2d) Ending Value %.2f' %
                 (self.params.exitbars, self.broker.getvalue()), doprint=True)


# Create a cerebro entity
cerebro = bt.Cerebro()

# Add a strategy
# cerebro.addstrategy(TestStrategy) 

strats = cerebro.optstrategy(
	  TestStrategy,
	  exitbars=range(1, 10))

# Create a Data Feed
data = bt.feeds.YahooFinanceData(dataname='MSFT',
                                 fromdate=datetime(2011, 1, 1),
                                 todate=datetime(2012, 12, 31))

# Add the Data Feed to Cerebro
cerebro.adddata(data)

# Set our desired cash start ($)
cerebro.broker.setcash(100000.0)

# Add a FixedSize sizer according to the stake (한번 매매시 거래할 주식 수)
cerebro.addsizer(bt.sizers.FixedSize, stake=10)

# Set the commission - 0.1% ... divide by 100 to remove the %
cerebro.broker.setcommission(commission=0.001)

# Print out the starting conditions
print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

# Run over everything
cerebro.run()

# Print out the final result
print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

# 백테스팅 결과 전체 시각화
# cerebro.plot()