import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 进行k = 3的平滑
def smoothing(data):
    size = len(data)
    trainAccu = np.zeros([3, size])
    trainAccu[0, :] = data
    trainAccu[1, 1:] = trainAccu[0, :size - 1]
    trainAccu[2, :size - 1] = trainAccu[0, 1:]
    trainAccu[1, 0] = trainAccu[0, 0]
    trainAccu[2, size - 1] = trainAccu[0, size - 1]
    trainAccu1 = np.mean(trainAccu, axis=0)
    return trainAccu1

if __name__ == '__main__':
    df1 = pd.read_csv('evaluate/accuracyVSiter_CNN_3.csv', sep=',', encoding='utf-8')
    print(df1)

    plt.figure(0)
    plt.plot(df1['iter'],df1['train'],c='b')
    plt.plot(df1['iter'], df1['validate'], c='r')
    plt.xlabel('iteration')
    plt.ylabel('accuracy')
    plt.ylim([0.9, 1.0])
    plt.legend(['train data', 'validate data'],loc='best')
    plt.title('accuracy vs iteration')
    plt.savefig('image/CNNaccuracyVSiter-3.png', dpi=150)

    #进行平滑
    trainAccu1 = smoothing(df1['train'])
    validateAccu1 = smoothing(df1['validate'])

    plt.figure(1)
    plt.plot(df1['iter'], trainAccu1, c='b')
    plt.plot(df1['iter'], validateAccu1, c='r')
    plt.xlabel('iteration')
    plt.ylabel('accuracy')
    plt.ylim([0.9, 1.0])
    plt.legend(['train data', 'validate data'], loc='best')
    plt.title('accuracy vs iteration after smoothing')
    plt.savefig('image/CNNaccuracyVSiter-3_1.png', dpi=150)