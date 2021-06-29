from numpy.core.numeric import NaN
import requests
import csv
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt

def get_data():
    url = "https://finance.naver.com/item/sise_day.nhn" # 네이버 금융 일별시세 사이트
    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36"}

    title = ("날짜	종가	전일비	시가	고가	저가	거래량".split("\t"))
    name_code_dict = {"삼성전자": "005930", "SK하이닉스": "000660", "LG화학": "051910", "삼성전자우": "005935", "NAVER": "035420", "삼성바이오로직스": "207940", "카카오": "035720", "현대차": "005380", "삼성SDI": "006400", "셀트리온": "068270"}

    for code in name_code_dict:
        # 엑셀파일 만들기(.scv)
        filename = "{}.csv".format(code)
        f = open(filename, "w", encoding="utf-8-sig", newline="")
        writer = csv.writer(f)
        writer.writerow(title)

        # 마지막 페이지 찾기
        res = requests.get("{}?code={}".format(url, name_code_dict[code]), headers = headers)
        html = BeautifulSoup(res.text, 'lxml') 
        pgrr = html.find('td', class_='pgRR') 
        s = str(pgrr.a['href']).split('=')
        last_page = s[-1]

        # 각각의 페이지 BeautifulSoup 실행
        for page in range(1, int(last_page)+1):   
            page_url = "{}?code={}&page={}".format(url, name_code_dict[code], page)
            res = requests.get(page_url, headers = headers)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, "lxml")

            date_rows = soup.find("table", attrs={"class":"type2"}).find_all("tr")

            # 정보를 저장
            for row in date_rows:
                columns = row.find_all("td")
                if len(columns)<=1:
                    continue
                data = [column.get_text().strip() for column in columns]
                writer.writerow(data)

        print("{} 생성완료".format(code))
    
def make_df(name):

    df = pd.read_csv("{}.csv".format(name), index_col=0)
    df = df[:252]
    df = df.loc[::-1]

    lst = ["종가", "전일비", "시가", "고가", "저가", "거래량"]
    for i in lst:
        smt = []
        for j in df[i]:
            b = j[-11:-8] + j[-7:-4] + j[-3:] # , 앞부분과 ,뒷부분으로 나누어 합쳐줌
            b = int(b) # 숫자로 변환
            smt.append(b) # 리스트에 저장
        smt = pd.Series(smt)
        smt.index = df.index
        df[i] = smt

    return df

def get_moving_average(x, w):
    x = pd.Series(x)
    ma = x.rolling(w).mean()
    return ma

def get_exponential_moving_average(x, w):
    x = pd.Series(x)
    ema = x.ewm(span=w).mean()
    return ema

def get_bollinger_band(x, w=20, k=2): # 2 표준편차 안에 있을 확률 95%
    x = pd.Series(x)
    mbb = x.rolling(w).mean()
    ubb = mbb + k * x.rolling(w).std()
    lbb = mbb - k * x.rolling(w).std()
    return mbb, ubb, lbb

def get_stochastic(x, n=15, m=5, t=3):
    x = pd.Series(x)
    
    ndays_high = x.rolling(window=n, min_periods=1).max() # n일 중 최고가
    ndays_low = x.rolling(window=n, min_periods=1).min() # n일 중 최저가
 
    Fast_k = ((x - ndays_low) / (ndays_high - ndays_low))*100 # Fast%K 구하기
    Fast_D = Fast_k.ewm(span=m).mean() # Fast%D 구하기 = Slow%K와 같음 지수이동평균으로 계산함.
    Slow_D = Fast_D.ewm(span=t).mean() # Slow%D 구하기
 
    # dataframe에 컬럼 추가
    # df = df.assign(Fast_k=Fast_k, Fast_D=Fast_D, Slow_D=Slow_D).dropna()
    
    return Fast_k, Fast_D, Slow_D

def get_RSI(x, w=14):
    
    fluct = [x["종가"][i] - x["종가"][i-1] for i in range(len(x)) ]
    fluct = pd.Series(fluct)
    fluct[0] = NaN # 첫날은 전날이 없기 때문에
    au = fluct.apply(lambda x: x if x>0 else 0)
    ad = fluct.apply(lambda x: x*(-1) if x<0 else 0)
    AU = get_moving_average(au, w)
    AD = get_moving_average(ad, w)
    RSI = 100*(AU/ (AU+AD))
    RSI.index = x.index
    return RSI

