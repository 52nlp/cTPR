/*
 * Copyright (C) 2012 by
 * 
 * 	SMU Text Mining Group
 *	Singapore Management University
 *
 * TwitterLDA is distributed for research purpose, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
 * 
 * The original paper is as follows:
 * Wayne Xin Zhao, Jing Jiang et al., Comparing Twitter and traditional media using topic models. 
 * ECIR'11.
 * 
 * Note that the package here is not developed by the authors
 * in the paper, nor used in the original papers. It's an implementation
 * based on the paper, where most of the work is done by qiming.diao.2010@smu.sg.
 * 
 * Feel free to contact the following people if you find any
 * problems in the package.
 * 
 * minghui.qiu.2010@smu.edu.sg
 *
 */

package TwitterLDA;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.sql.*;
import java.util.concurrent.*;
import java.util.Collection;
import java.util.LinkedList;

import Common.Stopwords;
import Common.FileUtil;
import Common.JC;

public class TwitterLDAmain {

	static ArrayList<String> stopWords;

	public static void main(String args[]) throws Exception {
		String base = System.getProperty("user.dir") + "/data/";
		String name = "test";
		//char[] options = { 'f', 'i', 'o', 'p', 's' };
		String filelist = base + "/filelist_" + name + ".txt";
		String dataDir = base + "/Data4Model/" + name + "/";
		String outputDir = base + "/ModelRes/" + name + "/";
		String modelParas = base + "/modelParameters-" + name + ".txt";
		String stopfile = base + "/stoplist.txt";
		
		// create output folder
		FileUtil.mkdir(new File(base + "/ModelRes/"));
		FileUtil.mkdir(new File(outputDir));

		ArrayList<String> files = new ArrayList<String>();
		FileUtil.readLines(filelist, files);

		// 1. get model parameters
		int A_all = 500;
		float alpha_g = (float)0.5;
		float beta_word = (float)0.01;
		float beta_b = (float)0.01;
		float gamma = (float)20;
		int nIter = 500;
		//System.err.println("Topics:" + A_all + ", alpha_g:" + alpha_g
		//		+ ", beta_word:" + beta_word + ", beta_b:" + beta_b
		//		+ ", gamma:" + gamma + ", iteration:" + nIter);
		
		new Stopwords();
		Stopwords.addStopfile(stopfile);
		int outputTopicwordCnt = 30;
		int outputBackgroundwordCnt = 50;

		String outputWordsInTopics = outputDir + "WordsInTopics.txt";
		String outputBackgroundWordsDistribution = outputDir
				+ "BackgroundWordsDistribution.txt";
		String outputTextWithLabel = outputDir + "/TextWithLabel/";

		if (!new File(outputTextWithLabel).exists())
			FileUtil.mkdir(new File(outputTextWithLabel));
		
		System.out.println("getting model parameters is done");
		
		// 2. get documents (users)
		final HashMap<String, Integer> wordMap = new HashMap<String, Integer>();
		final ArrayList<user> users = new ArrayList<user>();
		final ArrayList<String> uniWordMap = new ArrayList<String>();
		
		String url = "jdbc:postgresql://localhost/image_tagging";
		String user = "postgres";
		String password = "";
		Connection con = DriverManager.getConnection(url, user, password);
		
		Statement stmt = con.createStatement();
		String sql = "delete from words_in_topics";
		stmt.executeUpdate(sql);

		sql = "delete from words_in_topics";
		stmt.executeUpdate(sql);

		sql = "delete from topic_distribution_on_users";
		stmt.executeUpdate(sql);

		sql = "delete from topic_counts_on_users";
		stmt.executeUpdate(sql);

		sql = "delete from text_with_label";
		stmt.executeUpdate(sql);

		sql = "delete from word_with_label_in_each_text";
		stmt.executeUpdate(sql);

		// TODO: delete the line below
		//int total = 1000;

		sql = "select user_id from (select user_id, count(*) as num from " +
				"(select distinct on (tweet_id) user_id from preprocess) as a " +
				"group by user_id) as b where num between 8 and 100";
		ResultSet rs = stmt.executeQuery(sql);

		// マルチスレッドで使用
		//ExecutorService threadPool = Executors.newFixedThreadPool(4);
		//int cores = Runtime.getRuntime().availableProcessors();
		//System.out.println(cores);

		int total = 0;
		ArrayList<String> userIDList = new ArrayList<String>();
		//Collection<Callable<Void>> processes = new LinkedList<Callable<Void>>();
		while(rs.next()){
			userIDList.add(Long.toString(rs.getLong("user_id")));
			total++;
		}
		
		int count = 1;
		for(int i = 0; i < userIDList.size(); i++){
			System.out.println(count+"/"+total);

			String user_id = userIDList.get(i);
			user tweetuser = new user(user_id, wordMap, uniWordMap);
			users.add(tweetuser);

			count++;
		}

		// マルチスレッドver
		//while(rs.next()){
		//	final String user_id = Long.toString(rs.getLong("user_id"));
		//	final int tmpPos = count;
		//	
		//	processes.add(new Callable<Void>() {
		//		@Override
		//		public Void call() throws Exception {
		//			final user tweetuser = new user(user_id, wordMap, uniWordMap, tmpPos, total);
		//			users.add(tweetuser);
		//			return null;
		//		}
		//	});
		//	count++;
		//}

		//try {
		//	threadPool.invokeAll(processes);
		//} catch (InterruptedException e) {
		//	throw new RuntimeException(e);
		//} finally {
		//	threadPool.shutdown();
		//}
		/* ---ここまで--- */

		// ComUtil.printHash(wordMap);
		if (uniWordMap.size() != wordMap.size()) {
			System.out.println(wordMap.size());
			System.out.println(uniWordMap.size());
			System.err
					.println("uniqword size is not the same as the hashmap size!");
			System.exit(0);
		}

		// output wordMap and itemMap
		FileUtil.writeLines(outputDir + "wordMap.txt", wordMap);
		FileUtil.writeLines(outputDir + "uniWordMap.txt", uniWordMap);
		int uniWordMapSize = uniWordMap.size();
		wordMap.clear();
		uniWordMap.clear();
		// uniItemMap.clear();

		System.out.println("getting documents is done");

		// 3. run the model
		Model model = new Model(A_all, users.size(), uniWordMapSize, nIter,
				alpha_g, beta_word, beta_b, gamma);
		model.intialize(users);
		// model.fake_intialize(users);
		model.estimate(users, nIter);

		System.out.println("runnin the model is done");

		// 4. output model results
		System.out.println("Record Topic Distributions/Counts");
		model.outputTopicDistributionOnUsers(outputDir, users);
		System.out.println("read uniwordmap");
		FileUtil.readLines(outputDir + "uniWordMap.txt", uniWordMap);

		try {
			model.outputTextWithLabel(outputTextWithLabel, users, uniWordMap);
		} catch (Exception e) {
			e.printStackTrace();
		}
		System.out.println("write text with labels done");
		// model.outputTopicCountOnTime(outputTopicsCountOnTime);
		users.clear();

		try {
			model.outputWordsInTopics(outputWordsInTopics, uniWordMap,
					outputTopicwordCnt);
		} catch (Exception e1) {
			e1.printStackTrace();
		}

		try {
			model.outputBackgroundWordsDistribution(
					outputBackgroundWordsDistribution, uniWordMap,
					outputBackgroundwordCnt);
		} catch (Exception e1) {
			e1.printStackTrace();
		}
		System.out.println("Record Background done");

		System.out.println("Final Done");

		rs.close();
		stmt.close();
		con.close();
	}

