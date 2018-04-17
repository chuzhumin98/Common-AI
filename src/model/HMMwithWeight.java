package model;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.PrintStream;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;
import java.util.Scanner;

import net.sf.json.JSONArray;
import net.sf.json.JSONObject;

public class HMMwithWeight {
	public static String eryuanTablePath = "output/eryuantabletotal_2.txt"; //二元表的位置
	public static String wordPinyinListPath = "data/pinyin-hanzi.txt"; //拼音汉字表
	public static String pinyinTablePath = "output/pinyintabletotal_IKC.txt"; //拼音转换表
	
	public static String inputPath = "data/input.txt"; //输入文件
	public static String outputPath = "data/output4.txt"; //输出文件
	
	public int wordSize;
	public String[] wordList; //词汇表
	public Map<String, Integer> wordIndexList; //词汇倒排表
	
	public Map<String, ArrayList<Integer>> pinyin; //拼音词汇对照表	
	public Map<String, Integer> pinyinIndex; //拼音的索引值
	
	public JSONObject[] eryuanTable; //二元表
	public int[][] pinyinTable; //拼音二元表
	
	public HMMwithWeight() {
		this.wordIndexList = new HashMap<String, Integer>();
		this.pinyin = new HashMap<String, ArrayList<Integer>>();
		this.pinyinIndex = new HashMap<String, Integer>();
	}
	
	/**
	 * 将二元表载入进来
	 */
	public void readTable() {
		try {
			Scanner input = new Scanner(new File(HMMwithWeight.eryuanTablePath),"utf-8");
			this.wordSize = Integer.valueOf(input.nextLine());
			System.out.println("word size:"+wordSize);
			this.eryuanTable = new JSONObject [wordSize];
			this.wordList = new String [this.wordSize];
			for (int i = 0; i < wordSize; i++) {
				this.eryuanTable[i] = JSONObject.fromObject(input.nextLine());
			}
			System.out.println("complete load eryuan table.");
			for (int i = 0; i < this.wordSize; i++) {
				String word = (String) this.eryuanTable[i].get("w");
				this.wordIndexList.put(word, i);
				this.wordList[i] = word;
			}
			System.out.println("compete load wordlist.");
		} catch (FileNotFoundException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}	
	}
	
