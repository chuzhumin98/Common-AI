package model;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.PrintStream;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Scanner;

import net.sf.json.JSONArray;
import net.sf.json.JSONObject;

public class ExportModel {
	public static String wordListPath = "data/1-2orderhanzi.txt"; //一二级汉字表
	public static String wordPinyinListPath = "data/pinyin-hanzi.txt"; //拼音汉字表
	public static String[] datasetName = {"2016-01.txt", "2016-02.txt", "2016-03.txt", "2016-04.txt", "2016-05.txt",
			"2016-06.txt", "2016-07.txt", "2016-08.txt", "2016-09.txt", "2016-10.txt", "2016-11.txt"}; //训练数据集的名字
	public static String datasetPath = "input/sina_news/"; //训练数据集的路径
	private static ExportModel model;
	
	public ArrayList<Character> wordList; //词汇表
	public Map<Character, Integer> wordIndexList; //词汇倒排表
	public Map<String, ArrayList<Integer>> pinyin; //拼音词汇对照表
	
	public int[][] transferMatrix; //转移矩阵
	
	/**
	 * 构造函数，只能通过getInstance()函数生成实例
	 */
	private ExportModel() {
		this.wordList = new ArrayList<Character>();
		this.pinyin = new HashMap<String, ArrayList<Integer>>();
		this.wordIndexList = new HashMap<Character, Integer>();
		this.loadWordList();
		this.loadPinyin();
	}
	
	public static ExportModel getInstance() {
		if (model == null) {
			model = new ExportModel();
		}
		return model;
	}
	
	/**
	 * 将词库导入进来
	 */
	public void loadWordList() {
		try {
			Scanner input = new Scanner(new File(ExportModel.wordListPath), "gbk");
			String words = input.nextLine();
			for (int i = 0; i < words.length(); i++) {
				this.wordList.add(words.charAt(i));
				this.wordIndexList.put(words.charAt(i), i);
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
			Scanner input = new Scanner(new File(ExportModel.wordPinyinListPath), "gbk");
			int countTerm = 0; //不同term的个数
			while (input.hasNextLine()) {
				String line = input.nextLine();
				if (line.length() == 0) continue;
				String[] splits = line.split(" ");
				ArrayList<Integer> words = new ArrayList<Integer>();
				for (int i = 1; i < splits.length; i++) {
					char thisWord = splits[i].charAt(0);
					if (this.wordIndexList.containsKey(thisWord)) {
						words.add(this.wordIndexList.get(thisWord));
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
	
	/**
	 * 载入文章的数据
	 */
	public void loadArticles() {
		this.transferMatrix = new int [this.wordIndexList.size()][this.wordIndexList.size()];
		for (int i = 0; i < this.datasetName.length; i++) {
			try {
				Scanner input = new Scanner(new File(ExportModel.datasetPath+ExportModel.datasetName[i]));
				while (input.hasNextLine()) {
					JSONObject record = JSONObject.fromObject(input.nextLine());
					String html = (String)record.get("html");
					String title = (String)record.get("title");
					for (int j = 0; j < html.length()-1; ) {
						if (this.wordIndexList.containsKey(html.charAt(j))) {
							if (this.wordIndexList.containsKey(html.charAt(j+1))) {
								int left = this.wordIndexList.get(html.charAt(j));
								int right = this.wordIndexList.get(html.charAt(j+1));
								this.transferMatrix[left][right]++;
								j++;
							} else {
								j += 2;
							}
						} else {
							j++;
						}
					}
				}
				System.out.println("end for read "+ExportModel.datasetName[i]);
			} catch (FileNotFoundException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		}
	}
	
	public void exportEryuanTable() {
		try {
			PrintStream output = new PrintStream("output/eryuantabletotal.txt");
			output.println(this.wordIndexList.size());
			for (int i = 0; i < this.transferMatrix.length; i++) {
				JSONObject wordInfo = new JSONObject();
				wordInfo.put("w", this.wordList.get(i)); //word
				JSONArray postArray = new JSONArray(); 
				JSONArray postCount = new JSONArray();
				int countPred = 0; //计数总的以此为前缀的个数
				for (int j = 0; j < this.transferMatrix[i].length; j++) {
					if (this.transferMatrix[i][j] > 0) {
						postArray.add(j);
						postCount.add(this.transferMatrix[i][j]);
						countPred += this.transferMatrix[i][j];
					}
				}
				wordInfo.put("a", postArray); //postarray
				wordInfo.put("c", postCount); //postcount
				wordInfo.put("t", countPred); //total count
				output.println(wordInfo.toString());
			}
		} catch (FileNotFoundException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
	
	public static void main(String[] args) {
		ExportModel model = ExportModel.getInstance();
		model.loadArticles();
		model.exportEryuanTable();
	}
}
