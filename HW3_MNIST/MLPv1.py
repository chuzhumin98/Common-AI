from LoadData import *
import tensorflow as tf
import pandas as pd

# 增加一层
def addLayer(inputs, inSize, outSize, activateFunction=None):
    # 增加一层并返回该层的输出
    Weights = tf.Variable(tf.random_normal([inSize, outSize]))
    biases = tf.Variable(tf.zeros([1, outSize]))
    Wx_plus_b = tf.matmul(inputs, Weights) + biases
    if activateFunction is None:
        outputs = Wx_plus_b
    else:
        outputs = activateFunction(Wx_plus_b)
    return outputs


# 由于内存有限，采用分段预测再拼接的方式
def splitBatchPredict(sess, predictionResult, x, testData):
    totalTestPrediction = np.array([])
    predictBatchSize = 5000  # 预测时每次batch的大小
    splitNum = len(testData) // predictBatchSize
    for i in range(splitNum):
        testPredictionResult = sess.run(predictionResult, feed_dict={x: testData[i*predictBatchSize:(i+1)*predictBatchSize,:]})
        totalTestPrediction = np.concatenate((totalTestPrediction, testPredictionResult),axis=0)
    if (splitNum*predictBatchSize < len(testData)):
        testPredictionResult = sess.run(predictionResult, feed_dict={x: testData[splitNum*predictBatchSize:len(testData),:]})
        totalTestPrediction = np.concatenate((totalTestPrediction, testPredictionResult), axis=0)
    totalTestPrediction = totalTestPrediction.astype(np.int32)
    return totalTestPrediction

if __name__ == '__main__':
    # 导入输入训练集
    trainData, trainLabels = LoadTrainData('train.csv')
    trainLabelsOneHot = oneHotLabels(trainLabels)
    trainData = trainData.astype(np.float32)
    trainData = trainData / 255  # 归一化
    trainLabelsOneHot = trainLabelsOneHot.astype(np.float32)
    print('train data size:', len(trainLabels))

    # 输入的变量们
    x = tf.placeholder(tf.float32, [None, 784])  # 输入数据占位符
    y = tf.placeholder(tf.float32, [None, 10])  # 占位符，实际样本标签

    # 两个隐含层和输出层
    layer1 = addLayer(x, 784, 256, activateFunction=tf.nn.relu)
    layer2 = addLayer(layer1, 256, 256, activateFunction=tf.nn.relu)
    yhat = addLayer(layer2, 256, 10, activateFunction=None)

    # 计算最后一层是softmax层的cross entropy
    crossEntropy = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=yhat, labels=y))

    # 设置优化算法及学习率
    boundaries = [4000, 7000, 10000, 15000, 20000]
    learing_rates = [0.001, 0.0005, 0.0002, 0.0001, 0.00005, 0.00002]
    iterNum = tf.placeholder(tf.int32)
    learing_rate = tf.train.piecewise_constant(iterNum, boundaries=boundaries, values=learing_rates)  # 学习率阶梯状下降
    trainStep = tf.train.AdamOptimizer(learning_rate=learing_rate).minimize(crossEntropy)  # 采用Adam优化

    correctPrediction = tf.equal(tf.argmax(yhat, axis=1), tf.argmax(y, axis=1))  # 生成正确与否的数组，求sum即分类正确的个数
    predictionResult = tf.argmax(yhat, axis=1)  # 生成预测结果集
    accuracy = tf.reduce_mean(tf.cast(correctPrediction, tf.float32))  # 计算平均值即分类准确率，用于模型结果的观测

    init = tf.global_variables_initializer()  # 变量的初始化

    batchGen = nextBatch(trainData, trainLabelsOneHot, 50)  # 选取50的batch的生成器
    batchGenitor = batchGen.__iter__()

    with tf.Session() as sess:
        sess.run(init)
        for i in range(15000):
            batchData, batchLabels = batchGenitor.__next__() #生成一个batch
            if (i+1) % 100 == 0:
                trainAccuacy = sess.run(accuracy, feed_dict={x: batchData, y: batchLabels}) #观测不得影响模型
                print('step #', i+1, ' train accuracy = ', trainAccuacy)
            sess.run(trainStep, feed_dict={x: batchData, y: batchLabels, iterNum:i})

        # 导入测试集
        testData = LoadTestData('test.csv')
        print('test data size:', len(testData))

        # 输出预测结果
        testPrediction = splitBatchPredict(sess, predictionResult, x, testData)
        print(testPrediction)
        predictFrame = pd.DataFrame(np.transpose([range(1,len(testPrediction)+1), testPrediction]), columns=['ImageId','Label'])
        predictFrame.to_csv('result/MLPv2.csv', sep=',', index=None)