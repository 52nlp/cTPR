package TwitterLDA;

import java.io.*;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.regex.*;
import net.moraleboost.mecab.Lattice;
import net.moraleboost.mecab.Tagger;
import net.moraleboost.mecab.impl.StandardTagger;
import net.moraleboost.mecab.Node;
import java.sql.*;

//import Common.Stopwords;

import Common.ComUtil;
import Common.Stopwords;

//import edu.mit.jwi.item.Word;

public class tweet {

	protected int time;

	protected int[] tweetwords;
	
	protected long tweet_id;

	public tweet(long tweet_id, HashMap<String, Integer> wordMap,
			ArrayList<String> uniWordMap) throws Exception {
		
		this.tweet_id = tweet_id;

		int number = wordMap.size();

		ArrayList<Integer> words = new ArrayList<Integer>();
		ArrayList<String> tokens = new ArrayList<String>();
		
		String url = "jdbc:postgresql://localhost/image_tagging";
		String user = "postgres";
		String password = "";
		Connection con = DriverManager.getConnection(url, user, password);
		
		Statement stmt = con.createStatement();
		String sql = String.format("select distinct word from preprocess where tweet_id=%d",this.tweet_id);
		ResultSet rs = stmt.executeQuery(sql);
		
		while(rs.next()){
			String word = rs.getString("word");
			if(!wordMap.containsKey(word)){
				words.add(number);
				wordMap.put(word, number++);
				uniWordMap.add(word);
			} else {
				words.add(wordMap.get(word));
			}
		}
		
		rs.close();
		stmt.close();
		con.close();

		//for (int i = 0; i < tokens.size(); i++) {
		//	String tmpToken = tokens.get(i).toLowerCase();
		//	// if(!isNoisy(tokens.get(i))) {
		//	if (!Stopwords.isStopword(tmpToken) && !isNoisy(tmpToken)) {
		//		if (!wordMap.containsKey(tmpToken)) {
		//			words.add(number);
		//			wordMap.put(tmpToken, number++);
		//			uniWordMap.add(tmpToken);
		//		} else {
		//			words.add(wordMap.get(tmpToken));
		//		}
		//	}
		//	// else
		//	// System.out.println(tokens.get(i));
		//}

		tweetwords = new int[words.size()];

		for (int w = 0; w < words.size(); w++) {
			tweetwords[w] = words.get(w);
		}
		words.clear();
		tokens.clear();

	}

	//public tweet(String dataline, HashMap<String, Integer> wordMap,
	//		ArrayList<String> uniWordMap) {

	//	int number = wordMap.size();

	//	// String inline = dataline.substring(20);
	//	String inline = dataline; // no specific restriction of input data

	//	ArrayList<Integer> words = new ArrayList<Integer>();
	//	ArrayList<String> tokens = new ArrayList<String>();

	//	ComUtil.tokenize(inline, tokens);

	//	for (int i = 0; i < tokens.size(); i++) {
	//		String tmpToken = tokens.get(i).toLowerCase();
	//		// if(!isNoisy(tokens.get(i))) {
	//		if (!Stopwords.isStopword(tmpToken) && !isNoisy(tmpToken)) {
	//			if (!wordMap.containsKey(tmpToken)) {
	//				words.add(number);
	//				wordMap.put(tmpToken, number++);
	//				uniWordMap.add(tmpToken);
	//			} else {
	//				words.add(wordMap.get(tmpToken));
	//			}
	//		}
	//		// else
	//		// System.out.println(tokens.get(i));
	//	}

	//	tweetwords = new int[words.size()];

	//	for (int w = 0; w < words.size(); w++) {
	//		tweetwords[w] = words.get(w);
	//	}
	//	words.clear();
	//	tokens.clear();

	//}

	private boolean isNoisy(String token) {
		if (token.toLowerCase().contains("#pb#")
				|| token.toLowerCase().contains("http:"))
			return true;
		if (token.contains("@")) {
			return true;
		}
		return token.matches("[\\p{Punct}]+");
		// // at least contains a word
		// Pattern MY_PATTERN = Pattern.compile(".*[a-z]+.*");
		// Matcher m = MY_PATTERN.matcher(token.toLowerCase());
		// // filter @xxx
		// if (!m.matches() || token.contains("@")) {
		// return true;
		// }
		// else
		// return false;
	}

}
