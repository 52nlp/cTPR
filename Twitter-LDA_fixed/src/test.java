import net.moraleboost.mecab.Lattice;
import net.moraleboost.mecab.Tagger;
import net.moraleboost.mecab.impl.StandardTagger;
import net.moraleboost.mecab.Node;

class test
{
	public static void main(String[] args) throws Exception
	{
		// Taggerを構築。
		// 引数には、MeCabのcreateTagger()関数に与える引数を与える。
		StandardTagger tagger = new StandardTagger("");

		// バージョン文字列を取得
		System.out.println("MeCab version " + tagger.version());

		// Lattice（形態素解析に必要な実行時情報が格納されるオブジェクト）を構築
		Lattice lattice = tagger.createLattice();

		// 解析対象文字列をセット
		String text = "明日は攻殻機動隊を放送する。";
		lattice.setSentence(text);

		// tagger.parse()を呼び出して、文字列を形態素解析する。
		tagger.parse(lattice);

		// 一つずつ形態素をたどりながら、表層形と素性を出力
		Node node = lattice.bosNode();
		while (node != null) {
			String surface = node.surface();
			String feature = node.feature();
			System.out.println(surface + "\t" + feature);
			node = node.next();
		}

		// lattice, taggerを破壊
		lattice.destroy();
		tagger.destroy();
	}
}