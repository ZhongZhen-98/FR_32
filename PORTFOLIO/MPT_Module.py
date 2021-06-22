import requests
import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import scipy.optimize as sco

name_code_dict = {"삼성전자": "005930", "SK하이닉스": "000660", "LG화학": "051910", "삼성전자우": "005935", "NAVER": "035420", "삼성바이오로직스": "207940", "카카오": "035720", "현대차": "005380", "삼성SDI": "006400", "셀트리온": "068270"}
rf = 0 #무위험수익률
def top_200():
    df = pd.read_csv("시가총액 1~200.csv", header = 0, index_col = 0, na_values=0) #Finished\Crawling\Crawling Stock_py\cr_11_Stock.py
    a = df["종목명"]
    lst = list(a)
    return lst # 시총 200종목 종목명

def get_code_name():
    data = pd.read_html("http://kind.krx.co.kr/corpgeneral/corpList.do?method=download", header = 0, index_col=0)[0] # 상장된 기업만 나옴 ETF 나오지 않음,
    data = data["종목코드"]
    data = data.map("{:06d}".format)
    return data

def get_price_data():
    url = "https://finance.naver.com/item/sise_day.nhn" # 네이버 금융 일별시세 사이트
    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36"}

    title = ("날짜	종가	전일비	시가	고가	저가	거래량".split("\t"))

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

def read_data(n):
    # 최근 n개의 데이터만 확인
    d_df = pd.read_csv("삼성전자.csv", header=0, na_values=0)
    date = d_df["날짜"][:n] # 날짜 데이터 가져오기
    dic = {}
    for name in name_code_dict:
        p_df = pd.read_csv("{}.csv".format(name), index_col = 0, header=0, na_values=0) # 엑셀파일 열기
        p_df = p_df["종가"][:n] # 최근 50개만 확인
        p_df = p_df.dropna() 
        p_df_lst = p_df.values # value값을 리스트에 저장
        price = []
        for i in p_df_lst:
            b = i[-11:-8] + i[-7:-4] + i[-3:] # , 앞부분과 ,뒷부분으로 나누어 합쳐줌
            b = int(b) # 숫자로 변환
            price.append(b) # 리스트에 저장
        dic[name] = price

    df = pd.DataFrame(dic, index= date) # 날짜별, 기업별 종가 데이터프레임

    return df

def cal_rtnrisk(df):
    df_returns = np.log(df.pct_change()+1) # 일간 로그 수익률
    df_returns = df_returns.dropna()
    df_ann_returns = df_returns.mean()* 252 # 연간 로그 수익률
    df_returns_cov = df_returns.cov() # 일간 로그 수익률 공분산
    df_ann_returns_cov = df_returns_cov * 252 # 연간 로그 수익률 공분산
    
    return df_ann_returns, df_ann_returns_cov

def make_df(df_ann_returns, df_ann_returns_cov): # 연수익률, 연공분산, 무위험이자율
    port_returns = []
    port_risk = []
    port_weights = [] 
    sharp_ratio = []
    for i in range(20000):
        weights = np.random.random_sample(len(name_code_dict)) # 기업 개수 집어넣기
        weights /= np.sum(weights) # 가중합 구하기
        preturns = np.dot(weights, df_ann_returns)
        prisk = np.sqrt(np.dot(weights.T, np.dot(df_ann_returns_cov,weights)))
        port_returns.append(preturns)
        port_risk.append(prisk)
        port_weights.append(weights)
        sharp_ratio.append((preturns-rf)/prisk) 

    portfolio = {"Returns":port_returns, "Risk": port_risk, "Sharpe": sharp_ratio}

    for i, s in enumerate(name_code_dict):      
        portfolio[s] = [weight[i] for weight in port_weights] 

    df = pd.DataFrame(portfolio)

    df = df[["Returns", "Risk", "Sharpe"] + [s for s in name_code_dict]] 
    
    max_sharpe = df.loc[df["Sharpe"] == df["Sharpe"].max()] 
    
    min_risk = df.loc[df["Risk"] == df["Risk"].min()]

    return df, max_sharpe, min_risk, port_weights