	private static void getModelPara(String modelParas,
			ArrayList<String> modelSettings) {
		modelSettings.clear();
		// T , alpha , beta , gamma , iteration , saveStep, saveTimes
		modelSettings.clear();
		// add default parameter settings
		modelSettings.add("40");
		modelSettings.add("1.25");
		modelSettings.add("0.01");
		modelSettings.add("0.01");
		modelSettings.add("20");
		modelSettings.add("20");

		ArrayList<String> inputlines = new ArrayList<String>();
		FileUtil.readLines(modelParas, inputlines);
		for (int i = 0; i < inputlines.size(); i++) {
			int index = inputlines.get(i).indexOf(":");
			String para = inputlines.get(i).substring(0, index).trim()
					.toLowerCase();
			String value = inputlines.get(i)
					.substring(index + 1, inputlines.get(i).length()).trim()
					.toLowerCase();
			switch (ModelParas.valueOf(para)) {
			case topics:
				modelSettings.set(0, value);
				break;
			case alpha_g:
				modelSettings.set(1, value);
				break;
			case beta_word:
				modelSettings.set(2, value);
				break;
			case beta_b:
				modelSettings.set(3, value);
				break;
			case gamma:
				modelSettings.set(4, value);
				break;
			case iteration:
				modelSettings.set(5, value);
				break;
			default:
				break;
			}
		}
	}

	public enum ModelParas {
		topics, alpha_g, beta_word, beta_b, gamma, iteration;
	}
}
