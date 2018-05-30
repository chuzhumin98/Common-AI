import matplotlib.pyplot as plt
from LoadData import *
import numpy as np

if __name__ == '__main__':
    # 导入输入训练集
    trainData, trainLabels = LoadTrainData('train.csv')
    size = len(trainLabels)  # 总的样本点个数
    indexArray = np.array(range(size), dtype=int)  # 下标数组
    np.random.shuffle(indexArray)
    for i in range(4):
        plt.subplot(221+i)
        image = trainData[indexArray[i], :]
        image = np.reshape(image, [28, 28])
        plt.imshow(image, cmap='gray')
    plt.savefig('image/digits.png')
    print(trainLabels[indexArray[0:4]])
