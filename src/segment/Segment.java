package segment;

import java.io.Closeable;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.PrintStream;
import java.io.StringReader;
import java.util.Scanner;

import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.analysis.Token;
import org.apache.lucene.analysis.TokenStream;
import org.mira.lucene.analysis.IK_CAnalyzer;

import com.chenlb.mmseg4j.analysis.MaxWordAnalyzer;

import model.ExportModel;
import net.paoding.analysis.analyzer.PaodingAnalyzer;
import net.sf.json.JSONArray;
import net.sf.json.JSONObject;


public class Segment {
	public ExportModel model; //导入拼音和汉字数据
	
	int[][] pinyinCount; //词汇的拼音配对信息
	
	public Segment() {
		this.model = ExportModel.getInstance(); 
		int pinyinSize = this.model.pinyinString.size();
		pinyinCount = new int [pinyinSize][pinyinSize];
	}
	
	/**
	 * 载入文章的数据，得到词项关联信息
	 */
	public void loadArticles() {
		for (int i = 0; i < ExportModel.datasetName.length; i++) {
			try {
				Scanner input = new Scanner(new File(ExportModel.datasetPath+ExportModel.datasetName[i]), "utf-8");
				//Analyzer analyzer = new IK_CAnalyzer();
				Analyzer analyzer = new PaodingAnalyzer(); 
				while (input.hasNextLine()) {
					JSONObject record = JSONObject.fromObject(input.nextLine());
					//System.out.println(record);
					String html = (String)record.get("html");
					String title = (String)record.get("title");
					StringReader reader = new StringReader(title+" "+html);  
				    TokenStream ts = analyzer.tokenStream("", reader);  
				    Token t;  
				    try {
						while ((t = ts.next()) != null) {  
							String splitWords = t.term(); 
							if (splitWords.length() >= 2) {
								//System.out.println(splitWords);
								for (int j = 0; j < splitWords.length()-1; ) {
									if (this.model.wordIndexList.containsKey(splitWords.charAt(j))) {
										if (this.model.wordIndexList.containsKey(splitWords.charAt(j+1))) {
											int left = this.model.wordIndexList.get(splitWords.charAt(j));
											int right = this.model.wordIndexList.get(splitWords.charAt(j+1));
											int leftPinyin = this.model.wordPinyinIndex[left];
											int rightPinyin = this.model.wordPinyinIndex[right];
											this.pinyinCount[leftPinyin][rightPinyin]++;
											j++;
										} else {
											j += 2;
										}
									} else {
										j++;
									}
								}					
							}
						}
				    } catch (IOException e) {
						// TODO Auto-generated catch block
						e.printStackTrace();
					}    
				    reader.close();  
					
				}
				System.out.println("end for read "+ExportModel.datasetName[i]);
			} catch (FileNotFoundException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		}
	}
	
	/**
	 * 输出拼音二元模型到文件中
	 * 
	 * @param path
	 */
	public void exportPinyinTable(String path) {
		try {
			PrintStream output = new PrintStream(path);
			output.println(this.pinyinCount.length);
			for (int i = 0; i < this.pinyinCount.length; i++) {
				String thisLine = this.pinyinCount[i][0]+"";
				for (int j = 1; j < this.pinyinCount[i].length; j++) {
					thisLine = thisLine + " " + this.pinyinCount[i][j];
				}
				output.println(thisLine);
			}
		} catch (FileNotFoundException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
	
	public static void main(String[] args) {
		Segment seg = new Segment();
		seg.loadArticles();
		seg.exportPinyinTable("output/pinyintabletotal_Paoding.txt");
	}
}
