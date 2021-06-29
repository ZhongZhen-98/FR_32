# list & for

data = [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [7.89, 8.01, 9.1, 8.86, 10.34, 14.1, 13.32, 12.09, 12.56, 12.4]]

x = []
y = []
timestep = 2

for i in range(len(data[0])-timestep):
    t1 = []
    for j in range(0, timestep):
        t2 = []
        t2.append(data[0][i+j])
        t2.append(data[1][i+j])
        t1.append(t2)
    x.append(t1)
    y.append(data[1][i+timestep])

print(x)
print(y)


# if, else, while, dict

dict = {
    "종목1" : [
        {"시가" : 55000, "종가" : 60000}, {"시가" : 62000, "종가" : 70000}, {"시가" : 71000, "종가" : 68900}
    ],
    "종목2" : [
        {"시가" : 30, "종가" : 32}, {"시가" : 31.5, "종가" : 34}, {"시가" : 33, "현재가" : 34.2}
    ]
}

keys = list(dict.keys())
for i in range(len(keys)):
    j = 0
    while (j < len(dict[keys[i]])):
        if "종가" not in dict[keys[i]][j].keys():
            break
        j += 1
    print(keys[i] + " 일별 데이터 개수: ", j)
    if j < len(dict[keys[i]]) and dict[keys[i]][j]["현재가"] > dict[keys[i]][j]["시가"] * 1.03:
        print(keys[i] + " BUY AT ", dict[keys[i]][j]["현재가"])
    else:
        print(keys[i] + " 상장된 시장 장 마감")

# 함수

def aboveMean(list):
    s = sum(list)
    count = 0
    mean = s / len(list)
    for i in range(len(list)):
        if list[i] > mean:
            count += 1
    return count

test = [0, 0, 0, 1]
print(aboveMean(data[1]), aboveMean(test))

## 위의 데이터 분석에 함수 사용??


# 클래스 (생성자, 인스턴스, 상속) - 간단한 백테스팅 !!

class Portfolio: # 시간별 포트폴리오가치, 보유 현금 계산용 클래스

    def __init__(self, principal, data):
        self.d = data
        self.cash = principal
        self.item = 0
        self.portVal = 0
        self.s = False # 매도 한 날 매수 안 하게끔 설정

    def buy(self, time): # 매수 반영 (현금, 보유 수)
        if self.d[time] <= self.cash and self.item == 0 and self.s is False:
            self.cash -= self.d[time]
            self.item += 1

    def sell(self, time): # 매도 반영 (현금, 보유 수)
        if self.item != 0:
            self.cash += self.d[time]
            self.item -= 1
            self.s = True

    def portf(self, time): # 포트폴리오 가치 계산 & 값들 출력
        self.portVal = self.d[time] * self.item
        print("보유 수: ", self.item)
        print("현재 보유 현금: ", self.cash)
        print("현재 보유자산 가치: ", self.portVal)
        self.s = False

class MyPort(Portfolio): # 상속 (내 전략 조건 구성)

    def __init__(self, strategy_name, target_profit, data, buyCond, sellCond1, sellCond2, principal=100):
        self.strategy_name = strategy_name
        self.target_profit = target_profit
        self.data = data
        self.buyCond = buyCond
        self.sellCond1 = sellCond1
        self.sellCond2 = sellCond2
        super().__init__(principal, data)

    def action(self, time): # 조건에 맞으면 매수 or 매도 실행
        if self.data[time] > self.sellCond1 or self.data[time] < self.sellCond2:
            self.sell(time)
        if self.data[time] > self.buyCond:
            self.buy(time)

data2 = [10.01, 9.10, 8.86, 10.34, 14.10, 13.32, 12.09, 12.56, 12.40] # 한 종목
## 10이상이면 매수  // 12이상, 9이하면 매도 - 1주씩 매매

backtest = MyPort(strategy_name="전략1", target_profit="30%", data=data2, buyCond=10, sellCond1=12, sellCond2=9)
print(backtest.strategy_name)
print("목표수익률: ", backtest.target_profit)
print("시작금: ", backtest.cash)
print("대상데이터: ", backtest.d)
print("")
for t in range(len(data2)):
    backtest.action(t)
    backtest.portf(t)
    print("")
    
'''
<종목 수 추가시>
1. 매수 매도 동일 실행 가능 (서로 종목이 다를 경우)
2. 종목 별 매매 정보(보유 수, 매수매도가격?) 딕셔너리 등에 저장 필요

<매수 매도 조건 복잡화 하면>
1. 클래스 구성형태 자체를 바꿔야 할 가능성이 높다 - 입맛에 맞춰서 (클래스를 추가시키고 상속관계 복잡화... 등)
    -> action 함수의 조건 부분의 복잡화도 가능, 클래스 생성자에서 받는 parameter 추가
    -> parameter 수가 너무 많거나 시간별로 유동적인(dynamic) 경우:
        MyPort 클래스의 기본 변수를 미리 설정해놓고, 시간 별로 조건에 맞춰 변화시킨다
2. 시간별로 종목들 돌아가며(검색) 특정 조건이 맞을 시 매매하는 방법??
'''
