import numpy as np
from LoadData import *
import tensorflow as tf
import pandas as pd

# 将weight做初始化
def initWeightVarible(shape):
    initial = tf.truncated_normal(shape, stddev=0.1)
    return tf.Variable(initial)

#将bias做初始化
def initBiasVariable(shape):
    initial = tf.constant(0.1, shape=shape)
    return tf.Variable(initial)

# 进行卷积操作
def conv2d(x, W):
    return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME')

# 采用最大池化
def maxPool(n, x):
    return tf.nn.max_pool(x, ksize=[1, n, n, 1], strides=[1, n, n, 1], padding='SAME')

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

# 由于内存有限，采用分段预测再拼接的方式
def splitBatchPredict(sess, predictionResult, x, testData, keepProb):
    totalTestPrediction = np.array([])
    predictBatchSize = 5000  # 预测时每次batch的大小
    splitNum = len(testData) // predictBatchSize
    for i in range(splitNum):
        testPredictionResult = sess.run(predictionResult, feed_dict={x: testData[i*predictBatchSize:(i+1)*predictBatchSize,:], keepProb: 1.0})
        totalTestPrediction = np.concatenate((totalTestPrediction, testPredictionResult),axis=0)
    if (splitNum*predictBatchSize < len(testData)):
        testPredictionResult = sess.run(predictionResult, feed_dict={x: testData[splitNum*predictBatchSize:len(testData),:], keepProb: 1.0})
        totalTestPrediction = np.concatenate((totalTestPrediction, testPredictionResult), axis=0)
    totalTestPrediction = totalTestPrediction.astype(np.int32)
    return totalTestPrediction

# 计算大规模时的准确率
def calculateAccuracy(sess, accuracy, x, testData, y, testLabels, keepProb):
    predictBatchSize = 5000  # 预测时每次batch的大小
    splitNum = len(testData) // predictBatchSize
    predictCorrectCount = 0
    for i in range(splitNum):
        low = i*predictBatchSize
        high = (i+1)*predictBatchSize
        testPredictionResult = sess.run(accuracy,feed_dict={x: testData[low:high, :], y: testLabels[low:high],
                                                   keepProb: 1.0})
        predictCorrectCount += testPredictionResult*predictBatchSize
    if (splitNum * predictBatchSize < len(testData)):
        low = splitNum*predictBatchSize
        high = len(testData)
        testPredictionResult = sess.run(accuracy, feed_dict={x: testData[low:high, :], y: testLabels[low:high],
                                                             keepProb: 1.0})
        predictCorrectCount += testPredictionResult * (high-low)
    return predictCorrectCount / len(testData)

# 计算大规模时部分样本的准确率,其中，limit为采样上限
def calculateSamplingAccuracy(sess, accuracy, x, testData, y, testLabels, keepProb, limit=1000):
    size = len(testData)  # 总的样本点个数
    indexArray = np.array(range(size), dtype=int)  # 下标数组
    np.random.shuffle(indexArray)
    testSize = min(size, limit) #选取的检测数据个数
    return sess.run(accuracy, feed_dict={x: testData[indexArray[0:testSize], :], y: testLabels[indexArray[0:testSize],:],
                                                             keepProb: 1.0})


