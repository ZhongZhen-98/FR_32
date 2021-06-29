#1
apart = [[101,102,103,104],[201,202,203,204],[301,302,303,304],[401,402,403,404]]
arrears = [101, 203, 301, 404]

for i in apart:
    for j in i:
        if not(j in arrears):
            print("Newspaper delivery: {}".format(j))


#2
num_lst = [1169, 1208, 865, 1243, 290]
def LastDisitSort(lst):
    last_num = []
    num_dic = {}
    answer = []
    for i in lst:
        num_dic[i%10] = i
        last_num.append(i%10)
    last_num.sort(reverse=True)
    for j in last_num:
        answer.append(num_dic[j])
    return answer

print(LastDisitSort(num_lst))

#3
odd_lst = [1169, 290, 865, 1243, 1208]
def OddDisitSort(lst):
    sum_odd = []
    num_dic = {}
    answer = []
    for i in lst:
        sums = 0
        for j in str(i):
            if int(j)%2 == 1:
                sums += int(j)
        sum_odd.append(sums)
        num_dic[sums]=i
    sum_odd.sort(reverse=True)
    for s in sum_odd:
        answer.append(num_dic[s])
    return answer

print(OddDisitSort(odd_lst))



#4
def countAllLetters (sentence):
    alpha = []
    sentence = sentence.lower()
    for i in sentence:
        if i.isalpha() == True:
            alpha.append(i)
    a_set = set(alpha)
    answer = {}
    for i in a_set:
        answer[i]= alpha.count(i)
    return answer

sentence = "This is a short line"
print(countAllLetters(sentence))

#5
def count_characters(value):
    value_set = set(value)
    return len(value_set)

value = 'abbccdddeee'
print(count_characters(value))