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

    df1 = pd.read_csv('evaluate/accuracyVSiter_RNN_1.csv', sep=',', encoding='utf-8')
    print(df1)
    '''
    plt.figure(0)
    plt.plot(df1['iter'],df1['train'],c='b')
    plt.plot(df1['iter'], df1['validate'], c='r')
    plt.xlabel('iteration')
    plt.ylabel('accuracy')
    plt.ylim([0.9, 1.0])
    plt.legend(['train data', 'validate data'],loc='best')
    plt.title('accuracy vs iteration')
    plt.savefig('image/CNNaccuracyVSiter-3.png', dpi=150)
    '''
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
    plt.savefig('image/RNNaccuracyVSiter-1_1.png', dpi=150)


    '''
    df1 = pd.read_csv('evaluate/accuracyVSiter_CNN_3.csv', sep=',', encoding='utf-8')
    df2 = pd.read_csv('evaluate/accuracyVSiter_CNN_2.csv', sep=',', encoding='utf-8')
    df3 = pd.read_csv('evaluate/accuracyVSiter_CNN_4.csv', sep=',', encoding='utf-8')
    df4 = pd.read_csv('evaluate/accuracyVSiter_CNN_6.csv', sep=',', encoding='utf-8')
    print(len(df1))
    kernelSizes = ['3','5','7','9']

    trainAccus = np.zeros([len(kernelSizes), len(df1)], dtype=np.float32)
    validateAccus = np.zeros([len(kernelSizes), len(df1)], dtype=np.float32)
    trainAccus[0,:] = smoothing(df1['train'])
    trainAccus[1, :] = smoothing(df2['train'])
    trainAccus[2, :] = smoothing(df3['train'])
    trainAccus[3, :] = smoothing(df4['train'])

    validateAccus[0,:] = smoothing(df1['validate'])
    validateAccus[1, :] = smoothing(df2['validate'])
    validateAccus[2, :] = smoothing(df3['validate'])
    validateAccus[3, :] = smoothing(df4['validate'])

    plt.figure(2)
    plt.plot(df1['iter'],validateAccus[0,:], lw=1.5)
    plt.plot(df1['iter'], validateAccus[1, :], lw=1.5)
    plt.plot(df1['iter'], validateAccus[2, :], lw=1.5)
    plt.plot(df1['iter'], validateAccus[3, :], lw=1.5)
    plt.ylim([0.9, 1.0])
    plt.xlabel('iterate number')
    plt.ylabel('validate accuary')
    plt.title('iter vs validate accuaray')
    plt.legend(kernelSizes,loc='best')
    plt.savefig('image/iter vs validate_kernel_v1.png',dpi=150)

    plt.figure(3)
    plt.plot(df1['iter'], trainAccus[0, :], lw=1.5)
    plt.plot(df1['iter'], trainAccus[1, :], lw=1.5)
    plt.plot(df1['iter'], trainAccus[2, :], lw=1.5)
    plt.plot(df1['iter'], trainAccus[3, :], lw=1.5)
    plt.ylim([0.9, 1.0])
    plt.xlabel('iterate number')
    plt.ylabel('train accuary')
    plt.title('iter vs train accuaray')
    plt.legend(kernelSizes, loc='best')
    plt.savefig('image/iter vs train_kernel_v1.png', dpi=150)
    '''
    '''
    df1 = pd.read_csv('evaluate/accuracyVSiter_CNN_7.csv', sep=',', encoding='utf-8')
    df2 = pd.read_csv('evaluate/accuracyVSiter_CNN_8.csv', sep=',', encoding='utf-8')
    df3 = pd.read_csv('evaluate/accuracyVSiter_CNN_2.csv', sep=',', encoding='utf-8')
    df4 = pd.read_csv('evaluate/accuracyVSiter_CNN_9.csv', sep=',', encoding='utf-8')
    print(len(df1))
    batchSizes = ['1','10','50','250']

    trainAccus = np.zeros([len(batchSizes), len(df1)], dtype=np.float32)
    validateAccus = np.zeros([len(batchSizes), len(df1)], dtype=np.float32)
    trainAccus[0, :] = smoothing(df1['train'])
    trainAccus[1, :] = smoothing(df2['train'])
    trainAccus[2, :] = smoothing(df3['train'])
    trainAccus[3, :] = smoothing(df4['train'])

    validateAccus[0, :] = smoothing(df1['validate'])
    validateAccus[1, :] = smoothing(df2['validate'])
    validateAccus[2, :] = smoothing(df3['validate'])
    validateAccus[3, :] = smoothing(df4['validate'])

    plt.figure(2)
    plt.plot(df1['iter'], validateAccus[0, :], lw=1.5)
    plt.plot(df1['iter'], validateAccus[1, :], lw=1.5)
    plt.plot(df1['iter'], validateAccus[2, :], lw=1.5)
    plt.plot(df1['iter'], validateAccus[3, :], lw=1.5)
    plt.ylim([0.9, 1.0])
    plt.xlabel('iterate number')
    plt.ylabel('validate accuary')
    plt.title('iter vs validate accuaray')
    plt.legend(batchSizes, loc='best')
    plt.savefig('image/iter vs validate_batch_v1.png', dpi=150)

    plt.figure(3)
    plt.plot(df1['iter'], trainAccus[0, :], lw=1.5)
    plt.plot(df1['iter'], trainAccus[1, :], lw=1.5)
    plt.plot(df1['iter'], trainAccus[2, :], lw=1.5)
    plt.plot(df1['iter'], trainAccus[3, :], lw=1.5)
    plt.ylim([0.9, 1.0])
    plt.xlabel('iterate number')
    plt.ylabel('train accuary')
    plt.title('iter vs train accuaray')
    plt.legend(batchSizes, loc='best')
    plt.savefig('image/iter vs train_batch_v1.png', dpi=150)
    '''
    '''
    df1 = pd.read_csv('evaluate/accuracyVSiter_CNN_11.csv', sep=',', encoding='utf-8')
    df2 = pd.read_csv('evaluate/accuracyVSiter_CNN_12.csv', sep=',', encoding='utf-8')
    df3 = pd.read_csv('evaluate/accuracyVSiter_CNN_13.csv', sep=',', encoding='utf-8')
    df4 = pd.read_csv('evaluate/accuracyVSiter_CNN_14.csv', sep=',', encoding='utf-8')
    print(len(df1))
    batchSizes = ['0.01','0.001','0.0001','0.00001']

    trainAccus = np.zeros([len(batchSizes), len(df1)], dtype=np.float32)
    validateAccus = np.zeros([len(batchSizes), len(df1)], dtype=np.float32)
    trainAccus[0, :] = smoothing(df1['train'])
    trainAccus[1, :] = smoothing(df2['train'])
    trainAccus[2, :] = smoothing(df3['train'])
    trainAccus[3, :] = smoothing(df4['train'])

    validateAccus[0, :] = smoothing(df1['validate'])
    validateAccus[1, :] = smoothing(df2['validate'])
    validateAccus[2, :] = smoothing(df3['validate'])
    validateAccus[3, :] = smoothing(df4['validate'])

    plt.figure(6)
    plt.plot(df1['iter'], validateAccus[0, :], lw=1.5)
    plt.plot(df1['iter'], validateAccus[1, :], lw=1.5)
    plt.plot(df1['iter'], validateAccus[2, :], lw=1.5)
    plt.plot(df1['iter'], validateAccus[3, :], lw=1.5)
    plt.ylim([0.9, 1.0])
    plt.xlabel('iterate number')
    plt.ylabel('validate accuary')
    plt.title('iter vs validate accuaray')
    plt.legend(batchSizes, loc='best')
    plt.savefig('image/iter vs validate_lr_v1.png', dpi=150)

    plt.figure(7)
    plt.plot(df1['iter'], trainAccus[0, :], lw=1.5)
    plt.plot(df1['iter'], trainAccus[1, :], lw=1.5)
    plt.plot(df1['iter'], trainAccus[2, :], lw=1.5)
    plt.plot(df1['iter'], trainAccus[3, :], lw=1.5)
    plt.ylim([0.9, 1.0])
    plt.xlabel('iterate number')
    plt.ylabel('train accuary')
    plt.title('iter vs train accuaray')
    plt.legend(batchSizes, loc='best')
    plt.savefig('image/iter vs train_lr_v1.png', dpi=150)
    '''