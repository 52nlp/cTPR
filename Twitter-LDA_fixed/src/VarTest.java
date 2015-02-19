import java.sql.*;
import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import net.moraleboost.mecab.Lattice;
import net.moraleboost.mecab.Tagger;
import net.moraleboost.mecab.impl.StandardTagger;
import net.moraleboost.mecab.Node;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

class VarTest{
	public static void main(String args[]) throws Exception {
		String url = "jdbc:postgresql://localhost/image_tagging";
		String user = "postgres";
		String password = "";
		Connection con = DriverManager.getConnection(url, user, password);
		
		Statement stmt = con.createStatement();
		String sql = "select tweet_id, tweet from twipple limit 3";
		ResultSet rs = stmt.executeQuery(sql);
		
		Pattern p = Pattern.compile("名詞");

		while(rs.next()){
			long id = rs.getLong("tweet_id");
			String tweet = rs.getString("tweet");
			
			System.out.println(tweet);
			
			// Taggerを構築。
			// 引数には、MeCabのcreateTagger()関数に与える引数を与える。
			StandardTagger tagger = new StandardTagger("");

			// Lattice（形態素解析に必要な実行時情報が格納されるオブジェクト）を構築
			Lattice lattice = tagger.createLattice();

			lattice.setSentence(tweet);
			tagger.parse(lattice);
			Node node = lattice.bosNode();
			while(node != null){
				String surface = node.surface();
				String feature = node.feature();
				Matcher m = p.matcher(feature);
				
				if(m.find()){
					System.out.println(surface+" "+feature);
				}
				node = node.next();
			}
		}
	}
}