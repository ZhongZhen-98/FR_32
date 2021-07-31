import numpy as np
import matplotlib.pyplot as plt

# GATE
def AND(x1, x2):
    x = np.array([x1, x2])
    w = np.array([0.5, 0.5])
    theta = 0.7
    if np.sum(x*w) <= theta:
        return 0
    else:
        return 1

def OR(x1, x2):
    x = np.array([x1, x2])
    w = np.array([0.5, 0.5])
    theta = 0
    if np.sum(x*w) <= theta:
        return 0
    else:
        return 1

def NAND(x1, x2):
    x = np.array([x1, x2])
    w = np.array([-0.5, -0.5])
    theta = -0.7
    if np.sum(x*w) <= theta:
        return 0
    else:
        return 1

def XOR(x1,x2):
    return AND(NAND(x1,x2), OR(x1, x2))

# 신경망함수
def step_function(x_data):
    return (x_data>0).astype(np.int)

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def relu(x):
    return np.maximum(0,x)

def identity(x):
    return x

def softmax(a):
    C = np.max(a)
    exp_a = np.exp(a-C)
    sum_a = np.sum(exp_a)
    return exp_a / sum_a

def init_network():
    network = {}
    network["W1"] = np.array([[1,3,5],[2,4,6]])
    network["W2"] = np.array([[1,2],[3,4],[5,6]])
    network["W3"] = np.array([[1,2],[3,4]])
    return network

# 손실함수
def MSE(y, t):
    return (1/2)*np.sum((y-k)**2)

def cross_entrpy_error(y, t):
    delta = 1e-7 # 진수가 0이면 로그값 -inf로 출력되어 작은 값 더함
    return -np.sum(t*np.log(y+delta))

def crossEntropyError(y, t):
    delta = 1e-7
    return -np.sum(t*np.log(y+delta)) / y.shape[0]

# 수치미분
def numerical_diff(f, x):
    h = 1e-4
    return (f(x+h) - h(x-h)) / 2*h

# 편미분
def numerical_gradient(f, x):
    h = 1e-4
    grad = np.zeros_like(x)

    for idx in range(x.size):
        tmp_val = x[idx]
        x[idx] = tmp_val + h
        hxh1 = f(x)
        x[idx] = tmp_val - h
        grad[idx] = (fxh1 - fxh2) / 2*h
        x[idx] = tmp_val
    
    return grad


# 신경망 구현
def forward(network, x):
    W1, W2, W3 = network["W1"], network["W2"], network["W3"]
    y = np.dot(x, W1)
    y_hat = sigmoid(y)
    k = np.dot(y_hat, W2)
    k_hat = sigmoid(k)
    j = np.dot(k_hat, W3)
    j_hat = identity(j)
    return j_hat

# MNIST 신경망 구현




# Main

network = init_network()
x = np.array([1,2])
y = forward(network, x)
print(y)
