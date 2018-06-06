from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import tensorflow as tf
from LoadData import *
import pandas as pd
from CNNevaluatev1 import splitDatas
from MLPv1 import *

# 由于内存有限，采用分段预测再拼接的方式
def splitBatchPredict(sess, predictionResult, x, testData, keep_prob, batch_size):
    totalTestPrediction = np.array([])
    predictBatchSize = 5000  # 预测时每次batch的大小
    splitNum = len(testData) // predictBatchSize
    for i in range(splitNum):
        testPredictionResult = sess.run(predictionResult, feed_dict={x: testData[i*predictBatchSize:(i+1)*predictBatchSize], keep_prob: 1., batch_size: predictBatchSize})
        totalTestPrediction = np.concatenate((totalTestPrediction, testPredictionResult),axis=0)
    if (splitNum*predictBatchSize < len(testData)):
        testPredictionResult = sess.run(predictionResult, feed_dict={x: testData[splitNum*predictBatchSize:len(testData)], keep_prob: 1., batch_size: len(testData)-splitNum*predictBatchSize})
        totalTestPrediction = np.concatenate((totalTestPrediction, testPredictionResult), axis=0)
    totalTestPrediction = totalTestPrediction.astype(np.int32)
    return totalTestPrediction

# 计算大规模时部分样本的准确率,其中，limit为采样上限
def calculateSamplingAccuracy(sess, accuracy, x, testData, y, testLabels, keep_prob, batch_size, limit=1000):
    size = len(testData)  # 总的样本点个数
    indexArray = np.array(range(size), dtype=int)  # 下标数组
    np.random.shuffle(indexArray)
    testSize = min(size, limit) #选取的检测数据个数
    return sess.run(accuracy, feed_dict={x: testData[indexArray[0:testSize]], y: testLabels[indexArray[0:testSize]],
                    keep_prob: 1., batch_size: testSize})

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

    # 定义网络超参数
    learning_rate = 0.001
    training_iters = 5001
    batch_size = tf.placeholder(tf.int32, [])
    display_step = 100

    # 定义网络参数
    n_inputs = 28  # 输入的维度
    n_steps = 28  # 时间长度
    n_hidden_units = 128  # 隐藏层的神经元个数
    n_classes = 10  # 输出的数量，也就分类数量，0-9

    # 占位符输入
    x = tf.placeholder(tf.float32, [None, n_steps, n_inputs])
    y = tf.placeholder(tf.float32, [None, n_classes])
    keep_prob = tf.placeholder(tf.float32)

    weights = {'in': tf.Variable(tf.random_normal([n_inputs, n_hidden_units])),
               'out': tf.Variable(tf.random_normal([n_hidden_units, n_classes]))}

    biases = {'in': tf.Variable(tf.constant(0.1, shape=[n_hidden_units, ])),
              'out': tf.Variable(tf.constant(0.1, shape=[n_classes, ]))}

    # 构建RNN模型
    X = tf.reshape(x, [-1, n_inputs])  # 这是为了向量化处理整合在了一起
    X_in = tf.matmul(X, weights['in']) + biases['in']
    X_in = tf.reshape(X_in, [-1, n_steps, n_hidden_units])
    # 使用基本的LSTM循环网络单元
    lstm_cell = tf.contrib.rnn.BasicLSTMCell(n_hidden_units, forget_bias=1.0, state_is_tuple=True)
    # 初始化为0，LSTM单元由两部分构成(c_state, h_state)
    init_state = lstm_cell.zero_state(batch_size, dtype=tf.float32)
    # dynamic_rnn接收张量要么为(batch, steps, inputs)或者(steps, batch, inputs)作为X_in
    outputs, final_state = tf.nn.dynamic_rnn(lstm_cell, X_in, initial_state=init_state, time_major=False)

    pred = tf.matmul(final_state[-1], weights['out']) + biases['out']

    # 定义损失函数和学习步骤
    cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=pred, labels=y))
    optimizer = tf.train.AdamOptimizer(learning_rate).minimize(cost)

    # 测试网络
    correct_pred = tf.equal(tf.argmax(pred, 1), tf.argmax(y, 1))
    predictionResult = tf.argmax(pred, axis=1)  # 生成预测结果集
    accuracy = tf.reduce_mean(tf.cast(correct_pred, tf.float32))

    batchGen = nextBatch(trainData, trainLabels, 50)  # 选取50的batch的生成器
    batchGenitor = batchGen.__iter__()

    # 初始化所有的共享变量
    init = tf.global_variables_initializer()
    trainData_1 = trainData.reshape([-1, n_steps, n_inputs])
    validateData_1 = validateData.reshape([-1, n_steps, n_inputs])

    # 开启一个训练
    with tf.Session() as sess:
        sess.run(init)
        step = 0
        batch_size0 = 50
        # Keep training until reach max iterations
        for i in range(training_iters):
            batch_xs, batch_ys = batchGenitor.__next__()
            batch_xs = batch_xs.reshape([batch_size0, n_steps, n_inputs])
            # 获取批数据
            sess.run(optimizer, feed_dict={x: batch_xs, y: batch_ys, batch_size: batch_size0})
            if i % display_step == 0:
                trainAccuacy = calculateSamplingAccuracy(sess, accuracy, x, trainData_1, y, trainLabels,
                                                         keep_prob, batch_size)  # 观测不得影响模型
                print('step #', i, ' train accuracy = ', trainAccuacy)
                validateAccuacy = calculateSamplingAccuracy(sess, accuracy, x, validateData_1, y, validateLabels,
                                                            keep_prob, batch_size)  # 观测不得影响模型
                print('step #', i, ' validate accuracy = ', validateAccuacy)
                iterList.append(i)
                trainAccuacyList.append(trainAccuacy)
                validateAccurayList.append(validateAccuacy)

        accuracyFrame = pd.DataFrame(np.transpose([iterList, trainAccuacyList, validateAccurayList]),
                                     columns=['iter', 'train', 'validate'])
        print(accuracyFrame)
        accuracyFrame.to_csv('evaluate/accuracyVSiter_RNN_2.csv', index=None)