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

# 选取下一个batch，按照batchSize来选取,返回[trainData, trainLabels]大小为batchSize
def nextBatch(trainData, trainLabels, batchSize):
    size = len(trainLabels)
    slices = size // batchSize #一轮的多少
    while True:
        indexArray = np.array(range(size), dtype=int)  # 下标数组
        np.random.shuffle(indexArray) # shuffle一下index
        for i in range(slices):
            low = i * batchSize
            high = (i+1) * batchSize
            yield [trainData[indexArray[low:high],:], trainLabels[indexArray[low:high],:]] # 返回一个batch
