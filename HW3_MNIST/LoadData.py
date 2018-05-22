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