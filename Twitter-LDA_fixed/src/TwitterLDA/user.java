package TwitterLDA;
import java.io.*;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.sql.*;

import Common.FileUtil;

//import edu.mit.jwi.item.Word;

public class user {

	protected String userID;
	
	protected int tweetCnt;
	
	ArrayList<tweet> tweets = new ArrayList<tweet>();
	
	
	// Fixed
	public user(String id, HashMap<String, Integer> wordMap, 
			ArrayList<String> uniWordMap) throws Exception {
		
		this.userID = id;

		String url = "jdbc:postgresql://localhost/image_tagging";
		String user = "postgres";
		String password = "";
		Connection con = DriverManager.getConnection(url, user, password);
		
		Statement stmt = con.createStatement();
		long longID = Long.parseLong(id);
		String sql = String.format("select distinct tweet_id from preprocess where user_id=%d",longID);
		ResultSet rs = stmt.executeQuery(sql);
		
		int tweetCount = 0;
		
		while(rs.next()){
			long tweet_id = rs.getLong("tweet_id");
			tweet tw = new tweet(tweet_id, wordMap, uniWordMap);
			tweets.add(tw);
			tweetCount++;
		}

		this.tweetCnt = tweetCount;
		
		rs.close();
		stmt.close();
		con.close();

		//for(int lineNo = 0; lineNo < datalines.size(); lineNo++) {
		//	String line = datalines.get(lineNo);
		//	tweet tw = new tweet(line, wordMap, uniWordMap);
		//	tweets.add(tw);						
		//}

		//datalines.clear();
	}

	// Original
	//public user(String Dir, String id, HashMap<String, Integer> wordMap, 
	//		ArrayList<String> uniWordMap) {
	//	
	//	this.userID = id;
	//	ArrayList<String> datalines = new ArrayList<String>();
	//	FileUtil.readLines(Dir, datalines);		
	//	
	//	this.tweetCnt = datalines.size();
	//	
	//	for(int lineNo = 0; lineNo < datalines.size(); lineNo++) {
	//		String line = datalines.get(lineNo);
	//		tweet tw = new tweet(line, wordMap, uniWordMap);
	//		tweets.add(tw);						
	//	}
	//	
	//	datalines.clear();
	//}
}