def efficient_frontier(df):
    df.plot.scatter(x="Risk", y="Returns", figsize = (8,6), grid = True)
    plt.title("Risk and Return")
    plt.xlabel("Risk")
    plt.ylabel("Expected Returns")
    plt.show()

def portfolio_optimization(df, max_sharpe, min_risk):
    
    df.plot.scatter(x="Risk", y="Returns", c="Sharpe", cmap="plasma", edgecolors="k", figsize = (11,7), grid = True)
    # plt.scatter(x=max_sharpe["Risk"], y=max_sharpe["Returns"], c="r", marker="*", s=300)
    # plt.scatter(x=min_risk["Risk"], y=min_risk["Returns"], c="r", marker="X", s=200)
    # plt.title("Portfolio Optimization")
    # plt.xlabel("Risk")
    # plt.ylabel("Expected Returns")


def statistics(weights): # 개수 적어두기
    df = read_data(1000)
    ann_ret, ann_cov = cal_rtnrisk(df)

    weights=np.array(weights)
    returns = np.dot(weights, ann_ret) 
    risk = np.sqrt(np.dot(weights.T, np.dot(ann_cov, weights))) 
    sharpe_ratio = (returns-rf)/risk

    return np.array([returns, risk, sharpe_ratio])

def min_func_sharpe(weights):
    return -statistics(weights)[2]

def min_func_variance(weights):
    return statistics(weights)[1]**2

def min_func_port(weights):
    return statistics(weights)[1]

def optimize_sharpe():
    cons = ({'type':'eq', 'fun':lambda x:np.sum(x)-1}) # 수익률 마이너스인 점 제외 추가해보기
    bnds = tuple((0,1) for x in range(len(name_code_dict)))
    initial_weights = len(name_code_dict)*[1./len(name_code_dict)]
    opts = sco.minimize(min_func_sharpe, initial_weights, method='SLSQP', bounds=bnds, constraints=cons)

    return opts

def optimize_vari():
    cons = ({'type':'eq', 'fun':lambda x:np.sum(x)-1}) # 수익률 마이너스인 점 제외 추가해보기
    bnds = tuple((0,1) for x in range(len(name_code_dict)))
    initial_weights = len(name_code_dict)*[1./len(name_code_dict)]
    optvs = sco.minimize(min_func_variance, initial_weights, method='SLSQP', bounds=bnds, constraints=cons)

    return optvs

def optimize_vols():
    cons = ({'type':'eq', 'fun':lambda x:statistics(x)[0]-goal_ret}, {'type':'eq', 'fun':lambda x:np.sum(x)-1})
    bnds = tuple((0,1) for x in range(len(name_code_dict)))
    initial_weights = len(name_code_dict)*[1./len(name_code_dict)]
    set_ret = np.linspace(0.0, 0.4, 10)
    goal_vols = []
    for goal_ret in set_ret:
        cons = ({'type':'eq', 'fun':lambda x:statistics(x)[0]-goal_ret}, {'type':'eq', 'fun':lambda x:np.sum(x)-1})
        eff = sco.minimize(min_func_port, initial_weights, method='SLSQP', bounds=bnds, constraints=cons)
        goal_vols.append(eff["fun"])
    goal_vols = np.array(goal_vols)

    return goal_vols, set_ret

def stat_Port_Opi_plot():

    df = read_data(1000)
    df_ann_returns, df_ann_returns_cov = cal_rtnrisk(df)
    df, max_sharpe, min_risk, port_weights = make_df(df_ann_returns, df_ann_returns_cov)
    df.plot.scatter(x='Risk', y='Returns', c='Sharpe', cmap='viridis', edgecolors='k', figsize=(11,7), grid=True)  
    goal_vols, set_ret = optimize_vols()
    opts = optimize_sharpe()
    optvs = optimize_vari()
    plt.scatter(x=goal_vols, y=set_ret, c='r', marker='x', s=10)
    plt.scatter(x=statistics(opts['x'])[1], y=statistics(opts['x'])[0], c='b', marker='*', s=300) 
    plt.scatter(x=statistics(optvs['x'])[1], y=statistics(optvs['x'])[0], c='r',marker='X', s=200)  
    plt.title('Portfolio Optimization')
    plt.xlabel('Risk') 
    plt.ylabel('Expected Returns') 
    plt.show()
