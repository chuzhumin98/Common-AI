import numpy as np
from LoadData import LoadData
import tensorflow as tf

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

if __name__ == '__main__':
    # 导入输入训练集
    trainData, trainLabels = LoadData('train.csv')
    trainLabelsOneHot = oneHotLabels(trainLabels)
    trainData = trainData.astype(np.float32)
    trainData = trainData/255
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
    WConv2 = initWeightVarible([5, 5, 16, 32]) #卷积核用的是5*5，从8个对应到10个
    bConv2 = initBiasVariable([32])

    # 第二个pooling层
    hConv2 = tf.nn.relu(conv2d(hPool1, WConv2) + bConv2) #非线性变换
    hPool2 = maxPool(2, hConv2)

    # 全连接层
    Wfc1 = initWeightVarible([7 * 7 * 32, 200]) #全连接层
    bfc1 = initBiasVariable([200])
    hPool2Flat = tf.reshape(hPool2, [-1, 7 * 7 * 32]) #将第二个pooling层展开
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
            sess.run(trainStep, feed_dict={x: batchData, y: batchLabels, keepProb: 0.5})

        trainAccuacy = sess.run(accuracy, feed_dict={x: trainData, y:trainLabels, keepProb:1.0}) #对所有样本的训练准确率
        print('total train accuracy = ', trainAccuacy)

        # 导入测试集
        #testData, testLabels = LoadData('test.csv')
        #print('test data size:', len(testLabels))

        # accuacy on test
        #print('test accuracy = ',sess.run(accuracy,feed_dict={x: mnist.test.images, y: mnist.test.labels, keepProb: 1.0}))

