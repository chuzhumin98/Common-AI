import numpy as np
from LoadData import LoadTrainData
from LoadData import LoadTestData
import tensorflow as tf
import pandas as pd
from CNNv1 import *

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

    crossEntropy = -tf.reduce_sum(y * tf.log(yConv+1e-10)) # 计算交叉熵

    # 设置优化算法及学习率
    boundaries = [1000, 2500, 4500, 6000, 8000]
    learing_rates = [0.001, 0.0005, 0.0002, 0.0001, 0.00005, 0.00002]
    iterNum = tf.placeholder(tf.int32)
    learing_rate = tf.train.piecewise_constant(iterNum, boundaries=boundaries, values=learing_rates)  # 学习率阶梯状下降
    trainStep = tf.train.AdamOptimizer(learning_rate=learing_rate).minimize(crossEntropy)  # 采用Adam优化

    correctPrediction = tf.equal(tf.argmax(yConv, axis=1), tf.argmax(y, axis=1)) #生成正确与否的数组，求sum即分类正确的个数
    predictionResult = tf.argmax(yConv, axis=1) #生成预测结果集
    accuracy = tf.reduce_mean(tf.cast(correctPrediction, tf.float32)) #计算平均值即分类准确率，用于模型结果的观测

    init = tf.global_variables_initializer() #变量的初始化

    batchGen = nextBatch(trainData, trainLabelsOneHot, 50) #选取50的batch的生成器
    batchGenitor = batchGen.__iter__()

    with tf.Session() as sess:
        sess.run(init)
        for i in range(10000):
            batchData, batchLabels = batchGenitor.__next__() #生成一个batch
            if (i+1) % 100 == 0:
                trainAccuacy = sess.run(accuracy, feed_dict={x: batchData, y: batchLabels, keepProb: 1.0}) #观测不得影响模型
                print('step #', i+1, ' train accuracy = ', trainAccuacy)
                #yConvs = sess.run(yConv, feed_dict={x: batchData, y: batchLabels, keepProb: 1.0})
                #print(yConvs)
            sess.run(trainStep, feed_dict={x: batchData, y: batchLabels, keepProb: 0.5, iterNum: i})

        #trainAccuacy = sess.run(accuracy, feed_dict={x: trainData[0:10000], y:trainLabelsOneHot[0:10000], keepProb:1.0}) #对所有样本的训练准确率
        #print('total train accuracy = ', trainAccuacy)
        #trainPredictionResult = sess.run(predictionResult, feed_dict={x: trainData[0:10000], keepProb: 1.0})
        #print(trainPredictionResult)

        # 导入测试集
        testData = LoadTestData('test.csv')
        testData = testData / 255
        print('test data size:', len(testData))

        # 输出预测结果
        testPrediction = splitBatchPredict(sess, predictionResult, x, testData, keepProb)
        print(testPrediction)
        predictFrame = pd.DataFrame(np.transpose([range(1,len(testPrediction)+1), testPrediction]), columns=['ImageId','Label'])
        predictFrame.to_csv('result/CNNv2_1.csv', sep=',', index=None)



