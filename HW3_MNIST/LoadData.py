import numpy as np

# 导入训练集
def LoadTrainData(path):
    trainData = np.loadtxt(open(path, 'r'), delimiter=',', skiprows=1, dtype=np.int)
    trainLabels = trainData[:, 0]
    trainData = trainData[:, 1:785]  # N*784
    print(trainData)
    return [trainData, trainLabels]

# 导入测试集
def LoadTestData(path):
    testData = np.loadtxt(open(path, 'r'), delimiter=',', skiprows=1, dtype=np.int)
    return testData[:,:784]

# 对样本标签进行one hot化
def oneHotLabels(labels):
    size = len(labels) #样本点的个数
    labelsOneHot = np.zeros([size, 10])
    for i in range(10):
        labelsOneHot[labels[:] == i,i] = 1
    print(labelsOneHot)
    return labelsOneHot