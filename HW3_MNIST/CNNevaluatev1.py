from CNNv1 import *

#随机划分训练集和验证集
#    参数samples：所有样本数据
#    参数samplesLabels：样本所对应的标签
#    return：[训练集数据, 训练集标签, 验证集数据, 验证集标签]
def splitDatas(samples, samplesLabels):
    size = len(samplesLabels) #总的样本点个数
    indexArray = np.array(range(size), dtype=int) #下标数组
    np.random.shuffle(indexArray)
    #size = size // 10 #仅挑1/10进行研究
    validateStart = size * 4 // 5 #按照4:1的比例划分划分训练集和验证集
    trainData = samples[indexArray[0:validateStart]]
    trainLabel = samplesLabels[indexArray[0:validateStart]]
    validateData = samples[indexArray[validateStart:size]]
    validateLabel = samplesLabels[indexArray[validateStart:size]]
    return [trainData, trainLabel, validateData, validateLabel]

if __name__ == '__main__':
    iterList = [] #迭代次数列表
    trainAccuacyList = [] #训练集上正确率列表
    validateAccurayList = [] #验证集上正确率列表

    # 导入输入训练集
    Data, Labels = LoadTrainData('train.csv')
    LabelsOneHot = oneHotLabels(Labels)
    Data = Data.astype(np.float32)
    Data = Data / 255
    LabelsOneHot = LabelsOneHot.astype(np.float32)
    trainData, trainLabels, validateData, validateLabels = splitDatas(Data, LabelsOneHot)

    print('train data size:', len(trainLabels))

    x = tf.placeholder(tf.float32, [None, 784])  # 输入数据占位符
    xImage = tf.reshape(x, [-1, 28, 28, 1])  # reshape处理

    # 第一个卷积层变量
    WConv1 = initWeightVarible([5, 5, 1, 16])  # 卷积核用的是5*5，从1个对应到8个
    bConv1 = initBiasVariable([16])

    # 第一个pooling层
    hConv1 = tf.nn.relu(conv2d(xImage, WConv1) + bConv1)  # 非线性变换
    hPool1 = maxPool(2, hConv1)

    # 第二个卷积层变量
    WConv2 = initWeightVarible([5, 5, 16, 40])  # 卷积核用的是5*5，从8个对应到10个
    bConv2 = initBiasVariable([40])

    # 第二个pooling层
    hConv2 = tf.nn.relu(conv2d(hPool1, WConv2) + bConv2)  # 非线性变换
    hPool2 = maxPool(2, hConv2)

    # 全连接层
    Wfc1 = initWeightVarible([7 * 7 * 40, 200])  # 全连接层
    bfc1 = initBiasVariable([200])
    hPool2Flat = tf.reshape(hPool2, [-1, 7 * 7 * 40])  # 将第二个pooling层展开
    hfc1 = tf.nn.relu(tf.matmul(hPool2Flat, Wfc1) + bfc1)  # 非线性变换

    # 对全连接层进行dropout操作
    keepProb = tf.placeholder(tf.float32)  # 将keep的概率作为占位符可动态变化
    hfc1Drop = tf.nn.dropout(hfc1, keepProb)

    # 输出层，采用softmax函数
    Wfc2 = initWeightVarible([200, 10])
    bfc2 = initBiasVariable([10])
    yConv = tf.nn.softmax(tf.matmul(hfc1Drop, Wfc2) + bfc2)
    y = tf.placeholder(tf.float32, [None, 10])  # 占位符，实际样本标签

    crossEntropy = -tf.reduce_sum(y * tf.log(yConv))  # 计算交叉熵

    trainStep = tf.train.AdamOptimizer(1e-4).minimize(crossEntropy)  # 采用Adam优化

    correctPrediction = tf.equal(tf.argmax(yConv, axis=1), tf.argmax(y, axis=1))  # 生成正确与否的数组，求sum即分类正确的个数
    predictionResult = tf.argmax(yConv, axis=1)  # 生成预测结果集
    accuracy = tf.reduce_mean(tf.cast(correctPrediction, tf.float32))  # 计算平均值即分类准确率，用于模型结果的观测

    init = tf.global_variables_initializer()  # 变量的初始化

    batchGen = nextBatch(trainData, trainLabels, 50)  # 选取50的batch的生成器
    batchGenitor = batchGen.__iter__()

    with tf.Session() as sess:
        sess.run(init)
        for i in range(201):
            batchData, batchLabels = batchGenitor.__next__()  # 生成一个batch
            if i % 100 == 0:
                trainAccuacy = calculateSamplingAccuracy(sess, accuracy, x, trainData, y, trainLabels, keepProb)  # 观测不得影响模型
                print('step #', i, ' train accuracy = ', trainAccuacy)
                validateAccuacy = calculateSamplingAccuracy(sess, accuracy, x, validateData, y, validateLabels, keepProb)  # 观测不得影响模型
                print('step #', i, ' validate accuracy = ', validateAccuacy)
                iterList.append(i)
                trainAccuacyList.append(trainAccuacy)
                validateAccurayList.append(validateAccuacy)
                # yConvs = sess.run(yConv, feed_dict={x: batchData, y: batchLabels, keepProb: 1.0})
                # print(yConvs)
            sess.run(trainStep, feed_dict={x: batchData, y: batchLabels, keepProb: 0.5})

        accuracyFrame = pd.DataFrame(np.transpose([iterList, trainAccuacyList, validateAccurayList]), columns=['iter','train','validate'])
        print(accuracyFrame)
        accuracyFrame.to_csv('evaluate/accuracyVSiter_CNN.csv',index=None)