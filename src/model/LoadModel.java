package model;

import java.io.File;
import java.io.FileNotFoundException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Scanner;

public class LoadModel {
	public static final String wordListPath = "data/1-2orderhanzi.txt"; //一二级汉字表
	public static final String wordPinyinListPath = "data/pinyin-hanzi.txt"; //拼音汉字表
	public static final String[] datasetName = {"2016-01.txt", "2016-02.txt", "2016-03.txt", "2016-04.txt", "2016-05.txt",
			"2016-06.txt", "2016-07.txt", "2016-08.txt", "2016-09.txt", "2016-10.txt", "2016-11.txt"}; //训练数据集的名字
	public static final String datasetPath = "input/sina_news/"; //训练数据集的路径
	private static LoadModel model;
	
	public ArrayList<Character> wordList; //词汇表
	public Map<String, ArrayList<Integer>> pinyin; //拼音词汇对照表
	
	/**
	 * 构造函数，只能通过getInstance()函数生成实例
	 */
	private LoadModel() {
		this.wordList = new ArrayList<Character>();
		this.pinyin = new HashMap<String, ArrayList<Integer>>();
	}
	
	public static LoadModel getInstance() {
		if (model == null) {
			model = new LoadModel();
		}
		return model;
	}
	
	/**
	 * 将词库导入进来
	 */
	public void loadWordList() {
		try {
			Scanner input = new Scanner(new File(LoadModel.wordListPath), "gbk");
			String words = input.nextLine();
			for (int i = 0; i < words.length(); i++) {
				this.wordList.add(words.charAt(i));
			}
			System.out.println("load all the useful words number: "+this.wordList.size());
			input.close();
		} catch (FileNotFoundException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}		
	}
	
	/**
	 * 将拼音汉字对照表导入，仅利用在wordlist中出现的词
	 */
	public void loadPinyin() {
		try {
			Scanner input = new Scanner(new File(LoadModel.wordPinyinListPath), "gbk");
			int countTerm = 0; //不同term的个数
			while (input.hasNextLine()) {
				String line = input.nextLine();
				if (line.length() == 0) continue;
				String[] splits = line.split(" ");
				ArrayList<Integer> words = new ArrayList<Integer>();
				for (int i = 1; i < splits.length; i++) {
					char thisWord = splits[i].charAt(0);
					if (this.wordList.contains(thisWord)) {
						words.add(this.wordList.indexOf(thisWord));
					}
				}
				countTerm += words.size();
				this.pinyin.put(splits[0], words);
			}
			System.out.println("different pinyin number："+this.pinyin.size());
			System.out.println("different terms number："+countTerm);
			/* for (Entry<String, ArrayList<Integer>> item: this.pinyin.entrySet()) {
				System.out.print(item.getKey()+": ");
				ArrayList<Integer> words = item.getValue();
				for (int i = 0; i < words.size(); i++) {
					System.out.print(this.wordList.get(words.get(i))+" ");
				}
				System.out.println();
			} */
			input.close();
		} catch (FileNotFoundException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
	
	public static void main(String[] args) {
		LoadModel model = LoadModel.getInstance();
		model.loadWordList();
		model.loadPinyin();
	}
}
