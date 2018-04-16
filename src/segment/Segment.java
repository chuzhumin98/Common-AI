package segment;

import java.io.IOException;
import java.io.StringReader;

import org.apache.lucene.analysis.TokenStream;
import org.apache.lucene.analysis.tokenattributes.CharTermAttribute;

import com.chenlb.mmseg4j.analysis.MaxWordAnalyzer;


public class Segment {
	public static void main(String[] args) {
		MaxWordAnalyzer analyzer = new MaxWordAnalyzer();
		StringReader reader = new StringReader("中国即将在三年后举办北京冬奥会");  
	    TokenStream ts = analyzer.tokenStream("", reader);  
	    CharTermAttribute term = ts.getAttribute(CharTermAttribute.class);  
	    try {
			while (ts.incrementToken()) {  
				System.out.print(term.toString()+" ");  
			}
	    } catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}  
	    analyzer.close();  
	    reader.close();  
	}
}
