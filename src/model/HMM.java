package model;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

public class HMM {
	public static String eryuanTablePath = "output/eryuantabletotal.txt"; //二元表的位置
	public static String wordPinyinListPath = "data/pinyin-hanzi.txt"; //拼音汉字表
	
	public char[] wordList; //词汇表
	public Map<Character, Integer> wordIndexList; //词汇倒排表
	public Map<String, ArrayList<Integer>> pinyin; //拼音词汇对照表	
	
	public HMM() {
		this.wordIndexList = new HashMap<Character, Integer>();
		this.pinyin = new HashMap<String, ArrayList<Integer>>();
	}
	
	/**
	 * 将模型载入进来
	 */
	public void ReadModel() {
		
	}
	
	public static void main(String[] args) {
		
	}
}