	/**
	 * 将拼音汉字对照表导入，仅利用在wordlist中出现的词
	 */
	public void readPinyin() {
		try {
			Scanner input = new Scanner(new File(HMMwithWeight.wordPinyinListPath), "gbk");
			int countTerm = 0; //不同term的个数
			while (input.hasNextLine()) {
				String line = input.nextLine();
				if (line.length() == 0) continue;
				String[] splits = line.split(" ");
				ArrayList<Integer> words = new ArrayList<Integer>();
				for (int i = 1; i < splits.length; i++) {
					String thisWord = splits[i];
					if (this.wordIndexList.containsKey(thisWord)) {
						words.add(this.wordIndexList.get(thisWord));
					}
				}
				countTerm += words.size();
				this.pinyin.put(splits[0], words);
				int myIndex = this.pinyinIndex.size();
				this.pinyinIndex.put(splits[0], myIndex);
			}
			System.out.println("different pinyin size："+this.pinyin.size());
			System.out.println("different terms size："+countTerm);
			input.close();
		} catch (FileNotFoundException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
	
	/**
	 * 将拼音二元表读入
	 */
	public void readPinyinTable() {
		try {
			Scanner input = new Scanner(new File(HMMwithWeight.pinyinTablePath), "gbk");
			int pinyinSize = input.nextInt();
			this.pinyinTable = new int [pinyinSize][pinyinSize];
			for (int i = 0; i < pinyinSize; i++) {
				for (int j = 0; j < pinyinSize; j++) {
					this.pinyinTable[i][j] = input.nextInt();
				}
			}
			input.close();
		} catch (FileNotFoundException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
	}
	
	/**
	 * 采用HMM算法测试训练数据
	 */
	public void testModel() {
		try {
			Scanner input = new Scanner(new File(HMMwithWeight.inputPath));
			PrintStream output = new PrintStream(new File(HMMwithWeight.outputPath));
			while (input.hasNextLine()) {
				String line = input.nextLine();
				if (line.length() > 0) {
					System.out.println(line);
					String[] splits = line.split(" ");
					ArrayList<Integer> pred; //二元模型的前一个
					ArrayList<Integer> succ; //二元模型的后一个
					ArrayList<Double> predProb = new ArrayList<Double>(); //到达前一个时的log概率
					ArrayList<Double> succProb = new ArrayList<Double>(); //到达后一个时的log概率
					int[][] predPoint = new int [splits.length][this.wordSize]; //记录上一个最优的位置
					for (int i = 0; i < splits.length-1; i++) {
						pred = this.pinyin.get(splits[i]);
						succ = this.pinyin.get(splits[i+1]);
						int predIndex = this.pinyinIndex.get(splits[i]);
						int succIndex = this.pinyinIndex.get(splits[i+1]);
						double eta = Math.min(Math.log(this.pinyinTable[predIndex][succIndex]+1)/Math.log(3), 14); //设置这一组词项变化的权重
						double w = 0.85 + eta * 0.01; //分配给转换关系的权重，另一部分为词频信息
						if (i == 0) { //在初始位置时需要初始化predProb信息
							predProb.clear();
							for (int j = 0; j < pred.size(); j++) {
								double countPred = this.eryuanTable[pred.get(j)].getDouble("t");
								double logProb = Math.log(countPred+1.0/pred.size()); //平滑后的log概率
								predProb.add(logProb);
							}
						}
						double[][] totalProb = new double [pred.size()][succ.size()]; //计算各对这对的概率
						Double totalSuccCount = 0.0; //P(w_i)的分母部分
						for (int k = 0; k < succ.size(); k++) {
							totalSuccCount += this.eryuanTable[succ.get(k)].getDouble("pt");
						}
						//计算每一对之间的概率变化
						for (int j = 0; j < pred.size(); j++) {
							double countPred = this.eryuanTable[pred.get(j)].getDouble("t");
							JSONArray postArray = (JSONArray) this.eryuanTable[pred.get(j)].get("a");
							JSONArray postCount = (JSONArray) this.eryuanTable[pred.get(j)].get("c");
							for (int k = 0; k < succ.size(); k++) {
								double countSucc = this.eryuanTable[succ.get(k)].getDouble("pt");
								if (postArray.contains(succ.get(k))) {
									//System.out.println(this.wordList[pred.get(j)]+"-"+this.wordList[succ.get(k)]);
									int index = postArray.indexOf(succ.get(k)); //对应的词汇组合的下标
									double thisCount = postCount.getDouble(index); //获取该对词汇出现的次数
									double logProb = Math.log((thisCount+1.0/pred.size())
											/(countPred+1))*w + Math.log((countSucc+1.0)/totalSuccCount)*(1-w);
									totalProb[j][k] = logProb + predProb.get(j);
								} else {
									double logProb = Math.log((1.0/pred.size())/(countPred+1))
											*w + Math.log((countSucc+1.0)/totalSuccCount)*(1-w);
									totalProb[j][k] = logProb + predProb.get(j);
								}
							}
						}
						//找出最大概率项，进行动态规划
						succProb.clear();
						for (int k = 0; k < succ.size(); k++) {
							int indexMax = 0; //最大概率的索引
							for (int j = 1; j < pred.size(); j++) {
								if (totalProb[j][k] > totalProb[indexMax][k]) {
									indexMax = j;
								}
							}
							predPoint[i+1][succ.get(k)] = pred.get(indexMax); //记录前缀节点
							succProb.add(totalProb[indexMax][k]);
							//System.out.println(this.wordList[pred.get(indexMax)]+"-"+this.wordList[succ.get(k)]);
						}
						//进入新的一层循环时将succProb的数据拷贝至predProb中
						predProb = succProb;
						succProb = new ArrayList<Double>();
					}
					ArrayList<Integer> finishIndex = this.pinyin.get(splits[splits.length-1]);
					int totalMaxIndex = 0; //概率最大时对应的下标
					for (int i = 1; i < finishIndex.size(); i++) {
						if (predProb.get(i) > predProb.get(totalMaxIndex)) {
							totalMaxIndex = i;
						}
					}
					int newIndex = finishIndex.get(totalMaxIndex); //记录当前的最优字符下标（往前推）
					String maxProbString = this.wordList[newIndex]; //最大概率字符串		
					for (int i = splits.length-1; i > 0; i--) {
						newIndex = predPoint[i][newIndex];
						maxProbString = this.wordList[newIndex] + maxProbString;
					}
					System.out.println(maxProbString);
					output.println(maxProbString);
				}
			}
		} catch (FileNotFoundException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
	
	/**
	 * xxx.jar (-拼音汉字对应表  -二元矩阵表   -二元拼音表   -输入文件  -输出文件)
	 * 
	 * @param args
	 */
	public static void main(String[] args) {
		System.out.println("this is HMMwithWeight.java");
		HMMwithWeight hmm = new HMMwithWeight();
		if (args.length >= 1) {
			HMMwithWeight.wordPinyinListPath = args[0];
		}
		if (args.length >= 2) {
			HMMwithWeight.eryuanTablePath = args[1];
		}
		if (args.length >= 3) {
			HMMwithWeight.pinyinTablePath = args[2];
		}
		if (args.length >= 4) {
			HMMwithWeight.inputPath = args[3];
		}
		if (args.length >= 5) {
			HMMwithWeight.outputPath = args[4];
		}
		hmm.readTable();
		hmm.readPinyin();
		hmm.readPinyinTable();
		hmm.testModel();
	}
}