def Gold_Dead_Cross(name):
    df = make_df(name)
    returns = (df["종가"][-1]-df["종가"][0])/df["종가"][0] # 수익률
    
    # 이동평균선 제작
    ma5 = get_moving_average(df["종가"],5) # 5평선
    ma20 = get_moving_average(df["종가"],20) # 20평선
    ma60 = get_moving_average(df["종가"],60) # 60평선
    
    # 데이터프레임에 이동평균선 추가
    df["5평선"] = ma5
    df["20평선"] = ma20
    df["60평선"] = ma60
    sub = ma5 - ma20
    df["sub"]=sub

    pres, yest, sums, num_sts = 0, 0, 0, 0

    for i in df.index:
        pres = df["sub"][i] # 오늘자
        if (pres > 0) and (yest < 0): # 매수타이밍
            if num_sts == 0:
                sums -=df["종가"][i]
                num_sts +=1
        if  (pres < 0) and (yest > 0): # 매도타이밍
            if num_sts == 1: 
                sums +=df["종가"][i]
                num_sts -=1
        yest = df["sub"][i] # 이제 어제자

    print("{}의 시장수익률은 {}% 입니다.".format(name, round(returns, 4) * 100))
    print("{}의 골든, 데드 크로스 수익률은 {}% 입니다.".format(name, round(sums/df["종가"][0], 4) * 100))

    # df["종가"].plot(x=df, y="PRICE", c="red")
    # ma5.plot(x=df, y="PRICE",c="blue")
    # ma20.plot(x=df, y="PRICE",c="green")
    # ma60.plot(x=df, y="PRICE",c="black")
    # plt.show()

def MACD(name):
    df = make_df(name)
    returns = (df["종가"][-1]-df["종가"][0])/df["종가"][0] # 수익률
    
    # 지수이동평균선 제작 1970년대 MACD 만들때 미국 주 6일이라 12일은 2주
    ema12 = get_exponential_moving_average(df["종가"], 12) # 12 지수이평선 2주
    ema26 = get_exponential_moving_average(df["종가"], 26) # 26 지수이평선 1달  

    # 데이터프레임에 이동평균선 추가
    df["12 지수이평선"] = ema12
    df["26 지수이평선"] = ema26
    macd = ema12 - ema26
    df["sub"]=macd
    signal = get_exponential_moving_average(df["sub"], 9)
    df["Signal"] = signal
    oscillator = macd - signal 
    df["Oscillator"] = oscillator

    pres, yest, sums, num_sts = 0, 0, 0, 0

    for i in df.index:
        pres = df["Oscillator"][i] # 오늘자
        if (pres > 0) and (yest < 0): # 매수타이밍 MACD가 시그널 선을 아래서 위로 올라갈 때
            if num_sts == 0:
                sums -=df["종가"][i]
                num_sts +=1
        if  (pres < 0) and (yest > 0): # 매도타이밍
            if num_sts == 1: 
                sums +=df["종가"][i]
                num_sts -=1
        yest = df["Oscillator"][i] # 이제 어제자

    print("{}의 시장수익률은 {}% 입니다.".format(name, round(returns, 4) * 100))
    print("{}의 MACD 수익률은 {}% 입니다.".format(name, round(sums/df["종가"][0], 4) * 100))

    # macd.plot(x=df, y="MACD",c="red")
    # signal.plot(x=df, y="Signal",c="blue")
    # oscillator.plot(x=df, y="Oscillator",c="green")
    # plt.show()

