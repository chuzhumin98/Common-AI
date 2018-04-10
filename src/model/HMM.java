package model;

import java.io.File;
import java.io.FileNotFoundException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;
import java.util.Scanner;

import net.sf.json.JSONObject;

public class HMM {
	public static String eryuanTablePath = "output/eryuantabletotal.txt"; //二元表的位置
	public static String wordPinyinListPath = "data/pinyin-hanzi.txt"; //拼音汉字表
	
	public static String inputPath = "data/input.txt"; //输入文件
	
	public int wordSize;
	public String[] wordList; //词汇表
	public Map<String, Integer> wordIndexList; //词汇倒排表
	public Map<String, ArrayList<Integer>> pinyin; //拼音词汇对照表	
	
	public JSONObject[] eryuanTable; //二元表
	
	public HMM() {
		this.wordIndexList = new HashMap<String, Integer>();
		this.pinyin = new HashMap<String, ArrayList<Integer>>();
	}
	
	/**
	 * 将二元表载入进来
	 */
	public void readTable() {
		try {
			Scanner input = new Scanner(new File(HMM.eryuanTablePath));
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
			Scanner input = new Scanner(new File(HMM.wordPinyinListPath), "gbk");
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
	 * 采用HMM算法测试训练数据
	 */
	public void testModel() {
		try {
			Scanner input = new Scanner(new File(HMM.inputPath));
			while (input.hasNextLine()) {
				String line = input.nextLine();
				if (line.length() > 0) {
					System.out.println(line);
					String[] splits = line.split(" ");
					ArrayList<Integer> pred; //二元模型的前一个
					ArrayList<Integer> succ; //二元模型的后一个
					for (int i = 0; i < splits.length-1; i++) {
						pred = this.pinyin.get(splits[i]);
						succ = this.pinyin.get(splits[i+1]);
					}
				}
			}
		} catch (FileNotFoundException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
	
	public static void main(String[] args) {
		HMM hmm = new HMM();
		hmm.readTable();
		hmm.readPinyin();
		hmm.testModel();
	}
}
