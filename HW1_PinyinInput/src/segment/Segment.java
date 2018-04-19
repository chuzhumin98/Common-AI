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

import com.mindflow.py4j.PinyinConverter;
import com.mindflow.py4j.exception.IllegalPinyinException;

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
				PinyinConverter converter = new PinyinConverter();
				Scanner input = new Scanner(new File(ExportModel.datasetPath+ExportModel.datasetName[i]), "utf-8");
				Analyzer analyzer = new IK_CAnalyzer();
				//Analyzer analyzer = new PaodingAnalyzer(); 
				int readLines = 0; //已经处理的行数
				while (input.hasNextLine()) {
					JSONObject record = JSONObject.fromObject(input.nextLine());
					//System.out.println(record);
					String html = (String)record.get("html");
					String title = (String)record.get("title");
					StringReader reader = new StringReader(title+" "+html);  
					//reader = new StringReader("清华大学计算机系");  
				    TokenStream ts = analyzer.tokenStream("", reader);  
				    Token t;  
				    try {
						while ((t = ts.next()) != null) {  
							String splitWords = t.term(); 
							//System.out.println(splitWords);
							if (splitWords.length() >= 2) {
								//System.out.println(splitWords);
								String pinyins0 = converter.getPinyin(splitWords);
								String[] pinyins = pinyins0.split(" ");
								for (int j = 0; j < pinyins.length-1; j++) {
									int leftPinyin = this.model.pinyinString.indexOf(pinyins[j]);
									int rightPinyin = this.model.pinyinString.indexOf(pinyins[j+1]);
									//System.out.println(pinyins[j]+" "+pinyins[j+1]);
									if (leftPinyin >= 0 && rightPinyin >= 0) {
										this.pinyinCount[leftPinyin][rightPinyin]++;
									}	
								}					
							}
						}
				    } catch (IOException e) {
						// TODO Auto-generated catch block
						e.printStackTrace();
					} catch (IllegalPinyinException e) {
						// TODO Auto-generated catch block
						//e.printStackTrace();
					}    
				    reader.close();  
					readLines++;
					if (readLines % 1000 == 0) {
						System.out.println("has read "+readLines +" lines in " + ExportModel.datasetName[i]);
					}
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
	
	/**
	 * 参数格式 xxx.jar (-拼音汉字表路径   -一二级汉字路径  -训练新闻文件夹路径  -输出结果路径)
	 * 后面的参数都为可选参数
	 * 
	 * @param args
	 */
	public static void main(String[] args) {
		System.out.println("this is Segment.java");
		String outPath = "output/pinyintabletotal_IKC3.txt";
		if (args.length >= 1) {
			ExportModel.wordPinyinListPath = args[0];
		}
		if (args.length >= 2) {
			ExportModel.wordListPath = args[1];
		}
		if (args.length >= 3) {
			ExportModel.datasetPath = args[2];
		}
		if (args.length >= 4) {
			outPath = args[3];
		}
		Segment seg = new Segment();
		seg.loadArticles();
		seg.exportPinyinTable(outPath);
	}
}