def Bollinger(name): # 매수 매도 타이밍 잡기 어려움.
    df = make_df(name)
    returns = (df["종가"][-1]-df["종가"][0])/df["종가"][0] # 수익률

    
    # 볼린저벤드 제작
    mbb, ubb, lbb = get_bollinger_band(df["종가"])

    # 데이터프레임에 이동평균선 추가
    df["MBB"] = mbb
    df["UBB"] = ubb
    df["LBB"] = lbb

    sums, num_sts = 0, 0

    for i in df.index:
        if (df["종가"][i] < df["LBB"][i]): # 매수타이밍 가격이 lbb 아래로 내려갔을 때
            if num_sts == 0:
                sums -=df["종가"][i]
                num_sts +=1
        if  (df["종가"][i] > df["UBB"][i]): # 매도타이밍
            if num_sts == 1: 
                sums +=df["종가"][i]
                num_sts -=1

    print("{}의 시장수익률은 {}% 입니다.".format(name, round(returns, 4) * 100))
    print("{}의 볼린저밴드 수익률은 {}% 입니다.".format(name, round(sums/df["종가"][0], 4) * 100))

    # df["price"].plot(x=df, y="PRICE",c="red")
    # mbb.plot(x=df, y="MBB",c="blue")
    # ubb.plot(x=df, y="UBB",c="green")
    # lbb.plot(x=df, y="LBB",c="black")
    # plt.show()

def Stochastic(name): # 오실레이터가 20이하로 매수, 80이상 매도, 또는 k선이 d위로 오르면 매수 하향이면 매도
    df = make_df(name)
    returns = (df["종가"][-1]-df["종가"][0])/df["종가"][0] # 수익률

    
    # 스토캐스틱 제작
    Fast_k, Fast_D, Slow_D = get_stochastic(df["종가"])

    # 데이터프레임에 스토캐스틱 추가
    df = df.assign(Fast_k=Fast_k, Fast_D=Fast_D, Slow_D=Slow_D).dropna()
    Fast_sub = Fast_k - Fast_D
    Slow_sub = Fast_D - Slow_D
    df["Fast_Sub"]= Fast_sub
    df["Slow_Sub"]= Slow_sub

    pres, yest, sums, num_sts = 0, 0, 0, 0

    for i in df.index:
        pres = df["Slow_Sub"][i] # 오늘자
        if (pres > 0) and (yest < 0): # 매수타이밍 
            if num_sts == 0:
                sums -=df["종가"][i]
                num_sts +=1
        if  (pres < 0) and (yest > 0): # 매도타이밍
            if num_sts == 1: 
                sums +=df["종가"][i]
                num_sts -=1
        yest = df["Slow_Sub"][i] # 이제 어제자

    print("{}의 시장수익률은 {}% 입니다.".format(name, round(returns, 4) * 100))
    print("{}의 스토캐스틱 수익률은 {}% 입니다.".format(name, round(sums/df["종가"][0], 4) * 100))

    # Fast_k.plot(x=df, y="PRICE",c="red")
    # Fast_D.plot(x=df, y="MBB",c="blue")
    # Slow_D.plot(x=df, y="UBB",c="green")
    # plt.axhline(80)
    # plt.axhline(20)

    # # Fast_sub.plot(x=df, y="PRICE",c="Black")
    # # Slow_sub.plot(x=df, y="PRICE",c="Black")


    # plt.show()

def RSI(name):
    df = make_df(name)
    returns = (df["종가"][-1]-df["종가"][0])/df["종가"][0] # 수익률

    RSI = get_RSI(df)
    df["RSI"] = RSI
    pres, yest, sums, num_sts = 0, 0, 0, 0

    for i in df.index:
        pres = df["RSI"][i]
        if (yest < 30 and pres > 30): # 매수타이밍 
            if num_sts == 0:
                sums -=df["종가"][i]
                num_sts +=1
        if  (yest>70 and pres<70): # 매도타이밍
            if num_sts == 1: 
                sums +=df["종가"][i]
                num_sts -=1
        yest = df["RSI"][i]
        
    print("{}의 시장수익률은 {}% 입니다.".format(name, round(returns, 4) * 100))
    print("{}의 RSI 수익률은 {}% 입니다.".format(name, round(sums/df["종가"][0], 4) * 100))

    # RSI.plot(x=df, y="PRICE",c="red")
   
    # plt.show()
    
# MAIN
name_code_dict = {"삼성전자": "005930", "SK하이닉스": "000660", "LG화학": "051910", "삼성전자우": "005935", "NAVER": "035420", "삼성바이오로직스": "207940", "카카오": "035720", "현대차": "005380", "삼성SDI": "006400", "셀트리온": "068270"}

for i in name_code_dict:
    Gold_Dead_Cross(i)
    MACD(i)
    Bollinger(i)
    Stochastic(i)
    RSI(i)



