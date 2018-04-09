package model;

import java.io.File;
import java.io.FileNotFoundException;
import java.util.ArrayList;
import java.util.Scanner;

public class LoadModel {
	public static final String wordListPath = "data/1-2orderhanzi.txt"; //一二级汉字表
	public static final String wordPinyinListPath = "data/pinyin-hanzi.txt"; //拼音汉字表
	public static final String[] datasetName = {"2016-01.txt", "2016-02.txt", "2016-03.txt", "2016-04.txt", "2016-05.txt",
			"2016-06.txt", "2016-07.txt", "2016-08.txt", "2016-09.txt", "2016-10.txt", "2016-11.txt"}; //训练数据集的名字
	public static final String datasetPath = "input/sina_news/"; //训练数据集的路径
	private static LoadModel model;
	
	public ArrayList<String> wordList; //词汇表
	public ArrayList<ArrayList<Integer>> pinyin; //拼音词汇对照表
	
	/**
	 * 构造函数，只能通过getInstance()函数生成实例
	 */
	private LoadModel() {
		this.wordList = new ArrayList<String>();
		this.pinyin = new ArrayList<ArrayList<Integer>>();
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
			System.out.println("load all the useful words number: "+words.length());
			input.close();
		} catch (FileNotFoundException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
	}
	
	public static void main(String[] args) {
		LoadModel model = LoadModel.getInstance();
		model.loadWordList();
	}
}
