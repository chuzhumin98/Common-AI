from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import tensorflow as tf
from LoadData import *
import pandas as pd

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

if __name__ == '__main__':
    # 导入输入训练集
    trainData, trainLabels = LoadTrainData('train.csv')
    trainLabelsOneHot = oneHotLabels(trainLabels)
    trainData = trainData.astype(np.float32)
    trainData = trainData/255 #归一化
    trainLabelsOneHot = trainLabelsOneHot.astype(np.float32)

    print('train data size:',len(trainLabels))

    # 定义网络超参数
    learning_rate = 0.001
    training_iters = 5000
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

    batchGen = nextBatch(trainData, trainLabelsOneHot, 50)  # 选取50的batch的生成器
    batchGenitor = batchGen.__iter__()

    # 初始化所有的共享变量
    init = tf.global_variables_initializer()

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
            if (i+1) % display_step == 0:
                # 计算精度
                trainAccuracy = sess.run(accuracy, feed_dict={x: batch_xs, y: batch_ys, keep_prob: 1., batch_size: batch_size0})
                print('step #', i+1, ' train accuracy = ', trainAccuracy)

        # 导入测试集
        testData = LoadTestData('test.csv')
        testData = testData / 255 #归一化
        testData = testData.reshape([-1, n_steps, n_inputs])
        print('test data size:', len(testData))

        # 输出预测结果
        testPrediction = splitBatchPredict(sess, predictionResult, x, testData, keep_prob, batch_size)
        print(testPrediction)
        predictFrame = pd.DataFrame(np.transpose([range(1, len(testPrediction) + 1), testPrediction]),
                                    columns=['ImageId', 'Label'])
        predictFrame.to_csv('result/RNNv5.csv', sep=',', index=None)

