from LoadData import *
import tensorflow as tf
import pandas as pd
from CNNevaluatev1 import splitDatas
from MLPv1 import *

# 计算大规模时部分样本的准确率,其中，limit为采样上限
def calculateSamplingAccuracy(sess, accuracy, x, testData, y, testLabels, limit=1000):
    size = len(testData)  # 总的样本点个数
    indexArray = np.array(range(size), dtype=int)  # 下标数组
    np.random.shuffle(indexArray)
    testSize = min(size, limit) #选取的检测数据个数
    return sess.run(accuracy, feed_dict={x: testData[indexArray[0:testSize], :], y: testLabels[indexArray[0:testSize],:]
                                                             })

if __name__ == '__main__':
    # 导入输入训练集
    iterList = []  # 迭代次数列表
    trainAccuacyList = []  # 训练集上正确率列表
    validateAccurayList = []  # 验证集上正确率列表

    # 导入输入训练集
    Data, Labels = LoadTrainData('train.csv')
    LabelsOneHot = oneHotLabels(Labels)
    Data = Data.astype(np.float32)
    Data = Data / 255
    LabelsOneHot = LabelsOneHot.astype(np.float32)
    trainData, trainLabels, validateData, validateLabels = splitDatas(Data, LabelsOneHot)
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

    batchGen = nextBatch(trainData, trainLabels, 100)  # 选取50的batch的生成器
    batchGenitor = batchGen.__iter__()

    with tf.Session() as sess:
        sess.run(init)
        for i in range(15001):
            batchData, batchLabels = batchGenitor.__next__() #生成一个batch
            if i % 100 == 0:
                trainAccuacy = calculateSamplingAccuracy(sess, accuracy, x, trainData, y, trainLabels,
                                                         )  # 观测不得影响模型
                print('step #', i, ' train accuracy = ', trainAccuacy)
                validateAccuacy = calculateSamplingAccuracy(sess, accuracy, x, validateData, y, validateLabels,
                                                            )  # 观测不得影响模型
                print('step #', i, ' validate accuracy = ', validateAccuacy)
                iterList.append(i)
                trainAccuacyList.append(trainAccuacy)
                validateAccurayList.append(validateAccuacy)
            sess.run(trainStep, feed_dict={x: batchData, y: batchLabels, iterNum:i})

        accuracyFrame = pd.DataFrame(np.transpose([iterList, trainAccuacyList, validateAccurayList]),
                                     columns=['iter', 'train', 'validate'])
        print(accuracyFrame)
        accuracyFrame.to_csv('evaluate/accuracyVSiter_MLP_4.csv', index=None)