if __name__ == '__main__':
    # 导入输入训练集
    trainData, trainLabels = LoadTrainData('train.csv')
    trainLabelsOneHot = oneHotLabels(trainLabels)
    trainData = trainData.astype(np.float32)
    trainData = trainData/255 #归一化
    trainLabelsOneHot = trainLabelsOneHot.astype(np.float32)

    print('train data size:',len(trainLabels))

    x = tf.placeholder(tf.float32, [None, 784]) #输入数据占位符
    xImage = tf.reshape(x, [-1, 28, 28, 1]) #reshape处理


    # 第一个卷积层变量
    WConv1 = initWeightVarible([5, 5, 1, 16]) #卷积核用的是5*5，从1个对应到8个
    bConv1 = initBiasVariable([16])

    # 第一个pooling层
    hConv1 = tf.nn.relu(conv2d(xImage, WConv1) + bConv1) #非线性变换
    hPool1 = maxPool(2, hConv1)

    # 第二个卷积层变量
    WConv2 = initWeightVarible([5, 5, 16, 40]) #卷积核用的是5*5，从8个对应到10个
    bConv2 = initBiasVariable([40])

    # 第二个pooling层
    hConv2 = tf.nn.relu(conv2d(hPool1, WConv2) + bConv2) #非线性变换
    hPool2 = maxPool(2, hConv2)

    # 全连接层
    Wfc1 = initWeightVarible([7 * 7 * 40, 200]) #全连接层
    bfc1 = initBiasVariable([200])
    hPool2Flat = tf.reshape(hPool2, [-1, 7 * 7 * 40]) #将第二个pooling层展开
    hfc1 = tf.nn.relu(tf.matmul(hPool2Flat, Wfc1) + bfc1) #非线性变换

    # 对全连接层进行dropout操作
    keepProb = tf.placeholder(tf.float32) #将keep的概率作为占位符可动态变化
    hfc1Drop = tf.nn.dropout(hfc1, keepProb)

    # 输出层，采用softmax函数
    Wfc2 = initWeightVarible([200, 10])
    bfc2 = initBiasVariable([10])
    yConv = tf.nn.softmax(tf.matmul(hfc1Drop, Wfc2) + bfc2)
    y = tf.placeholder(tf.float32, [None, 10]) #占位符，实际样本标签

    crossEntropy = -tf.reduce_sum(y * tf.log(yConv)) # 计算交叉熵

    trainStep = tf.train.AdamOptimizer(1e-4).minimize(crossEntropy) #采用Adam优化

    correctPrediction = tf.equal(tf.argmax(yConv, axis=1), tf.argmax(y, axis=1)) #生成正确与否的数组，求sum即分类正确的个数
    predictionResult = tf.argmax(yConv, axis=1) #生成预测结果集
    accuracy = tf.reduce_mean(tf.cast(correctPrediction, tf.float32)) #计算平均值即分类准确率，用于模型结果的观测

    init = tf.global_variables_initializer() #变量的初始化

    batchGen = nextBatch(trainData, trainLabelsOneHot, 50) #选取50的batch的生成器
    batchGenitor = batchGen.__iter__()

    with tf.Session() as sess:
        sess.run(init)
        for i in range(20000):
            batchData, batchLabels = batchGenitor.__next__() #生成一个batch
            if (i+1) % 100 == 0:
                trainAccuacy = sess.run(accuracy, feed_dict={x: batchData, y: batchLabels, keepProb: 1.0}) #观测不得影响模型
                print('step #', i+1, ' train accuracy = ', trainAccuacy)
                #yConvs = sess.run(yConv, feed_dict={x: batchData, y: batchLabels, keepProb: 1.0})
                #print(yConvs)
            sess.run(trainStep, feed_dict={x: batchData, y: batchLabels, keepProb: 0.5})

        #trainAccuacy = sess.run(accuracy, feed_dict={x: trainData[0:10000], y:trainLabelsOneHot[0:10000], keepProb:1.0}) #对所有样本的训练准确率
        #print('total train accuracy = ', trainAccuacy)
        #trainPredictionResult = sess.run(predictionResult, feed_dict={x: trainData[0:10000], keepProb: 1.0})
        #print(trainPredictionResult)

        # 导入测试集
        testData = LoadTestData('test.csv')
        print('test data size:', len(testData))

        # 输出预测结果
        testPrediction = splitBatchPredict(sess, predictionResult, x, testData, keepProb)
        print(testPrediction)
        predictFrame = pd.DataFrame(np.transpose([range(1,len(testPrediction)+1), testPrediction]), columns=['ImageId','Label'])
        predictFrame.to_csv('result/CNNv2.csv', sep=',', index=None)



