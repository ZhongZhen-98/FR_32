# coding: utf-8
import matplotlib.pyplot as plt
from matplotlib.image import imread

img = imread('FR\특세\deep-learning-from-scratch-master\dataset\cactus.png') # 이미지 읽어오기
plt.imshow(img)

plt.show()
