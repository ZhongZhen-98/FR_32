import pandas as pd
import simfin as sf

# 각자 원하는 디렉터리로 설정
sf.set_data_dir('./SummerStudy/Week6')
sf.set_api_key(api_key='free')

market = "us"

# ttm = trailing twelve months => 분기말+1달 기준 근 1년으로 계산한 데이터
# => 각종 재무지표 계산시 유용
df_income_ttm = sf.load_income(variant='ttm', market=market)
df_balance_ttm = sf.load_balance(variant='ttm', market=market)
df_cashflow_ttm = sf.load_cashflow(variant='ttm', market=market)

df_prices = sf.load_shareprices(variant='daily', market=market)

## 백테스팅 하기까지 단계 ##
# 1. 각 항목별로 column 뭐 있는지 확인 -> 필요한 column들 가져다 가공하기 위함
# 2. 필요 데이터 끌어다가 원하는 비율(재무지표) 산출하기
# 3. 종목별 분기별 해당 비율만 담고 있는 데이터프레임 반환 (한 분기는 모두 같은 값으로 forward fill하기)
# 4. 종목별로 일별(바꿔도 됨) 가격 데이터 담긴 데이터프레임과 3번에서 만든 데이터프레임 병합 -> csv파일로 저장
# 5. 4번에서 만들어진 최종 종목별 csv파일들 data feed로 backtrader에 모두 추가
# 6. backtrader의 strategy class 안에서 조건 설정 (위의 데이터들 이용)
# 7. backtrader의 cerebro engine으로 백테스팅 실행

## 1.

# 항목들(전체 column 이름들 - index column 포함) 확인
sf.info_datasets('income')
sf.info_datasets('balance')
sf.info_datasets('cashflow')

# 인덱스 column 확인
print(df_income_ttm.index.names)
print(df_balance_ttm.index.names)
print(df_cashflow_ttm.index.names)

## 2 & 3.

# 기본 제공 재무지표들 (영업이익률, 부채비율, ROA, ROE 등)
# => prices 데이터 넣어주고 'ffill' 옵션 주면 일별로 같은 분기는 지표들 같은 값으로 나오게 설정가능
df_fin_signals = sf.fin_signals(df_prices=df_prices,
                                df_income_ttm=df_income_ttm,
                                df_balance_ttm=df_balance_ttm,
                                df_cashflow_ttm=df_cashflow_ttm,
                                fill_method='ffill')

print(df_fin_signals.dropna().head())

# 기본 제공 성장지표들
# => 분기성장률 등도 계산하므로 분기별 데이터를 추가해주어야 함
df_income_qrt = sf.load_income(variant='quarterly', market=market)
df_balance_qrt = sf.load_balance(variant='quarterly', market=market)
df_cashflow_qrt = sf.load_cashflow(variant='quarterly', market=market)

df_growth_signals = sf.growth_signals(df_prices=df_prices,
                                      df_income_ttm=df_income_ttm,
                                      df_income_qrt=df_income_qrt,
                                      df_balance_ttm=df_balance_ttm,
                                      df_balance_qrt=df_balance_qrt,
                                      df_cashflow_ttm=df_cashflow_ttm,
                                      df_cashflow_qrt=df_cashflow_qrt,
                                      fill_method='ffill')

print(df_growth_signals.dropna().head())

# 기본 제공 밸류에이션 지표들 (P/B, P/E 등)
df_val_signals = sf.val_signals(df_prices=df_prices,
                                df_income_ttm=df_income_ttm,
                                df_balance_ttm=df_balance_ttm,
                                df_cashflow_ttm=df_cashflow_ttm) # forward-fill 불필요

print(df_val_signals.dropna().head())

# 예시로 각 분야별 지표 당 한가지씩 뽑아서 새로운 데이터프레임에 저장 (백테스팅 사용 위함)
# => Net Profit Margin, Sales Growth QOQ, Price to Book Value

df1 = df_fin_signals['Net Profit Margin']
df2 = df_growth_signals['Sales Growth QOQ']
df3 = df_val_signals['Price to Book Value']

df_12 = pd.concat([df1, df2], axis=1)
df_123 = pd.concat([df_12, df3], axis=1)

# 이외 원하는 데이터가 있다면 데이터프레임들 가공해서 산출해야 함 (pandas 다루기)

## 4.

# 티커마다 나눠주기
df_prices = df_prices[['Open', 'High', 'Low', 'Close', 'Volume']]
df_tickers = sf.load_companies(market=market)

# 20개 종목 대상으로 테스팅 해볼 시 (csv파일로 디렉터리에 저장)
for ticker in df_tickers.index[0:20]:
    try:
        df = pd.concat([df_prices.loc[ticker], df_123.loc[ticker]], axis=1)
        df.to_csv('./SummerStudy/Week6/us_stocks_db/' + ticker + '.csv')
    except Exception as e:
        print(e)

# 전체 종목 대상으로 날짜 조건으로 고르는 경우
# (백테스팅 코드는 이 방식으로 csv파일들 db구축한 것 가정하고 시작)
for ticker in df_tickers.index:
    try:
        df = pd.concat([df_prices.loc[ticker], df_123.loc[ticker]], axis=1)
        # 테스팅 기간 (18, 19 2년) 데이터 존재하는 경우
        if len(df) >= 400 and int(df.index[0].strftime("%Y")) < 2017 and int(df.index[-1].strftime("%Y")) > 2019:
            df.to_csv('./SummerStudy/Week6/us_stocks_db/' + ticker + '.csv')
        else:
            continue
    except Exception as e:
        print(e)

## 5 & 6 & 7. (Backtrader 부분) backtrader_multiple_stocks_augmented_data.py 에서 진행
## 6주차 Multiple Data Feeds 항목 (노션페이지) 에서 진행