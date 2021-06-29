import pandas as pd
my_list = ["2021-04-13", 3.14, "ABC", 100, True]
my_dict = {"a":1, "b":2, "c":3}

sr1 = pd.Series(my_list)
sr2 = pd.Series(my_dict)
print(sr1) 
print(type(sr1))

print(sr2) 
print(type(sr2))

my_tuple = ("나종진", "1998-07-21", "남", True)
sr3 = pd.Series(my_tuple, index = ["이름", "생년월일", "성별", "학생여부"])

print(sr3)
print(sr3[:3])

w_index = ['어제 온도', '오늘 온도', '내일 온도']
korean_weather = pd.Series((25,23,22), index=w_index)
japan_weather = pd.Series((26,22,24), index=w_index)

sub_tem = pd.DataFrame([korean_weather - japan_weather], index=["온도차"])
print(sub_tem)




import seaborn as sns
import pandas as pd

titanic = sns.load_dataset('titanic')

# 1. 타이타닉 객체에서 pclass, sex, age, deck, alone 5개 열을 선택하여 데이터프레임 df를 만들고 위의 다섯개의 행과 아래 다섯개의 행만 보이게 한번에 출력해보세요.

print("1번")
df = titanic[["pclass", "sex", "age", "deck", "alone"]]
print(df)

# 2. 위에서 만든 데이터프레임 df의 열 중 pclass가 가지고 있는 고유값의 종류와 데이터 개수를 시리즈 객체로 반환하세요. 

print("2번")
print(df["pclass"].value_counts())

# 3. deck 열에서 볼 수 있는 NaN값을 'F'으로 바꾼 후 출력해보세요.

print("3번")
df["deck"] = df["deck"].fillna("F")
print(df)

# 4. 제일 뒤 열 인덱스와 제일 앞 행 인덱스를 삭제한 후 출력하세요.

print("4번")
df = df.drop("alone", axis=1)
df = df.drop(0)
print(df)

# 5. age열의 평균값, 최소값, 최대값을 추출하여 출력해보세요.

print("5번")
print(df["age"].mean())
print(df["age"].min())
print(df["age"].max())

# 6. age열의 NaN값을 뒤에 오는 값으로 채운 후 출력해보세요.

print("6번")
df["age"] = df["age"].fillna(method='bfill')
print(df)

# 7. 판다스 내장 그래프 도구를 활용하여 타이타닉 데이터프레임으로 하나의 그래프를 자유롭게 그려보세요.
%matplotlib inline
print("7번")
df["sex"].value_counts().plot(kind="pie")


