package com.mindflow.py4j;

import java.util.concurrent.Callable;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/**
 * ${DESCRIPTION}
 *
 * @author Ricky Fung
 * @create 2017-02-16 23:57
 */
public class ThreadSafeTest {

    public static void main(String[] args) {

        final String[] arr = {"大夫", "重庆银行", "长沙银行", "便宜坊", "西藏", "藏宝图", "出差", "参加", "列车长"
        		,"绿帽子","一撙酒","苟利国家生死以,岂因祸福避趋之.或许你以为只是这样吗？那你就真的太过于Naive了，哈哈哈哈哈，不要想了"
        				+ "c++123"};
        final Converter converter = new PinyinConverter();

        int threadNum = 1;
        ExecutorService pool = Executors.newFixedThreadPool(threadNum);
        for(int i=0;i<threadNum;i++){
            pool.submit(new Callable<Void>() {
                @Override
                public Void call() throws Exception {

                    System.out.println("thread "+Thread.currentThread().getName()+" start");
                    for(int i=0;i<arr.length;i++){
                        System.out.println(converter.getPinyin(arr[i%arr.length]));
                    }
                    System.out.println("thread "+Thread.currentThread().getName()+" over");
                    return null;
                }
            });
        }

        pool.shutdown();
    }
}
