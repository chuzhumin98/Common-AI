import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

if __name__ == '__main__':
    df1 = pd.read_csv('evaluate/accuracyVSiter_CNN_1.csv', sep=',', encoding='utf-8')
    print(df1)

    plt.figure(0)
    plt.plot(df1['iter'],df1['train'],c='b')
    plt.plot(df1['iter'], df1['validate'], c='r')
    plt.xlabel('iteration')
    plt.ylabel('accuracy')
    plt.ylim([0.9, 1.0])
    plt.legend(['train data', 'validate data'],loc='best')
    plt.title('accuracy vs iteration')
    plt.savefig('image/CNNaccuracyVSiter-1.png', dpi=150)

    #进行平滑
    size = len(df1['iter'])
    trainAccu = np.zeros([3, size])
    trainAccu[0,:] = df1['train']
    trainAccu[1,1:] = trainAccu[0,:size-1]
    trainAccu[2,:size-1] = trainAccu[0,1:]
    trainAccu[1,0] = trainAccu[0,0]
    trainAccu[2,size-1] = trainAccu[0,size-1]
    trainAccu1 = np.mean(trainAccu, axis=0)
    #print(trainAccu1)

    validateAccu = np.zeros([3,size])
    validateAccu[0,:] = df1['validate']
    validateAccu[1,1:] = validateAccu[0,:size-1]
    validateAccu[2,:size-1] = validateAccu[0,1:]
    validateAccu[1,0] = validateAccu[0,0]
    validateAccu[2,size-1] = validateAccu[0,size-1]
    validateAccu1 = np.mean(validateAccu, axis=0)
    #print(validateAccu1)

    plt.figure(1)
    plt.plot(df1['iter'], trainAccu1, c='b')
    plt.plot(df1['iter'], validateAccu1, c='r')
    plt.xlabel('iteration')
    plt.ylabel('accuracy')
    plt.ylim([0.9, 1.0])
    plt.legend(['train data', 'validate data'], loc='best')
    plt.title('accuracy vs iteration after smoothing')
    plt.savefig('image/CNNaccuracyVSiter-1_1.png', dpi=150)