package model;

import java.io.File;
import java.io.FileNotFoundException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Scanner;

import net.sf.json.JSONArray;
import net.sf.json.JSONObject;

public class LoadModel {
	public static final String wordListPath = "data/1-2orderhanzi.txt"; //一二级汉字表
	public static final String wordPinyinListPath = "data/pinyin-hanzi.txt"; //拼音汉字表
	public static final String[] datasetName = {"2016-01.txt", "2016-02.txt", "2016-03.txt", "2016-04.txt", "2016-05.txt",
			"2016-06.txt", "2016-07.txt", "2016-08.txt", "2016-09.txt", "2016-10.txt", "2016-11.txt"}; //训练数据集的名字
	public static final String datasetPath = "input/sina_news/"; //训练数据集的路径
	private static LoadModel model;
	
	public ArrayList<Character> wordList; //词汇表
	public Map<Character, Integer> wordIndexList; //词汇倒排表
	public Map<String, ArrayList<Integer>> pinyin; //拼音词汇对照表
	
	public JSONObject[] eryuan; //每个对象是一个JSONObject,它包含键值word,post,count
	
	/**
	 * 构造函数，只能通过getInstance()函数生成实例
	 */
	private LoadModel() {
		this.wordList = new ArrayList<Character>();
		this.pinyin = new HashMap<String, ArrayList<Integer>>();
		this.wordIndexList = new HashMap<Character, Integer>();
		this.loadWordList();
		this.loadPinyin();
		this.eryuan = new JSONObject[this.wordIndexList.size()];
		//进行该JSON对象的初始化
		for (int i = 0; i < this.wordList.size(); i++) {
			ArrayList<Integer> postArray = new ArrayList<Integer>(); //后缀数组
			ArrayList<Integer> postCount = new ArrayList<Integer>(); //对应的计数
			this.eryuan[i] = new JSONObject();
			this.eryuan[i].put("word", this.wordList.get(i));
			this.eryuan[i].put("post", postArray);
			this.eryuan[i].put("count", postCount);
		}
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
			Scanner input = new Scanner(new File(LoadModel.wordPinyinListPath), "gbk");
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
		for (int i = 10; i < 11; i++) {
			try {
				Scanner input = new Scanner(new File(LoadModel.datasetPath+LoadModel.datasetName[i]));
				int count = 0;
				while (input.hasNextLine()) {
					count++;
					if (count % 100 == 0) {
						System.out.println(count);
					}
					JSONObject record = JSONObject.fromObject(input.nextLine());
					String html = (String)record.get("html");
					String title = (String)record.get("title");
					for (int j = 0; j < html.length()-1; ) {
						if (this.wordIndexList.containsKey(html.charAt(j))) {
							if (this.wordIndexList.containsKey(html.charAt(j+1))) {
								int left = this.wordIndexList.get(html.charAt(j));
								int right = this.wordIndexList.get(html.charAt(j+1));
								JSONArray postArray = (JSONArray)this.eryuan[left].get("post");
								JSONArray postCount = (JSONArray)this.eryuan[left].get("count");
								if (!postArray.contains(right)) {
									postArray.add(right);
									postCount.add(1);
									this.eryuan[left].put("post", postArray);
									this.eryuan[left].put("count", postCount);
								} else {
									int index = postArray.indexOf(right);
									int predCount = (int) postCount.get(index);
									postCount.set(index, predCount+1);
									this.eryuan[left].put("count", postCount);
								}
								j++;
							} else {
								j += 2;
							}
						} else {
							j++;
						}
					}
				}
				for (int j = 0; j < 2; j++) {
					System.out.println(this.eryuan[j].toString());
				}
			} catch (FileNotFoundException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		}
	}
	
	public static void main(String[] args) {
		LoadModel model = LoadModel.getInstance();
		model.loadWordList();
		model.loadPinyin();
		model.loadArticles();
	}
}
